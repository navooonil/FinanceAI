import datetime
import uuid
from unittest.mock import MagicMock, patch
import pytest
from fastapi import status

from main import app
from app.database import get_db
from app.models.agent import AgentRun
from app.models.invoice import Invoice
from app.services.agents import compiled_graph, FinanceOpsState, step_router, planner_node


class AsyncSessionMock:
    """
    Class-based mock for SQLAlchemy async database sessions.
    Simulates queries to AgentRun and Invoice tables and handles flushing IDs.
    """
    def __init__(self, agent_run=None, invoice=None):
        self.agent_run = agent_run
        self.invoice = invoice
        self.added = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def execute(self, query, *args, **kwargs):
        mock_res = MagicMock()
        query_str = str(query).lower()
        if "agent_runs" in query_str:
            mock_res.scalar_one_or_none.return_value = self.agent_run
        elif "invoices" in query_str:
            mock_res.scalar_one_or_none.return_value = self.invoice
        else:
            mock_res.scalar_one_or_none.return_value = None
        return mock_res

    async def commit(self):
        pass

    async def flush(self):
        # Auto-populate UUID IDs for models on flush just like real Postgres/SQLAlchemy
        for obj in self.added:
            if hasattr(obj, "id") and obj.id is None:
                obj.id = uuid.uuid4()

    def add(self, obj):
        self.added.append(obj)


def test_planner_node_behavior():
    """
    Asserts the planner agent establishes the correct planned steps sequence.
    """
    mock_run = MagicMock()
    mock_run.output_results = {}
    mock_session = AsyncSessionMock(agent_run=mock_run)

    with patch("app.services.agents.AsyncSessionLocal", return_value=mock_session):
        state = {
            "invoice_id": str(uuid.uuid4()),
            "company_id": str(uuid.uuid4()),
            "plan": [],
            "current_step_index": 0,
            "ocr_raw_text": "",
            "extracted_data": {},
            "validation_results": {},
            "research_context": "",
            "financial_analysis": {},
            "risk_assessment": {},
            "generated_report": "",
            "errors": [],
            "agent_run_id": str(uuid.uuid4())
        }
        outputs = planner_node(state)
        
        assert outputs["plan"] == ["ocr", "validation", "research", "finance_analysis", "risk_assessment", "report_generation"]
        assert outputs["current_step_index"] == 0
        assert "processing_time_ms" in outputs


def test_step_router_logic():
    """
    Asserts the graph's execution router routes to scheduled plan indices,
    increments the step tracking pointer, and handles early abort conditions.
    """
    # 1. Normal routing sequence
    state = {
        "errors": [],
        "plan": ["ocr", "validation"],
        "current_step_index": 0
    }
    
    from langgraph.graph import END
    
    # First edge evaluation
    next_node = step_router(state)
    assert next_node == "ocr"
    state["current_step_index"] = 1
    
    # Second edge evaluation
    next_node = step_router(state)
    assert next_node == "validation"
    state["current_step_index"] = 2
    
    # End edge evaluation
    state["current_step_index"] = 2  # simulate end index boundary check
    next_node = step_router(state)
    assert next_node == END

    # 2. Early abort route
    state_err = {
        "errors": ["Critical checksum error"],
        "plan": ["ocr", "validation"],
        "current_step_index": 0
    }
    next_node = step_router(state_err)
    assert next_node == END


def test_compiled_graph_full_run():
    """
    Asserts that compiling and invoking the graph runs all step nodes sequentially
    and produces a complete audit report.
    """
    agent_run_id = str(uuid.uuid4())
    mock_run = MagicMock()
    mock_run.output_results = {}
    mock_session = AsyncSessionMock(agent_run=mock_run)

    with patch("app.services.agents.AsyncSessionLocal", return_value=mock_session):
        initial_state = {
            "invoice_id": str(uuid.uuid4()),
            "company_id": str(uuid.uuid4()),
            "plan": [],
            "current_step_index": 0,
            "ocr_raw_text": "",
            "extracted_data": {},
            "validation_results": {},
            "research_context": "",
            "financial_analysis": {},
            "risk_assessment": {},
            "generated_report": "",
            "errors": [],
            "agent_run_id": agent_run_id
        }
        
        final_state = compiled_graph.invoke(initial_state)
        
        # Verify execution index completed all 6 steps
        assert final_state["current_step_index"] == 6
        assert len(final_state["errors"]) == 0
        assert "FINANCIAL AUDIT REPORT" in final_state["generated_report"]
        assert final_state["extracted_data"]["vendor_name"] == "TechParts Corp"
        
        # Assert telemetry logged traces for each step inside mock_run.output_results
        assert "planner" in mock_run.output_results
        assert "ocr" in mock_run.output_results
        assert "validation" in mock_run.output_results
        assert "research" in mock_run.output_results
        assert "finance_analysis" in mock_run.output_results
        assert "risk_assessment" in mock_run.output_results
        assert "report_generation" in mock_run.output_results


def test_process_endpoint_success(client):
    """
    Asserts the /process API endpoint executes the LangGraph workflow, updates DB models,
    and returns status HTTP 200.
    """
    company_id = str(uuid.uuid4())
    invoice_id = str(uuid.uuid4())
    
    mock_invoice = MagicMock()
    mock_invoice.id = uuid.UUID(invoice_id)
    mock_invoice.company_id = uuid.UUID(company_id)
    mock_invoice.status = "processing"
    
    mock_run = MagicMock()
    mock_run.id = uuid.uuid4()
    mock_run.output_results = {}
    mock_run.status = "running"
    
    mock_session = AsyncSessionMock(agent_run=mock_run, invoice=mock_invoice)
    app.dependency_overrides[get_db] = lambda: mock_session
    
    try:
        payload = {
            "company_id": company_id,
            "invoice_id": invoice_id
        }
        
        with patch("app.services.agents.AsyncSessionLocal", return_value=mock_session):
            response = client.post("/api/v1/agents/process", json=payload)
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["status"] == "completed"
            assert "report" in data
            
            # Assert DB objects were updated
            assert mock_invoice.status == "completed"
            assert mock_invoice.total_amount == 2200.00
            assert mock_invoice.invoice_number == "INV-2026-88"
            
            # Find the AgentRun in mock_session.added
            added_runs = [x for x in mock_session.added if isinstance(x, AgentRun)]
            assert len(added_runs) == 1
            assert added_runs[0].status == "completed"
    finally:
        app.dependency_overrides.clear()


def test_process_endpoint_invalid_uuids(client):
    """
    Asserts the /process endpoint returns 400 Bad Request when receiving invalid UUID inputs.
    """
    payload = {
        "company_id": "not-a-uuid",
        "invoice_id": str(uuid.uuid4())
    }
    response = client.post("/api/v1/agents/process", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid UUID format" in response.json()["detail"]


def test_process_endpoint_invoice_not_found(client):
    """
    Asserts the /process endpoint returns 404 Not Found if invoice isn't in DB.
    """
    mock_session = AsyncSessionMock(agent_run=None, invoice=None)
    app.dependency_overrides[get_db] = lambda: mock_session
    
    try:
        payload = {
            "company_id": str(uuid.uuid4()),
            "invoice_id": str(uuid.uuid4())
        }
        response = client.post("/api/v1/agents/process", json=payload)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Invoice document record not found" in response.json()["detail"]
    finally:
        app.dependency_overrides.clear()


def test_process_endpoint_crash_handling(client):
    """
    Asserts that if the graph execution crashes, the endpoint updates invoice
    and run status to 'failed', commits, and returns HTTP 500.
    """
    company_id = str(uuid.uuid4())
    invoice_id = str(uuid.uuid4())
    
    mock_invoice = MagicMock()
    mock_invoice.id = uuid.UUID(invoice_id)
    mock_invoice.status = "processing"
    
    mock_run = MagicMock()
    mock_run.id = uuid.uuid4()
    mock_run.status = "running"
    
    mock_session = AsyncSessionMock(agent_run=mock_run, invoice=mock_invoice)
    app.dependency_overrides[get_db] = lambda: mock_session
    
    try:
        payload = {
            "company_id": company_id,
            "invoice_id": invoice_id
        }
        
        # Patch compile_graph.invoke to raise an exception
        with patch.object(compiled_graph, "invoke", side_effect=Exception("Database crash")):
            response = client.post("/api/v1/agents/process", json=payload)
            
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "system crash" in response.json()["detail"]
            
            # Verify status fields were flipped to failed
            assert mock_invoice.status == "failed"
            
            # Find the AgentRun in mock_session.added
            added_runs = [x for x in mock_session.added if isinstance(x, AgentRun)]
            assert len(added_runs) == 1
            assert added_runs[0].status == "failed"
    finally:
        app.dependency_overrides.clear()
