import datetime
import uuid
from unittest.mock import MagicMock, patch
import pytest
from fastapi import status

from main import app
from app.database import get_db
from app.models.invoice import Invoice
from app.models.vendor import Vendor
from app.models.analytics import Analytics
from app.services.financial_intelligence import (
    levenshtein_similarity,
    AnomalyDetector,
    DuplicateDetector,
    VendorRiskScorer,
    TrendAnalyzer,
    PaymentPrioritizer
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


def test_levenshtein_similarity():
    """
    Verifies string metric distance comparisons on invoice numbers.
    """
    # Exact Match
    assert levenshtein_similarity("INV-2026-001", "INV-2026-001") == 1.0
    # Fuzzy variations (typos)
    assert levenshtein_similarity("INV-2026-001", "INV2026001") > 0.80
    # Distinct strings
    assert levenshtein_similarity("INV-2026-001", "BILL-8892-Z") < 0.40


@pytest.mark.asyncio
async def test_anomaly_detector_z_score():
    """
    Asserts anomaly detector flags transaction amounts that deviate significantly from history.
    """
    company_id = uuid.uuid4()
    vendor_id = uuid.uuid4()
    
    # Historical totals: mean = 100.0, std_dev = 0.0 (constant history)
    history_amounts = [(100.0,), (100.0,), (100.0,)]
    
    mock_session = AsyncSessionMock(data_list=history_amounts)
    
    # 1. Non-anomalous invoice
    normal_invoice = Invoice(
        company_id=company_id,
        vendor_id=vendor_id,
        total_amount=100.0,
        issue_date=datetime.date(2026, 6, 1)
    )
    
    is_anomaly, score, reasons = await AnomalyDetector.analyze_invoice(mock_session, normal_invoice)
    assert is_anomaly is False
    assert score == 0.0
    
    # 2. Anomalous invoice (amount deviates from constant history)
    anom_invoice = Invoice(
        company_id=company_id,
        vendor_id=vendor_id,
        total_amount=250.0,
        issue_date=datetime.date(2026, 6, 1)
    )
    
    is_anomaly, score, reasons = await AnomalyDetector.analyze_invoice(mock_session, anom_invoice)
    assert is_anomaly is True
    assert score > 0.7
    assert any("deviates from historical constant" in r for r in reasons)


@pytest.mark.asyncio
async def test_duplicate_detector_exact_and_fuzzy():
    """
    Asserts duplicate detector triggers alerts on matching properties.
    """
    company_id = uuid.uuid4()
    vendor_id = uuid.uuid4()
    
    # Mock pre-existing candidate in DB
    existing_invoice = Invoice(
        id=uuid.uuid4(),
        company_id=company_id,
        vendor_id=vendor_id,
        invoice_number="INV-8899",
        total_amount=1200.00,
        issue_date=datetime.date(2026, 6, 10),
        status="completed"
    )
    
    mock_session = AsyncSessionMock(data_list=[(existing_invoice,)])
    
    # 1. Exact invoice number match
    dup_invoice_num = Invoice(
        id=uuid.uuid4(),
        company_id=company_id,
        vendor_id=vendor_id,
        invoice_number="INV-8899",
        total_amount=500.00,
        issue_date=datetime.date(2026, 6, 15)
    )
    is_dup, match_id, m_type, reasons = await DuplicateDetector.find_duplicates(mock_session, dup_invoice_num)
    assert is_dup is True
    assert m_type == "exact_number"
    assert match_id == str(existing_invoice.id)
    
    # 2. Fuzzy invoice number match
    fuzzy_invoice_num = Invoice(
        id=uuid.uuid4(),
        company_id=company_id,
        vendor_id=vendor_id,
        invoice_number="INV8899",
        total_amount=500.00,
        issue_date=datetime.date(2026, 6, 15)
    )
    is_dup, match_id, m_type, reasons = await DuplicateDetector.find_duplicates(mock_session, fuzzy_invoice_num)
    assert is_dup is True
    assert m_type == "fuzzy_number"


@pytest.mark.asyncio
async def test_vendor_risk_grader():
    """
    Asserts risk scoring yields grading matrix based on historical failures.
    """
    company_id = uuid.uuid4()
    vendor_id = uuid.uuid4()
    
    # Mock vendor record
    vendor = Vendor(id=vendor_id, name="Risk supplier")
    
    # Mock invoices (failed parsing/review flags present)
    inv1 = Invoice(company_id=company_id, vendor_id=vendor_id, status="pending_review", total_amount=100.0)
    inv2 = Invoice(company_id=company_id, vendor_id=vendor_id, status="completed", total_amount=500.0)
    
    mock_session = AsyncSessionMock(data_list=[vendor, (inv1,), (inv2,)])
    
    # Query execute overrides
    async def custom_execute(query, *args, **kwargs):
        mock_res = MagicMock()
        query_str = str(query).lower()
        if "vendors" in query_str:
            mock_res.scalar_one_or_none.return_value = vendor
        elif "invoices" in query_str:
            mock_res.all.return_value = [(inv1,), (inv2,)]
        else:
            mock_res.all.return_value = []
        return mock_res
        
    mock_session.execute = custom_execute
    
    risk_info = await VendorRiskScorer.compute_vendor_risk(mock_session, vendor_id, company_id)
    # 50% checksum failures rate (1 out of 2) -> adds +25 points
    assert risk_info["risk_score"] == 25.0
    assert risk_info["risk_grade"] == "B"
    assert len(risk_info["risk_factors"]) == 1
    assert risk_info["risk_factors"][0]["factor"] == "high_checksum_failure_rate"


@pytest.mark.asyncio
async def test_payment_prioritizer_urgency():
    """
    Asserts prioritizer ranks payments correctly based on due date and risk penalties.
    """
    company_id = uuid.uuid4()
    vendor_id = uuid.uuid4()
    
    # Mock vendor details
    vendor = Vendor(id=vendor_id, name="Parts Distributor")
    
    # Outstanding invoice due in 5 days (highly urgent)
    urgent_invoice = Invoice(
        id=uuid.uuid4(),
        company_id=company_id,
        vendor_id=vendor_id,
        total_amount=1000.00,
        due_date=datetime.date.today() + datetime.timedelta(days=5),
        status="completed"
    )
    
    mock_session = AsyncSessionMock()
    
    # Custom execute mock returning objects
    async def custom_execute(query, *args, **kwargs):
        mock_res = MagicMock()
        query_str = str(query).lower()
        if "vendors" in query_str:
            mock_res.scalar_one_or_none.return_value = vendor
        elif "invoices" in query_str:
            # We return invoice list
            mock_res.all.return_value = [(urgent_invoice,)]
        else:
            mock_res.all.return_value = []
        return mock_res
        
    mock_session.execute = custom_execute
    
    priorities = await PaymentPrioritizer.get_payment_priorities(mock_session, company_id)
    assert len(priorities["queue"]) == 1
    # Base urgency = 30 - 5 = 25. Discount bonus = 0 (days_to_due <= 10). Total score = 25.
    assert priorities["queue"][0]["urgency_score"] == 25.0
    assert priorities["queue"][0]["payment_recommended"] is True


def test_analyze_invoice_endpoint(client):
    """
    Asserts analyze endpoint runs analysis services, logs records inside database, and returns 200 OK.
    """
    company_id = str(uuid.uuid4())
    invoice_id = str(uuid.uuid4())
    
    mock_invoice = MagicMock()
    mock_invoice.id = uuid.UUID(invoice_id)
    mock_invoice.company_id = uuid.UUID(company_id)
    mock_invoice.vendor_id = uuid.uuid4()
    mock_invoice.total_amount = 2500.00
    mock_invoice.issue_date = datetime.date.today()
    mock_invoice.due_date = datetime.date.today() + datetime.timedelta(days=15)
    mock_invoice.status = "completed"
    
    mock_session = AsyncSessionMock(data_list=[mock_invoice])
    app.dependency_overrides[get_db] = lambda: mock_session
    
    try:
        response = client.post(f"/api/v1/analytics/analyze-invoice/{invoice_id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["invoice_id"] == invoice_id
        assert "anomaly" in data
        assert "duplicate" in data
        
        # Verify 2 metrics were saved inside analytics audit log table
        added_analytics = [x for x in mock_session.added if isinstance(x, Analytics)]
        assert len(added_analytics) == 2
        metric_names = [x.metric_name for x in added_analytics]
        assert "invoice_anomaly" in metric_names
        assert "invoice_duplicate" in metric_names
    finally:
        app.dependency_overrides.clear()
