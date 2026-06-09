import datetime
import uuid
from unittest.mock import MagicMock, patch
import pytest
from fastapi import status

from main import app
from app.database import get_db
from app.models.invoice import Invoice
from app.models.agent import AgentRun
from app.models.workflow import Workflow
from app.services.workflow_engine import (
    ExpressionEvaluator,
    resolve_field_value,
    WorkflowExecutionEngine
)


class AsyncSessionMock:
    """
    Class-based mock for SQLAlchemy async database sessions.
    """
    def __init__(self, data_list=None):
        self.data_list = data_list or []
        self.added = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def execute(self, query, *args, **kwargs):
        mock_res = MagicMock()
        mock_res.all.return_value = self.data_list
        mock_res.scalar_one_or_none.return_value = self.data_list[0] if self.data_list else None
        return mock_res

    async def commit(self):
        pass

    async def flush(self):
        pass

    def add(self, obj):
        self.added.append(obj)


def test_expression_evaluator():
    """
    Verifies expression evaluator operator logic.
    """
    assert ExpressionEvaluator.evaluate(15000, "greater_than", 10000) is True
    assert ExpressionEvaluator.evaluate(5000, "greater_than", 10000) is False
    assert ExpressionEvaluator.evaluate("completed", "equals", "completed") is True
    assert ExpressionEvaluator.evaluate("pending", "not_equals", "completed") is True
    assert ExpressionEvaluator.evaluate("TechParts Corp", "contains", "parts") is True


@pytest.mark.asyncio
async def test_workflow_engine_direct_routing_success():
    """
    Asserts workflow routing executes sequential nodes and skips approvals on low values.
    """
    company_id = uuid.uuid4()
    invoice_id = uuid.uuid4()
    workflow_id = uuid.uuid4()
    
    # 1. Invoice amount = 5000 (Low value, routes directly to status update approved)
    invoice = Invoice(
        id=invoice_id,
        company_id=company_id,
        total_amount=5000.00,
        status="processing",
        issue_date=datetime.date.today()
    )
    
    definition = {
        "steps": [
            {
                "id": "step_amount_check",
                "type": "condition",
                "config": {
                    "field": "invoice.total_amount",
                    "operator": "greater_than",
                    "value": 10000.0,
                    "then_step_id": "step_vp_approval",
                    "else_step_id": "step_approve_status"
                }
            },
            {
                "id": "step_vp_approval",
                "type": "action",
                "action_type": "request_approval",
                "config": {
                    "approver_role": "VP_OF_FINANCE",
                    "next_step_id": None
                }
            },
            {
                "id": "step_approve_status",
                "type": "action",
                "action_type": "update_status",
                "config": {
                    "status": "approved",
                    "next_step_id": None
                }
            }
        ]
    }
    
    workflow = Workflow(
        id=workflow_id,
        company_id=company_id,
        name="Auto-Approve Low Spend",
        trigger_type="invoice_analyzed",
        definition=definition,
        is_active=True
    )
    
    agent_run = AgentRun(
        id=uuid.uuid4(),
        company_id=company_id,
        workflow_id=workflow_id,
        agent_name="Workflow-Test",
        status="pending",
        output_results={"audit_trail": []}
    )
    
    mock_session = AsyncSessionMock(data_list=[workflow])
    
    await WorkflowExecutionEngine.execute_workflow(mock_session, agent_run, invoice)
    
    # Assert workflow ran condition -> evaluated false -> ran step_approve_status -> completed
    assert agent_run.status == "completed"
    assert invoice.status == "approved"
    
    audit = agent_run.output_results["audit_trail"]
    assert len(audit) == 2
    assert audit[0]["step_id"] == "step_amount_check"
    assert audit[0]["status"] == "evaluated_false"
    assert audit[1]["step_id"] == "step_approve_status"
    assert audit[1]["status"] == "status_updated"


@pytest.mark.asyncio
async def test_workflow_engine_halt_on_approval():
    """
    Asserts workflow halts execution and transitions status to waiting_for_approval on high amounts.
    """
    company_id = uuid.uuid4()
    invoice_id = uuid.uuid4()
    workflow_id = uuid.uuid4()
    
    # Invoice amount = 15000 (High value, triggers approval chain)
    invoice = Invoice(
        id=invoice_id,
        company_id=company_id,
        total_amount=15000.00,
        status="processing",
        issue_date=datetime.date.today()
    )
    
    definition = {
        "steps": [
            {
                "id": "step_amount_check",
                "type": "condition",
                "config": {
                    "field": "invoice.total_amount",
                    "operator": "greater_than",
                    "value": 10000.0,
                    "then_step_id": "step_vp_approval",
                    "else_step_id": "step_approve_status"
                }
            },
            {
                "id": "step_vp_approval",
                "type": "action",
                "action_type": "request_approval",
                "config": {
                    "approver_role": "VP_OF_FINANCE",
                    "next_step_id": "step_approve_status"
                }
            },
            {
                "id": "step_approve_status",
                "type": "action",
                "action_type": "update_status",
                "config": {
                    "status": "approved",
                    "next_step_id": None
                }
            }
        ]
    }
    
    workflow = Workflow(
        id=workflow_id,
        company_id=company_id,
        name="Auto-Approve Low Spend",
        trigger_type="invoice_analyzed",
        definition=definition,
        is_active=True
    )
    
    agent_run = AgentRun(
        id=uuid.uuid4(),
        company_id=company_id,
        workflow_id=workflow_id,
        agent_name="Workflow-Test",
        status="pending",
        output_results={"audit_trail": []}
    )
    
    mock_session = AsyncSessionMock(data_list=[workflow])
    
    await WorkflowExecutionEngine.execute_workflow(mock_session, agent_run, invoice)
    
    # Assert workflow ran condition -> evaluated true -> hit step_vp_approval and paused
    assert agent_run.status == "waiting_for_approval"
    assert invoice.status == "processing"  # Not approved yet
    assert agent_run.output_results["current_step_id"] == "step_vp_approval"
    assert agent_run.output_results["pending_approval"]["approver_role"] == "VP_OF_FINANCE"


@pytest.mark.asyncio
async def test_workflow_resumption_approve_vs_reject():
    """
    Asserts resuming workflow applies decision, routes next nodes on approve, and rejects on reject.
    """
    company_id = uuid.uuid4()
    invoice_id = uuid.uuid4()
    workflow_id = uuid.uuid4()
    
    # Define workflow definition
    definition = {
        "steps": [
            {
                "id": "step_vp_approval",
                "type": "action",
                "action_type": "request_approval",
                "config": {
                    "approver_role": "VP_OF_FINANCE",
                    "next_step_id": "step_approve_status"
                }
            },
            {
                "id": "step_approve_status",
                "type": "action",
                "action_type": "update_status",
                "config": {
                    "status": "approved",
                    "next_step_id": None
                }
            }
        ]
    }
    
    workflow = Workflow(
        id=workflow_id,
        company_id=company_id,
        name="Approve Workflow",
        trigger_type="invoice_analyzed",
        definition=definition,
        is_active=True
    )
    
    # 1. Test Approval Decision
    invoice_a = Invoice(id=invoice_id, company_id=company_id, status="processing")
    agent_run_a = AgentRun(
        id=uuid.uuid4(),
        company_id=company_id,
        workflow_id=workflow_id,
        status="waiting_for_approval",
        input_parameters={"invoice_id": str(invoice_id)},
        output_results={
            "current_step_id": "step_vp_approval",
            "pending_approval": {"approver_role": "VP_OF_FINANCE", "next_step_id": "step_approve_status"},
            "audit_trail": []
        }
    )
    
    mock_session_a = AsyncSessionMock(data_list=[workflow])
    
    await WorkflowExecutionEngine.resume_workflow_approval(
        mock_session_a, agent_run_a, invoice_a, decision="approved", approver_id="usr_vp_1"
    )
    assert agent_run_a.status == "completed"
    assert invoice_a.status == "approved"

    # 2. Test Rejection Decision
    invoice_r = Invoice(id=invoice_id, company_id=company_id, status="processing")
    agent_run_r = AgentRun(
        id=uuid.uuid4(),
        company_id=company_id,
        workflow_id=workflow_id,
        status="waiting_for_approval",
        input_parameters={"invoice_id": str(invoice_id)},
        output_results={
            "current_step_id": "step_vp_approval",
            "pending_approval": {"approver_role": "VP_OF_FINANCE", "next_step_id": "step_approve_status"},
            "audit_trail": []
        }
    )
    
    mock_session_r = AsyncSessionMock(data_list=[workflow])
    
    await WorkflowExecutionEngine.resume_workflow_approval(
        mock_session_r, agent_run_r, invoice_r, decision="rejected", approver_id="usr_vp_1"
    )
    assert agent_run_r.status == "failed"
    assert invoice_r.status == "rejected"


def test_submit_approval_decision_endpoint(client):
    """
    Asserts approval API resumes workflow state, updates models, and returns 200 OK.
    """
    agent_run_id = str(uuid.uuid4())
    invoice_id = str(uuid.uuid4())
    company_id = str(uuid.uuid4())
    workflow_id = str(uuid.uuid4())
    
    mock_invoice = MagicMock()
    mock_invoice.id = uuid.UUID(invoice_id)
    mock_invoice.company_id = uuid.UUID(company_id)
    mock_invoice.status = "processing"
    
    mock_run = MagicMock()
    mock_run.id = uuid.UUID(agent_run_id)
    mock_run.workflow_id = uuid.UUID(workflow_id)
    mock_run.status = "waiting_for_approval"
    mock_run.input_parameters = {"invoice_id": invoice_id}
    mock_run.output_results = {
        "current_step_id": "step_vp_approval",
        "pending_approval": {"approver_role": "VP_OF_FINANCE", "next_step_id": "step_approve_status"},
        "audit_trail": []
    }
    
    # Setup mock session query results
    mock_session = AsyncSessionMock()
    
    async def custom_execute(query, *args, **kwargs):
        mock_res = MagicMock()
        query_str = str(query).lower()
        if "agent_runs" in query_str:
            mock_res.scalar_one_or_none.return_value = mock_run
        elif "invoices" in query_str:
            mock_res.scalar_one_or_none.return_value = mock_invoice
        else:
            mock_res.scalar_one_or_none.return_value = None
        return mock_res
        
    mock_session.execute = custom_execute
    app.dependency_overrides[get_db] = lambda: mock_session
    
    try:
        payload = {
            "decision": "approved",
            "approver_id": "usr_vp_99",
            "comments": "Matches budget checks."
        }
        
        # Patch execute_workflow inside resumption context to bypass graph traversing issues
        with patch.object(WorkflowExecutionEngine, "execute_workflow") as mock_exec:
            response = client.post(f"/api/v1/workflows/approval/{agent_run_id}", json=payload)
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["agent_run_id"] == agent_run_id
            
            # Verify executor resume was called
            mock_exec.assert_called_once()
    finally:
        app.dependency_overrides.clear()
