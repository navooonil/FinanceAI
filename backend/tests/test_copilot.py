import datetime
import uuid
from unittest.mock import MagicMock, patch
import pytest
from fastapi import status

from main import app
from app.database import get_db
from app.models.invoice import Invoice
from app.models.vendor import Vendor
from app.models.chat import ChatHistory
from app.services.copilot import AICopilotService


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


@pytest.mark.asyncio
async def test_copilot_intent_classification():
    """
    Asserts AI Copilot routes queries correctly based on message triggers.
    """
    company_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())
    
    mock_session = AsyncSessionMock()
    
    # 1. Overdue Invoices Intent
    res = await AICopilotService.process_message(
        mock_session, company_id, None, session_id, "Which invoices are overdue on our ledger?"
    )
    assert res["intent"] == "overdue_invoices"
    
    # 2. Risky Vendors Intent
    res = await AICopilotService.process_message(
        mock_session, company_id, None, session_id, "Show me the risky suppliers."
    )
    assert res["intent"] == "risky_vendors"
    
    # 3. Spending Trends Intent
    res = await AICopilotService.process_message(
        mock_session, company_id, None, session_id, "Show our spending trends by month."
    )
    assert res["intent"] == "spending_trends"
    
    # 4. Cashflow Projection Intent
    res = await AICopilotService.process_message(
        mock_session, company_id, None, session_id, "Predict future cashflow runway runway shortages."
    )
    assert res["intent"] == "cashflow_projection"
    
    # 5. Document RAG Intent (Fallback)
    with patch("app.services.copilot.RAGService") as mock_rag_class:
        mock_rag = MagicMock()
        mock_rag.generate_chat_response.return_value = ("RAG Answer", [])
        mock_rag_class.return_value = mock_rag
        
        res = await AICopilotService.process_message(
            mock_session, company_id, None, session_id, "What is the policy for invoice audits?"
        )
        assert res["intent"] == "document_rag"


@pytest.mark.asyncio
async def test_copilot_overdue_invoices_lookup():
    """
    Asserts overdue invoices intent triggers correct DB scans and compiles Markdown tables.
    """
    company_id = uuid.uuid4()
    session_id = uuid.uuid4()
    vendor_id = uuid.uuid4()
    
    # Overdue invoice
    overdue_inv = Invoice(
        id=uuid.uuid4(),
        company_id=company_id,
        vendor_id=vendor_id,
        invoice_number="INV-OVERDUE-01",
        total_amount=1500.00,
        due_date=datetime.date.today() - datetime.timedelta(days=10),
        status="completed"
    )
    vendor = Vendor(id=vendor_id, name="Overdue Supplier Corp")
    
    mock_session = AsyncSessionMock()
    
    # Custom execute mock returning queries
    async def custom_execute(query, *args, **kwargs):
        mock_res = MagicMock()
        query_str = str(query).lower()
        if "vendors" in query_str:
            mock_res.scalar_one_or_none.return_value = vendor.name
        elif "invoices" in query_str:
            mock_res.all.return_value = [(overdue_inv,)]
        else:
            mock_res.all.return_value = []
            mock_res.scalar_one_or_none.return_value = None
        return mock_res
        
    mock_session.execute = custom_execute
    
    res = await AICopilotService.process_message(
        mock_session, str(company_id), None, str(session_id), "Show unpaid overdue bills"
    )
    
    assert res["intent"] == "overdue_invoices"
    assert "INV-OVERDUE-01" in res["answer"]
    assert "Overdue Supplier Corp" in res["answer"]
    assert res["citations"] == ["Database (invoices table)"]
    assert len(res["structured_data"]["overdue_invoices"]) == 1
    
    # Verify ChatHistory row logs were added to DB (User and Assistant rows)
    added_chat = [x for x in mock_session.added if isinstance(x, ChatHistory)]
    assert len(added_chat) == 2
    assert added_chat[0].role == "user"
    assert added_chat[1].role == "assistant"
    assert added_chat[1].metadata_info["intent"] == "overdue_invoices"


def test_copilot_chat_endpoint(client):
    """
    Asserts copilot endpoint processes conversational payload and returns 200 OK.
    """
    company_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())
    
    mock_session = AsyncSessionMock()
    app.dependency_overrides[get_db] = lambda: mock_session
    
    try:
        payload = {
            "company_id": company_id,
            "session_id": session_id,
            "message": "Which invoices are overdue?"
        }
        
        # Patch process_message call
        with patch.object(AICopilotService, "process_message") as mock_process:
            mock_process.return_value = {
                "answer": "Answer summary text.",
                "session_id": session_id,
                "intent": "overdue_invoices",
                "citations": ["Database"],
                "structured_data": {}
            }
            
            response = client.post("/api/v1/copilot/chat", json=payload)
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["session_id"] == session_id
            assert data["intent"] == "overdue_invoices"
            assert data["citations"] == ["Database"]
            mock_process.assert_called_once()
    finally:
        app.dependency_overrides.clear()
