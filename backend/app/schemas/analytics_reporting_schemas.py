from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import datetime

from app.schemas.base import APIResponseBase


class EventTrackRequest(BaseModel):
    """
    Schema for tracking product usage events.
    """
    company_id: str = Field(..., description="Tenant UUID.")
    user_id: Optional[str] = Field(None, description="User UUID.")
    event_name: str = Field(..., description="Product event key (e.g. 'document_uploaded').")
    value: float = Field(1.0, description="Numerical metric value associated with event.")
    dimensions: Dict[str, Any] = Field(default_factory=dict, description="Metadata dimensions (e.g. browser, file_type).")


class KPIMetricItem(BaseModel):
    """
    Representation of a single KPI metric.
    """
    metric_name: str
    value: float
    description: str


class BusinessKPISummaryResponse(APIResponseBase):
    """
    Response schema returning computed Business KPIs for dashboard rendering.
    """
    company_id: str
    start_date: datetime.date
    end_date: datetime.date
    kpis: List[KPIMetricItem]


class FunnelStage(BaseModel):
    """
    Funnel step representation showing user progression.
    """
    stage_name: str
    count: int
    conversion_rate: float = Field(..., description="Conversion rate relative to first step.")
    dropoff_rate: float = Field(..., description="Drop-off rate from previous step.")


class UserJourneyResponse(APIResponseBase):
    """
    Funnel query response mapping onboarding & workflow completion conversions.
    """
    company_id: str
    funnel_name: str
    stages: List[FunnelStage]


class AIImpactSummaryResponse(APIResponseBase):
    """
    Analytics detailing AI tasks automated, recommendation approvals, and time saved.
    """
    company_id: str
    tasks_automated_count: int
    recommendations_accepted: int
    recommendations_rejected: int
    acceptance_rate: float = Field(..., description="Accepted / Total Recommendations Ratio.")
    estimated_hours_saved: float = Field(..., description="Calculated duration savings in human-hours.")


class GrowthMetricsResponse(APIResponseBase):
    """
    Usage metrics detailing active users, retention, and engagement indices.
    """
    company_id: str
    dau: int = Field(..., description="Daily Active Users count.")
    wau: int = Field(..., description="Weekly Active Users count.")
    mau: int = Field(..., description="Monthly Active Users count.")
    stickiness_ratio: float = Field(..., description="DAU / MAU ratio indicating user stickiness.")
    retention_rate_28d: float = Field(..., description="28-day user retention percentage.")
