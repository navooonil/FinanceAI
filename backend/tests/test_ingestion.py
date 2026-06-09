import uuid
from unittest.mock import patch, MagicMock
import pytest
from fastapi import status

from main import app
from app.database import get_db


@pytest.fixture
def mock_storage():
    with patch("app.api.v1.endpoints.storage_service") as mock:
        yield mock


@pytest.fixture
def mock_celery():
    with patch("app.api.v1.endpoints.process_document_task") as mock:
        yield mock


def test_upload_invoice_mimetype_rejected(client):
    """
    Asserts HTTP 400 Bad Request is returned when uploading a file of unsupported mimetype.
    """
    company_id = str(uuid.uuid4())
    file_content = b"fake file content"
    files = {"file": ("document.txt", file_content, "text/plain")}
    data = {"company_id": company_id}

    response = client.post("/api/v1/invoices/upload", files=files, data=data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Unsupported file format" in response.json()["detail"]


def test_upload_invoice_size_rejected(client):
    """
    Asserts HTTP 400 Bad Request when file size exceeds the 10MB limit.
    """
    company_id = str(uuid.uuid4())
    # Create content larger than 10MB
    oversized_content = b"a" * (10 * 1024 * 1024 + 1)
    files = {"file": ("invoice.pdf", oversized_content, "application/pdf")}
    data = {"company_id": company_id}

    response = client.post("/api/v1/invoices/upload", files=files, data=data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "File too large" in response.json()["detail"]


def test_upload_invoice_invalid_company_uuid(client):
    """
    Asserts HTTP 400 Bad Request when company_id is not a valid UUID format.
    """
    files = {"file": ("invoice.pdf", b"pdf content", "application/pdf")}
    data = {"company_id": "not-a-uuid"}

    response = client.post("/api/v1/invoices/upload", files=files, data=data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid company_id" in response.json()["detail"]


def test_upload_invoice_success(client, mock_storage, mock_celery):
    """
    Asserts invoice uploads successfully, gets persisted, and worker task is scheduled.
    Uses app.dependency_overrides to correctly mock the async database connection.
    """
    company_id = str(uuid.uuid4())
    file_content = b"%PDF-1.4 header contents of pdf"
    files = {"file": ("invoice.pdf", file_content, "application/pdf")}
    data = {"company_id": company_id}

    mock_storage.upload_file.return_value = "tenants/test-path/invoice.pdf"
    
    mock_session = MagicMock()
    async def mock_commit(): pass
    async def mock_flush():
        # Simulate generating a primary key
        mock_session.add.call_args[0][0].id = uuid.uuid4()
        
    mock_session.commit = mock_commit
    mock_session.flush = mock_flush
    
    async def override_get_db():
        yield mock_session
        
    app.dependency_overrides[get_db] = override_get_db

    try:
        response = client.post("/api/v1/invoices/upload", files=files, data=data)
        
        assert response.status_code == status.HTTP_202_ACCEPTED
        response_json = response.json()
        assert "invoice_id" in response_json
        assert response_json["status"] == "pending_ocr"
        
        # Verify storage was called
        mock_storage.upload_file.assert_called_once()
        # Verify celery was triggered
        mock_celery.delay.assert_called_once_with(response_json["invoice_id"])
    finally:
        # Clear dependencies overrides to prevent leakage
        app.dependency_overrides.clear()
