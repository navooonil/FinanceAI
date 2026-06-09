import logging
import uuid
import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.database import get_db
from app.models.invoice import Invoice
from app.models.agent import AgentRun
from app.models.workflow import Workflow
from app.models.vendor import Vendor
from app.schemas.workflow_schemas import (
    WorkflowCreateSchema,
    WorkflowResponseSchema,
    WorkflowTriggerRequestSchema,
    ApprovalRequestSchema,
    WorkflowExecutionStateResponseSchema,
    AuditStepSchema
)
from app.services.workflow_engine import WorkflowExecutionEngine, resolve_field_value, ExpressionEvaluator

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("", response_model=WorkflowResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_workflow_definition(
    request: WorkflowCreateSchema,
    company_id: str = Query(..., description="Tenant UUID context."),
    db: AsyncSession = Depends(get_db)
):
    """
    Saves a new workflow rule template definition inside PostgreSQL.
    """
    try:
        company_uuid = uuid.UUID(company_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid UUID format for company_id."
        )

    workflow = Workflow(
        company_id=company_uuid,
        name=request.name,
        description=request.description,
        trigger_type=request.trigger_type,
        definition=request.definition,
        is_active=request.is_active
    )
    db.add(workflow)
    await db.commit()
    
    return {
        "id": str(workflow.id),
        "company_id": str(workflow.company_id),
        "name": workflow.name,
        "description": workflow.description,
        "trigger_type": workflow.trigger_type,
        "definition": workflow.definition,
        "is_active": workflow.is_active
    }


@router.get("/{company_id}", response_model=List[WorkflowResponseSchema], status_code=status.HTTP_200_OK)
async def get_active_workflows(
    company_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Lists all workflows registered under a company.
    """
    try:
        company_uuid = uuid.UUID(company_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid UUID format for company_id."
        )

    stmt = select(Workflow).where(Workflow.company_id == company_uuid)
    res = await db.execute(stmt)
    workflows = [row[0] for row in res.all()]
    
    return [
        {
            "id": str(w.id),
            "company_id": str(w.company_id),
            "name": w.name,
            "description": w.description,
            "trigger_type": w.trigger_type,
            "definition": w.definition,
            "is_active": w.is_active
        }
        for w in workflows
    ]


@router.post("/trigger", status_code=status.HTTP_200_OK)
async def trigger_event_workflows(
    request: WorkflowTriggerRequestSchema,
    db: AsyncSession = Depends(get_db)
):
    """
    Fires an event to invoke active workflows. Evaluates trigger criteria
    and spins up asynchronous execution threads.
    """
    try:
        company_uuid = uuid.UUID(request.company_id)
        entity_uuid = uuid.UUID(request.entity_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid UUID format for company_id or entity_id."
        )

    # 1. Fetch the target invoice
    inv_res = await db.execute(select(Invoice).where(Invoice.id == entity_uuid))
    invoice = inv_res.scalar_one_or_none()
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice record not found."
        )

    # 2. Fetch active workflows matching trigger key
    stmt = (
        select(Workflow)
        .where(
            Workflow.company_id == company_uuid,
            Workflow.trigger_type == request.event_type,
            Workflow.is_active == True
        )
    )
    res = await db.execute(stmt)
    workflows = [row[0] for row in res.all()]

    runs_initiated = []

    for wf in workflows:
        # Check trigger criteria
        trigger = wf.definition.get("trigger", {})
        conditions = trigger.get("conditions", [])
        trigger_passed = True

        for cond in conditions:
            f_path = cond["field"]
            op = cond["operator"]
            val = cond["value"]

            resolved = await resolve_field_value(f_path, invoice, db)
            if not ExpressionEvaluator.evaluate(resolved, op, val):
                trigger_passed = False
                break

        if trigger_passed:
            # Instantiate execution thread
            agent_run = AgentRun(
                company_id=company_uuid,
                workflow_id=wf.id,
                agent_name=f"Workflow-{wf.name}",
                status="pending",
                input_parameters={"invoice_id": str(invoice.id)},
                output_results={"audit_trail": []}
            )
            db.add(agent_run)
            await db.flush()
            
            # Execute workflow
            await WorkflowExecutionEngine.execute_workflow(db, agent_run, invoice)
            runs_initiated.append(str(agent_run.id))

    return {
        "status": "success",
        "message": f"Evaluated event triggers. Runs initiated: {len(runs_initiated)}",
        "runs": runs_initiated
    }


@router.post("/approval/{agent_run_id}", response_model=WorkflowExecutionStateResponseSchema, status_code=status.HTTP_200_OK)
async def submit_approval_decision(
    agent_run_id: str,
    request: ApprovalRequestSchema,
    db: AsyncSession = Depends(get_db)
):
    """
    Submits a manual decision outcome (approve/reject) to resume a paused execution instance.
    """
    try:
        run_uuid = uuid.UUID(agent_run_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid UUID format for agent_run_id."
        )

    # Fetch agent run state
    stmt = select(AgentRun).where(AgentRun.id == run_uuid)
    res = await db.execute(stmt)
    agent_run = res.scalar_one_or_none()
    
    if not agent_run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AgentRun execution record not found."
        )

    if agent_run.status != "waiting_for_approval":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"AgentRun execution state is '{agent_run.status}' (not waiting for manual approval)."
        )

    invoice_id = agent_run.input_parameters.get("invoice_id")
    if not invoice_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AgentRun contains no target invoice reference."
        )

    inv_uuid = uuid.UUID(invoice_id)
    inv_res = await db.execute(select(Invoice).where(Invoice.id == inv_uuid))
    invoice = inv_res.scalar_one_or_none()
    
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Underlying invoice record not found."
        )

    # Resume the automation pipeline loop
    await WorkflowExecutionEngine.resume_workflow_approval(
        db,
        agent_run,
        invoice,
        request.decision,
        request.approver_id,
        request.comments
    )

    outputs = agent_run.output_results or {}
    raw_audit = outputs.get("audit_trail", [])
    
    audit_trail = [
        AuditStepSchema(
            timestamp=x.get("timestamp"),
            step_id=x.get("step_id"),
            status=x.get("status"),
            detail=x.get("detail")
        )
        for x in raw_audit
    ]

    return {
        "agent_run_id": str(agent_run.id),
        "workflow_id": str(agent_run.workflow_id) if agent_run.workflow_id else None,
        "status": agent_run.status,
        "current_step_id": outputs.get("current_step_id"),
        "audit_trail": audit_trail
    }


@router.get("/approvals/{company_id}", response_model=List[dict], status_code=status.HTTP_200_OK)
async def list_approval_runs(
    company_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Lists all workflow execution runs (approvals) for a company.
    """
    try:
        company_uuid = uuid.UUID(company_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid UUID format for company_id."
        )

    stmt = (
        select(AgentRun)
        .options(joinedload(AgentRun.workflow))
        .where(AgentRun.company_id == company_uuid)
        .order_by(AgentRun.created_at.desc())
    )
    res = await db.execute(stmt)
    runs = res.scalars().all()

    out = []
    for r in runs:
        # Get invoice details
        invoice_id_str = r.input_parameters.get("invoice_id")
        invoice_number = "—"
        vendor_name = "—"
        amount = 0.0
        if invoice_id_str:
            try:
                inv_uuid = uuid.UUID(invoice_id_str)
                inv_stmt = select(Invoice).options(joinedload(Invoice.vendor)).where(Invoice.id == inv_uuid)
                inv_res = await db.execute(inv_stmt)
                inv = inv_res.scalar_one_or_none()
                if inv:
                    invoice_number = inv.invoice_number or "Extracting..."
                    vendor_name = inv.vendor.name if inv.vendor else "Processing..."
                    amount = float(inv.total_amount) if inv.total_amount is not None else 0.0
            except Exception as e:
                logger.error(f"Error fetching invoice for agent run {r.id}: {e}")

        out.append({
            "id": str(r.id),
            "workflow_id": str(r.workflow_id) if r.workflow_id else None,
            "workflow_name": r.workflow.name if r.workflow else r.agent_name,
            "invoice_id": invoice_id_str,
            "invoice_number": invoice_number,
            "vendor_name": vendor_name,
            "amount": amount,
            "status": r.status,
            "current_step_id": r.output_results.get("current_step_id", "vp-approval-step") if r.output_results else "vp-approval-step",
            "created_at": r.created_at.isoformat() if r.created_at else datetime.datetime.now().isoformat(),
        })
    return out
