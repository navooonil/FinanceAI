import datetime
import logging
from typing import Any, Dict, List, Tuple, Optional
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from tenacity import retry, stop_after_attempt, wait_exponential

from app.models.invoice import Invoice
from app.models.vendor import Vendor
from app.models.agent import AgentRun
from app.models.workflow import Workflow
from app.services.financial_intelligence import VendorRiskScorer

logger = logging.getLogger(__name__)


class ExpressionEvaluator:
    """
    Evaluates trigger and step condition expressions against entity properties.
    """
    @staticmethod
    def evaluate(field_val: Any, operator: str, expected_val: Any) -> bool:
        if field_val is None:
            return False
            
        op = operator.strip().lower()
        
        try:
            if op == "equals":
                return str(field_val).strip().lower() == str(expected_val).strip().lower()
            elif op == "not_equals":
                return str(field_val).strip().lower() != str(expected_val).strip().lower()
            elif op == "greater_than":
                return float(field_val) > float(expected_val)
            elif op == "less_than":
                return float(field_val) < float(expected_val)
            elif op == "contains":
                return str(expected_val).strip().lower() in str(field_val).strip().lower()
        except (ValueError, TypeError):
            logger.error(f"Failed to compare field value '{field_val}' with expected '{expected_val}' using operator '{op}'")
            return False
            
        return False


class NotificationClientMock:
    """
    Simulated SaaS notification dispatcher with retry capabilities.
    """
    @staticmethod
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def send_slack_message(webhook_url: str, text: str) -> None:
        """
        Sends simulated Slack message. Implements retry logic using tenacity.
        """
        logger.info(f"Simulating Slack webhook dispatch to '{webhook_url}': '{text}'")
        # In production, this would make a httpx.post call.

    @staticmethod
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def send_email(to_address: str, subject: str, body: str) -> None:
        """
        Sends simulated Email message.
        """
        logger.info(f"Simulating Email dispatch to '{to_address}' [Subject: {subject}]: '{body}'")


async def resolve_field_value(field_path: str, invoice: Invoice, session: AsyncSession) -> Any:
    """
    Resolves data attributes on context objects (Invoices, Vendors).
    """
    parts = field_path.split(".")
    if len(parts) != 2:
        return None
        
    entity, attribute = parts[0].strip().lower(), parts[1].strip()
    
    if entity == "invoice":
        if hasattr(invoice, attribute):
            return getattr(invoice, attribute)
    elif entity == "vendor":
        if not invoice.vendor_id:
            return None
        if attribute == "risk_score":
            risk_info = await VendorRiskScorer.compute_vendor_risk(session, invoice.vendor_id, invoice.company_id)
            return risk_info["risk_score"]
        # Retrieve direct vendor properties
        vendor_res = await session.execute(select(Vendor).where(Vendor.id == invoice.vendor_id))
        vendor = vendor_res.scalar_one_or_none()
        if vendor and hasattr(vendor, attribute):
            return getattr(vendor, attribute)
            
    return None


class WorkflowExecutionEngine:
    """
    Automated State Machine graph parser executing user-defined triggers, condition nodes, and actions.
    """
    @staticmethod
    async def execute_workflow(
        session: AsyncSession,
        agent_run: AgentRun,
        invoice: Invoice,
        start_step_id: Optional[str] = None
    ) -> None:
        """
        Runs the workflow execution loop from a starting step identifier or trigger node.
        """
        # Fetch workflow model
        workflow_res = await session.execute(select(Workflow).where(Workflow.id == agent_run.workflow_id))
        workflow = workflow_res.scalar_one_or_none()
        if not workflow or not workflow.is_active:
            logger.error(f"Active workflow definition not found for run ID: {agent_run.id}")
            agent_run.status = "failed"
            agent_run.error_message = "Active workflow definition not found."
            await session.commit()
            return

        definition = workflow.definition
        steps_list = definition.get("steps", [])
        steps_by_id = {step["id"]: step for step in steps_list}

        current_results = agent_run.output_results or {}
        audit_trail = current_results.get("audit_trail", [])

        # Establish start step
        current_step_id = start_step_id or (steps_list[0]["id"] if steps_list else None)

        agent_run.status = "running"
        await session.flush()

        while current_step_id:
            step = steps_by_id.get(current_step_id)
            if not step:
                # Target step not configured, complete execution
                audit_trail.append({
                    "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                    "step_id": current_step_id,
                    "status": "step_not_found",
                    "detail": "Target execution step reference was not found in the workflow definition."
                })
                break

            step_type = step["type"].strip().lower()
            
            # --- 1. Evaluate Condition Nodes ---
            if step_type == "condition":
                config = step["config"]
                field_path = config["field"]
                operator = config["operator"]
                expected_val = config["value"]

                # Resolve the dynamic attribute value
                resolved_val = await resolve_field_value(field_path, invoice, session)
                passed = ExpressionEvaluator.evaluate(resolved_val, operator, expected_val)

                audit_trail.append({
                    "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                    "step_id": step["id"],
                    "status": "evaluated_true" if passed else "evaluated_false",
                    "detail": f"Condition evaluated {passed} for {field_path} ({resolved_val}) {operator} {expected_val}"
                })

                current_step_id = config["then_step_id"] if passed else config["else_step_id"]

            # --- 2. Execute Action Nodes ---
            elif step_type == "action":
                action_type = step["action_type"].strip().lower()
                config = step["config"]

                # Action A: Send Notification Channel Alerts
                if action_type == "send_notification":
                    channel = config["channel"].strip().lower()
                    template = config["template"]
                    
                    # Render template simple tags
                    message = template.replace("{invoice.invoice_number}", str(invoice.invoice_number or ""))
                    message = message.replace("{invoice.total_amount}", str(invoice.total_amount or 0.0))
                    
                    try:
                        if channel == "slack":
                            NotificationClientMock.send_slack_message("https://hooks.slack.com/services/mock", message)
                        elif channel == "email":
                            NotificationClientMock.send_email("finance-alerts@saas.com", "Workflow Operations Alert", message)
                        
                        audit_trail.append({
                            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                            "step_id": step["id"],
                            "status": "notification_sent",
                            "detail": f"Simulated message dispatched to {channel}"
                        })
                    except Exception as e:
                        logger.error(f"Failed to dispatch notification at step {step['id']}: {str(e)}")
                        audit_trail.append({
                            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                            "step_id": step["id"],
                            "status": "notification_failed",
                            "detail": f"Dispatched channel threw exceptions: {str(e)}"
                        })

                    current_step_id = config.get("next_step_id")

                # Action B: Update Ingestion Status
                elif action_type == "update_status":
                    target_status = config["status"]
                    invoice.status = target_status

                    audit_trail.append({
                        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                        "step_id": step["id"],
                        "status": "status_updated",
                        "detail": f"Invoice status successfully flipped to '{target_status}'"
                    })

                    current_step_id = config.get("next_step_id")

                # Action C: Halting Approval Chains (Asynchronous Pause)
                elif action_type == "request_approval":
                    approver_role = config["approver_role"]
                    
                    # Pause state transition
                    agent_run.status = "waiting_for_approval"
                    
                    audit_trail.append({
                        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                        "step_id": step["id"],
                        "status": "waiting_for_approval",
                        "detail": f"Execution halted. Paused waiting manual approval from: {approver_role}"
                    })

                    # Persist tracking parameters inside output_results JSONB
                    current_results["current_step_id"] = step["id"]
                    current_results["pending_approval"] = {
                        "approver_role": approver_role,
                        "next_step_id": config.get("next_step_id")
                    }
                    current_results["audit_trail"] = audit_trail
                    agent_run.output_results = current_results
                    
                    await session.commit()
                    return

            else:
                # Unknown step type
                audit_trail.append({
                    "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                    "step_id": step["id"],
                    "status": "failed",
                    "detail": f"Unsupported step type '{step_type}' encountered."
                })
                break

        # Workflow execution completed
        agent_run.status = "completed"
        current_results["audit_trail"] = audit_trail
        agent_run.output_results = current_results
        await session.commit()
        logger.info(f"Workflow execution {agent_run.id} finished successfully.")

    @staticmethod
    async def resume_workflow_approval(
        session: AsyncSession,
        agent_run: AgentRun,
        invoice: Invoice,
        decision: str,
        approver_id: Optional[str] = None,
        comments: Optional[str] = None
    ) -> None:
        """
        Resumes a paused workflow execution from the request_approval step.
        """
        if agent_run.status != "waiting_for_approval":
            logger.warning(f"Resumption aborted: AgentRun {agent_run.id} is not waiting for approval.")
            return

        current_results = agent_run.output_results or {}
        pending = current_results.get("pending_approval", {})
        current_step_id = current_results.get("current_step_id")
        audit_trail = current_results.get("audit_trail", [])

        audit_trail.append({
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "step_id": current_step_id or "approval_node",
            "status": f"approval_{decision}",
            "detail": f"Approval decision '{decision}' submitted by {approver_id or 'anonymous'}. Comments: {comments or 'none'}"
        })

        if decision == "approved":
            next_step_id = pending.get("next_step_id")
            
            # Clean up pending approval schema
            current_results["pending_approval"] = None
            current_results["current_step_id"] = None
            current_results["audit_trail"] = audit_trail
            agent_run.output_results = current_results
            
            # Resume processing loop
            await WorkflowExecutionEngine.execute_workflow(session, agent_run, invoice, next_step_id)
        else:
            # Rejection terminates execution and marks invoice as rejected
            invoice.status = "rejected"
            agent_run.status = "failed"
            agent_run.error_message = f"Workflow rejected during manual approval. Comments: {comments or 'none'}"
            
            current_results["pending_approval"] = None
            current_results["current_step_id"] = None
            current_results["audit_trail"] = audit_trail
            agent_run.output_results = current_results
            
            await session.commit()
            logger.info(f"Workflow execution {agent_run.id} terminated due to rejection.")
