import datetime
import uuid
from unittest.mock import MagicMock, patch
import pytest
from fastapi import status

from main import app
from app.database import get_db
from app.models.analytics import Analytics


class AsyncSessionMock:
    """
    Class-based mock for SQLAlchemy async sessions.
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
        # Return mock count for metric aggregations
        mock_res.scalar.return_value = len(self.data_list)
        return mock_res

    async def commit(self):
        pass

    def add(self, obj):
        self.added.append(obj)


def test_track_event_endpoint(client):
    """
    Asserts track endpoint persists event telemetry logs to database.
    """
    company_id = str(uuid.uuid4())
    payload = {
        "company_id": company_id,
        "event_name": "document_uploaded",
        "value": 1.0,
        "dimensions": {"file_type": "PDF", "file_size_bytes": 450000}
    }

    mock_session = AsyncSessionMock()
    app.dependency_overrides[get_db] = lambda: mock_session

    try:
        response = client.post("/api/v1/analytics-reporting/track", json=payload)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["status"] == "success"
        
        # Verify row was added to DB
        assert len(mock_session.added) == 1
        record = mock_session.added[0]
        assert isinstance(record, Analytics)
        assert record.metric_name == "document_uploaded"
        assert record.metric_value == 1.0
        assert record.dimensions["file_type"] == "PDF"
    finally:
        app.dependency_overrides.clear()


def test_get_kpis_endpoint(client):
    """
    Asserts KPI retrieval returns configured lists of metric values.
    """
    company_id = str(uuid.uuid4())
    mock_session = AsyncSessionMock(data_list=[1, 2, 3]) # Mock results count
    app.dependency_overrides[get_db] = lambda: mock_session

    try:
        response = client.get(f"/api/v1/analytics-reporting/kpis/{company_id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["company_id"] == company_id
        assert len(data["kpis"]) == 4
        
        # Assert specific metric is present
        names = [x["metric_name"] for x in data["kpis"]]
        assert "avg_invoice_processing_ms" in names
        assert "workflow_success_rate" in names
    finally:
        app.dependency_overrides.clear()


def test_funnel_and_impact_endpoints(client):
    """
    Asserts conversion funnel and AI impact statistics serialize successfully.
    """
    company_id = str(uuid.uuid4())
    mock_session = AsyncSessionMock()
    app.dependency_overrides[get_db] = lambda: mock_session

    try:
        # 1. Test Funnel API
        response = client.get(f"/api/v1/analytics-reporting/funnel/{company_id}")
        assert response.status_code == status.HTTP_200_OK
        funnel = response.json()
        assert len(funnel["stages"]) == 4
        assert funnel["stages"][0]["stage_name"] == "1_onboarded"

        # 2. Test AI Impact API
        response = client.get(f"/api/v1/analytics-reporting/ai-impact/{company_id}")
        assert response.status_code == status.HTTP_200_OK
        impact = response.json()
        assert "estimated_hours_saved" in impact
        assert impact["acceptance_rate"] > 0.90
    finally:
        app.dependency_overrides.clear()
