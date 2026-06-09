import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

from app.schemas.base import APIResponseBase


class AnomalyDetail(BaseModel):
    """
    Detailed anomaly detection metrics for an invoice.
    """
    is_anomaly: bool = Field(..., description="Flag indicating if the invoice amount or timing is anomalous.")
    score: float = Field(..., description="Anomaly score. Higher is more anomalous.")
    reasons: List[str] = Field(..., description="Text explanations for the anomaly flags.")


class DuplicateDetail(BaseModel):
    """
    Duplicate invoice analysis metrics.
    """
    is_duplicate: bool = Field(..., description="Flag indicating if a duplicate invoice was detected.")
    matching_invoice_id: Optional[str] = Field(None, description="UUID of the matching duplicate invoice.")
    match_type: Optional[str] = Field(None, description="Exact or fuzzy match description.")
    reasons: List[str] = Field(..., description="Detail reasoning for duplicate determination.")


class InvoiceAnalysisResponseSchema(APIResponseBase):
    """
    Response schema returning comprehensive anomaly, duplicate, and urgency results.
    """
    invoice_id: str = Field(..., description="Target invoice UUID.")
    company_id: str = Field(..., description="Tenant UUID.")
    anomaly: AnomalyDetail
    duplicate: DuplicateDetail
    urgency_score: float = Field(..., description="Calculated urgency score for payment priority.")
    priority_reason: str = Field(..., description="Explainable reason behind the payment priority grade.")


class VendorRiskFactor(BaseModel):
    """
    Singular risk indicator for a vendor.
    """
    factor: str = Field(..., description="Name of risk factor.")
    description: str = Field(..., description="Description of risk factor.")


class VendorRiskReportSchema(APIResponseBase):
    """
    Response schema displaying a vendor's risk grade and contributing factors.
    """
    vendor_id: str = Field(..., description="Vendor UUID.")
    vendor_name: str = Field(..., description="Name of the supplier.")
    risk_grade: str = Field(..., description="Operational risk grade (A, B, C, D, F).")
    risk_score: float = Field(..., description="Risk score mapping between 0 (safe) to 100 (high risk).")
    risk_factors: List[VendorRiskFactor] = Field(..., description="List of operational risk flags.")
    confidence_score: float = Field(..., description="Confidence rating in the risk assessment.")


class SpendTrendItemSchema(BaseModel):
    """
    Spend aggregates for a specific monthly duration.
    """
    period: str = Field(..., description="Year and month period string (YYYY-MM).")
    total_spend: float = Field(..., description="Aggregated spend total.")
    mom_percent_change: float = Field(..., description="Month-over-month percent change.")
    invoice_count: int = Field(..., description="Number of invoices processed in the period.")


class SpendTrendResponseSchema(APIResponseBase):
    """
    Response schema returning spend trends over time.
    """
    company_id: str = Field(..., description="Tenant UUID.")
    overall_growth_rate: float = Field(..., description="Weighted growth rate across the periods.")
    trends: List[SpendTrendItemSchema] = Field(..., description="List of monthly spend trends.")


class PaymentPriorityItemSchema(BaseModel):
    """
    Details of a single unpaid transaction inside the prioritization queue.
    """
    invoice_id: str = Field(..., description="Invoice UUID.")
    invoice_number: Optional[str] = Field(None, description="Invoice reference number.")
    vendor_name: str = Field(..., description="Counterparty name.")
    total_amount: float = Field(..., description="Remaining transaction balance.")
    due_date: datetime.date = Field(..., description="Payment due date.")
    urgency_score: float = Field(..., description="Calculated payment queue prioritization score.")
    discount_available: bool = Field(..., description="Flag indicating if early payment dynamic discounts are active.")
    payment_recommended: bool = Field(..., description="Final payment priority recommendation indicator.")


class PaymentPriorityQueueSchema(APIResponseBase):
    """
    List of unpaid invoices prioritized by early discount capture and risk profiles.
    """
    company_id: str = Field(..., description="Tenant UUID.")
    queue: List[PaymentPriorityItemSchema] = Field(..., description="Prioritized list of invoice items.")
