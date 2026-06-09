import hashlib
import hmac
import uuid
from unittest.mock import MagicMock
import pytest
from fastapi import status

from main import app
from app.database import get_db
from app.models.analytics import Analytics


class AsyncSessionMock:
    """
    Class-based mock for SQLAlchemy sessions.
    """
    def __init__(self):
        self.added = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def commit(self):
        pass

    def add(self, obj):
        self.added.append(obj)


def test_webhook_registration(client):
    """
    Asserts third-party webhooks can be registered with event scopes.
    """
    company_id = str(uuid.uuid4())
    payload = {
        "company_id": company_id,
        "target_url": "https://external-receiver.com/webhook",
        "event_scopes": ["invoice.completed", "workflow.waiting_for_approval"],
        "secret_token": "super-secure-token-shared-with-third-party"
    }

    mock_session = AsyncSessionMock()
    app.dependency_overrides[get_db] = lambda: mock_session

    try:
        response = client.post("/api/v1/integrations/webhooks", json=payload)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["company_id"] == company_id
        assert data["target_url"] == "https://external-receiver.com/webhook"
        assert "invoice.completed" in data["event_scopes"]
        
        # Verify telemetry audit row
        assert len(mock_session.added) == 1
        record = mock_session.added[0]
        assert isinstance(record, Analytics)
        assert record.metric_name == "webhook_subscription_created"
    finally:
        app.dependency_overrides.clear()


def test_configure_connector(client):
    """
    Asserts connection details to external ERP platforms can be registered.
    """
    company_id = str(uuid.uuid4())
    payload = {
        "company_id": company_id,
        "system_name": "netsuite",
        "auth_credentials": {
            "account_id": "NS_12345",
            "consumer_key": "key-secret-abc",
            "token_secret": "token-secret-xyz"
        }
    }

    mock_session = AsyncSessionMock()
    app.dependency_overrides[get_db] = lambda: mock_session

    try:
        response = client.post("/api/v1/integrations/configs", json=payload)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["company_id"] == company_id
        assert data["system_name"] == "netsuite"
        assert data["is_active"] is True
        
        # Verify telemetry audit row
        assert len(mock_session.added) == 1
        assert mock_session.added[0].metric_name == "integration_connector_configured"
    finally:
        app.dependency_overrides.clear()


def test_signature_verification(client):
    """
    Asserts signature helper computes HMAC signatures correctly.
    """
    company_id = str(uuid.uuid4())
    payload = {
        "invoice_id": str(uuid.uuid4()),
        "status": "completed",
        "total": 1500.00
    }
    secret = "hmac-shared-key-value"
    
    response = client.post(
        f"/api/v1/integrations/webhooks/test-dispatch?company_id={company_id}&event_type=invoice.completed&secret_token={secret}",
        json=payload
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "dispatched"
    assert "X-Finance-Signature" in data["header_key"]
    
    # Manually compute signature to verify correctness
    import json
    payload_bytes = json.dumps(payload, sort_keys=True).encode("utf-8")
    expected = hmac.new(secret.encode("utf-8"), payload_bytes, hashlib.sha256).hexdigest()
    
    assert expected in data["header_val"]
