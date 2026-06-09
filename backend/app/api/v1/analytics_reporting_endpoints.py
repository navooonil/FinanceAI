import datetime
import logging
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.analytics import Analytics
from app.schemas.analytics_reporting_schemas import (
    EventTrackRequest,
    BusinessKPISummaryResponse,
    KPIMetricItem,
    UserJourneyResponse,
    FunnelStage,
    AIImpactSummaryResponse,
    GrowthMetricsResponse
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/track", status_code=status.HTTP_201_CREATED)
async def track_analytics_event(
    request: EventTrackRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Ingests product analytics events. Persists checkpoints inside postgres tables.
    """
    try:
        company_uuid = uuid.UUID(request.company_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid UUID format for company_id."
        )

    # Instantiate event timeseries metric record
    record = Analytics(
        company_id=company_uuid,
        metric_name=request.event_name,
        metric_value=request.value,
        dimensions=request.dimensions
    )
    db.add(record)
    await db.commit()

    return {
        "status": "success",
        "message": f"Successfully tracked event: {request.event_name}"
    }


@router.get("/kpis/{company_id}", response_model=BusinessKPISummaryResponse, status_code=status.HTTP_200_OK)
async def get_business_kpis(
    company_id: str,
    start_date: Optional[str] = Query(None, description="Start filter YYYY-MM-DD."),
    end_date: Optional[str] = Query(None, description="End filter YYYY-MM-DD."),
    db: AsyncSession = Depends(get_db)
):
    """
    Compiles average turnaround time, duplicate rates, and validation metrics for Dashboards.
    """
    try:
        company_uuid = uuid.UUID(company_id)
        start = datetime.datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else (datetime.date.today() - datetime.timedelta(days=30))
        end = datetime.datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else datetime.date.today()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid format parameters."
        )

    # Fetch anomaly metrics counts
    anom_stmt = select(func.count(Analytics.id)).where(
        Analytics.company_id == company_uuid,
        Analytics.metric_name == "invoice_anomaly",
        Analytics.timestamp >= start,
        Analytics.timestamp <= end
    )
    anom_res = await db.execute(anom_stmt)
    anomaly_runs = anom_res.scalar() or 0

    # Fetch duplicate metrics counts
    dup_stmt = select(func.count(Analytics.id)).where(
        Analytics.company_id == company_uuid,
        Analytics.metric_name == "invoice_duplicate",
        Analytics.timestamp >= start,
        Analytics.timestamp <= end
    )
    dup_res = await db.execute(dup_stmt)
    duplicate_runs = dup_res.scalar() or 0

    # Mock turnaround metrics calculations based on task execution stats
    avg_turnaround_time_ms = 450.0
    workflow_success_rate = 98.4

    kpi_list = [
        KPIMetricItem(metric_name="avg_invoice_processing_ms", value=avg_turnaround_time_ms, description="Average time taken for OCR & Validation algorithms to run."),
        KPIMetricItem(metric_name="workflow_success_rate", value=workflow_success_rate, description="Percentage of workflows completed without error paths."),
        KPIMetricItem(metric_name="anomaly_runs_count", value=float(anomaly_runs), description="Total volume of anomaly analysis cycles executed."),
        KPIMetricItem(metric_name="duplicate_runs_count", value=float(duplicate_runs), description="Total duplicate invoice detection checks run.")
    ]

    return {
        "company_id": company_id,
        "start_date": start,
        "end_date": end,
        "kpis": kpi_list
    }


@router.get("/funnel/{company_id}", response_model=UserJourneyResponse, status_code=status.HTTP_200_OK)
async def get_user_journey_funnel(
    company_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Evaluates step conversions across the document lifecycle.
    """
    try:
        company_uuid = uuid.UUID(company_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid company_id UUID.")

    # In a real app we query distinct session event logs in Analytics.
    # Here we mock a standard conversion pattern representing: Onboarding -> Upload -> Analysis -> Workflow Complete
    stages = [
        FunnelStage(stage_name="1_onboarded", count=100, conversion_rate=1.0, dropoff_rate=0.0),
        FunnelStage(stage_name="2_document_uploaded", count=85, conversion_rate=0.85, dropoff_rate=0.15),
        FunnelStage(stage_name="3_analysis_reviewed", count=70, conversion_rate=0.70, dropoff_rate=0.176),
        FunnelStage(stage_name="4_workflow_executed", count=60, conversion_rate=0.60, dropoff_rate=0.142)
    ]

    return {
        "company_id": company_id,
        "funnel_name": "Onboarding to Ingestion Conversion Funnel",
        "stages": stages
    }


@router.get("/ai-impact/{company_id}", response_model=AIImpactSummaryResponse, status_code=status.HTTP_200_OK)
async def get_ai_impact_metrics(
    company_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Compiles value created parameters, calculating hours saved and automation rates.
    """
    try:
        company_uuid = uuid.UUID(company_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid company_id UUID.")

    # Mock parameters compiled from database records
    tasks_automated = 342
    accepted = 290
    rejected = 12
    acceptance_rate = accepted / max(1, (accepted + rejected))
    # Heuristic: assume 0.5 hours saved per automated document
    hours_saved = tasks_automated * 0.5

    return {
        "company_id": company_id,
        "tasks_automated_count": tasks_automated,
        "recommendations_accepted": accepted,
        "recommendations_rejected": rejected,
        "acceptance_rate": round(acceptance_rate, 4),
        "estimated_hours_saved": round(hours_saved, 1)
    }


@router.get("/growth/{company_id}", response_model=GrowthMetricsResponse, status_code=status.HTTP_200_OK)
async def get_growth_metrics(
    company_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Tracks DAU/MAU ratios and 28d user retention indices.
    """
    try:
        company_uuid = uuid.UUID(company_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid company_id UUID.")

    # Mocking active users metrics
    dau = 15
    wau = 35
    mau = 45
    stickiness = dau / mau if mau > 0 else 0.0
    retention = 82.5

    return {
        "company_id": company_id,
        "dau": dau,
        "wau": wau,
        "mau": mau,
        "stickiness_ratio": round(stickiness, 4),
        "retention_rate_28d": retention
    }
