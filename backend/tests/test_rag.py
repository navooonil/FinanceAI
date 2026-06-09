import uuid
from unittest.mock import MagicMock, patch
import pytest
from fastapi import status

from main import app
from app.database import get_db
from app.services.rag import RecursiveChunker
from app.api.v1.rag_endpoints import rag_service


def test_recursive_chunker_basic():
    """
    Asserts chunker splits text logically under the maximum character size limit.
    """
    chunker = RecursiveChunker(chunk_size=100, chunk_overlap=10)
    text = "This is a short paragraph.\n\nThis is a second paragraph that is slightly longer to test separation logic."
    
    chunks = chunker.chunk_text(text)
    assert len(chunks) >= 2
    assert chunks[0] == "This is a short paragraph."
    assert "second paragraph" in chunks[1]


def test_rag_ingest_endpoint(client):
    """
    Asserts ingest endpoint successfully chunks text, returns HTTP 201 and chunks count.
    """
    company_id = str(uuid.uuid4())
    doc_id = str(uuid.uuid4())
    payload = {
        "company_id": company_id,
        "document_id": doc_id,
        "document_type": "invoice",
        "text_content": "Vendor: Supplies Inc.\nSubtotal: $500\nLine Items:\n1. Copy paper - $100\n2. Pens - $400"
    }

    # Mock Chroma collection add to bypass direct DB write issues
    with patch.object(rag_service, "_collection") as mock_col:
        mock_col.add = MagicMock()
        
        response = client.post("/api/v1/rag/ingest", json=payload)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["status"] == "success"
        assert "chunks_count" in data


def test_rag_query_tenant_isolation(client):
    """
    Asserts query endpoint passes the company_id filter down to vector database queries,
    mitigating cross-tenant data leak risks.
    """
    company_id = str(uuid.uuid4())
    payload = {
        "company_id": company_id,
        "query": "find supplies cost",
        "top_k": 3
    }

    with patch.object(rag_service, "_collection") as mock_col:
        # Mock Chroma DB query result format
        mock_col.query.return_value = {
            "documents": [["Supplies Invoice details"]],
            "metadatas": [[{
                "document_id": str(uuid.uuid4()),
                "document_type": "invoice",
                "company_id": company_id
            }]]
        }

        response = client.post("/api/v1/rag/query", json=payload)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["results"]) == 1
        assert data["results"][0]["text"] == "Supplies Invoice details"
        
        # Critical security validation: Verify Chroma query received company_id filter check
        called_args = mock_col.query.call_args[1]
        assert called_args["where"] == {"company_id": company_id}


# Re-use the AsyncSessionMock from test_ocr to mock the chat database commits
class AsyncSessionMock:
    def __init__(self):
        self.added = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def commit(self):
        pass

    async def flush(self):
        pass

    def add(self, obj):
        self.added.append(obj)


def test_rag_chat_endpoint_audits_exchanges(client):
    """
    Asserts chat endpoint queries vector store, provides grounded response,
    and commits audit records (both User and Assistant lines) inside chat history store.
    """
    company_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())
    payload = {
        "company_id": company_id,
        "user_id": user_id,
        "session_id": session_id,
        "message": "find supplies cost"
    }

    # Mock RAG Service search retrieval
    with patch.object(rag_service, "_collection") as mock_col:
        mock_col.query.return_value = {
            "documents": [["Supplies Invoice cost details"]],
            "metadatas": [[{
                "document_id": str(uuid.uuid4()),
                "document_type": "invoice",
                "company_id": company_id
            }]]
        }

        # Mock DB commits
        mock_session = AsyncSessionMock()
        app.dependency_overrides[get_db] = lambda: mock_session

        try:
            response = client.post("/api/v1/rag/chat", json=payload)
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "answer" in data
            assert data["session_id"] == session_id
            
            # Assert audit records (User line and Assistant line) were saved to chat database
            assert len(mock_session.added) == 2
            
            # Assert roles mapping
            user_record = mock_session.added[0]
            assistant_record = mock_session.added[1]
            assert user_record.role == "user"
            assert user_record.message == "find supplies cost"
            assert assistant_record.role == "assistant"
            assert "Supplies Invoice cost details" in assistant_record.message
        finally:
            app.dependency_overrides.clear()
