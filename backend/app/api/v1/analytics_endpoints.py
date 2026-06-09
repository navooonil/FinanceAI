import datetime
import logging
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.invoice import Invoice
from app.models.vendor import Vendor
from app.models.analytics import Analytics
from app.schemas.analytics_schemas import (
    InvoiceAnalysisResponseSchema,
    VendorRiskReportSchema,
    SpendTrendResponseSchema,
    PaymentPriorityQueueSchema,
    AnomalyDetail,
    DuplicateDetail
)
from app.services.financial_intelligence import (
    AnomalyDetector,
    DuplicateDetector,
    VendorRiskScorer,
    TrendAnalyzer,
    PaymentPrioritizer
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/analyze-invoice/{invoice_id}", response_model=InvoiceAnalysisResponseSchema, status_code=status.HTTP_200_OK)
async def analyze_invoice_metrics(
    invoice_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Executes core duplicate detection and anomaly scoring on an ingested invoice document.
    Persists resulting checkpoints inside the analytics history store.
    """
    try:
        invoice_uuid = uuid.UUID(invoice_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid UUID format for invoice_id."
        )

    # 1. Fetch invoice record
    res = await db.execute(select(Invoice).where(Invoice.id == invoice_uuid))
    invoice = res.scalar_one_or_none()
    
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice record not found."
        )

    # 2. Run analysis services
    is_anomaly, anomaly_score, anomaly_reasons = await AnomalyDetector.analyze_invoice(db, invoice)
    is_duplicate, matching_id, match_type, duplicate_reasons = await DuplicateDetector.find_duplicates(db, invoice)

    # 3. Calculate urgency score
    today = datetime.date.today()
    due_date = invoice.due_date or (today + datetime.timedelta(days=30))
    days_to_due = (due_date - today).days
    
    base_urgency = max(0.0, 30.0 - float(days_to_due))
    discount_bonus = 15.0 if days_to_due > 10 else 0.0
    urgency_score = base_urgency + discount_bonus

    priority_reason = "Urgent attention required due to proximity to due date."
    if urgency_score > 35.0:
        priority_reason = "Highest priority: early payment discount window is active."

    # 4. Save results to the analytics audit table
    anomaly_record = Analytics(
        company_id=invoice.company_id,
        metric_name="invoice_anomaly",
        metric_value=1.0 if is_anomaly else 0.0,
        dimensions={
            "invoice_id": str(invoice.id),
            "is_anomaly": is_anomaly,
            "anomaly_score": anomaly_score,
            "reasons": anomaly_reasons
        }
    )

    duplicate_record = Analytics(
        company_id=invoice.company_id,
        metric_name="invoice_duplicate",
        metric_value=1.0 if is_duplicate else 0.0,
        dimensions={
            "invoice_id": str(invoice.id),
            "is_duplicate": is_duplicate,
            "matching_invoice_id": matching_id,
            "match_type": match_type,
            "reasons": duplicate_reasons
        }
    )

    db.add(anomaly_record)
    db.add(duplicate_record)
    await db.commit()

    return {
        "invoice_id": str(invoice.id),
        "company_id": str(invoice.company_id),
        "anomaly": AnomalyDetail(
            is_anomaly=is_anomaly,
            score=anomaly_score,
            reasons=anomaly_reasons
        ),
        "duplicate": DuplicateDetail(
            is_duplicate=is_duplicate,
            matching_invoice_id=matching_id,
            match_type=match_type,
            reasons=duplicate_reasons
        ),
        "urgency_score": urgency_score,
        "priority_reason": priority_reason
    }


@router.get("/vendor-risk/{company_id}", response_model=List[VendorRiskReportSchema], status_code=status.HTTP_200_OK)
async def get_vendor_risk_reports(
    company_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Computes and aggregates operational risk grade indices for all counters.
    """
    try:
        company_uuid = uuid.UUID(company_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid UUID format for company_id."
        )

    # Fetch all vendor IDs who have invoiced this tenant
    stmt = select(Invoice.vendor_id).where(Invoice.company_id == company_uuid).distinct()
    res = await db.execute(stmt)
    vendor_ids = [row[0] for row in res.all() if row[0] is not None]

    reports = []
    for v_id in vendor_ids:
        risk_info = await VendorRiskScorer.compute_vendor_risk(db, v_id, company_uuid)
        reports.append(risk_info)

    return reports


@router.get("/trends/{company_id}", response_model=SpendTrendResponseSchema, status_code=status.HTTP_200_OK)
async def get_monthly_spend_trends(
    company_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves aggregated month-over-month spend aggregates and total transaction indexes.
    """
    try:
        company_uuid = uuid.UUID(company_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid UUID format for company_id."
        )

    trend_results = await TrendAnalyzer.get_spend_trends(db, company_uuid)
    return trend_results


@router.get("/prioritize-payments/{company_id}", response_model=PaymentPriorityQueueSchema, status_code=status.HTTP_200_OK)
async def get_payment_prioritizations(
    company_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Returns lists of outstanding invoice transactions sorted descending by urgency cash priorities.
    """
    try:
        company_uuid = uuid.UUID(company_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid UUID format for company_id."
        )

    prioritized_queue = await PaymentPrioritizer.get_payment_priorities(db, company_uuid)
    return prioritized_queue
