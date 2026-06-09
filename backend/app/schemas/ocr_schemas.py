import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class LineItemSchema(BaseModel):
    """
    Schema representing a parsed invoice line item.
    """
    description: str = Field(..., description="Description of the item or service.")
    quantity: float = Field(default=1.0, description="Quantity of the item purchased.")
    unit_price: float = Field(..., description="Price per unit of the item.")
    total_amount: float = Field(..., description="Total price (quantity * unit_price).")


class ExtractedInvoiceSchema(BaseModel):
    """
    Schema representing structured financial parameters extracted from documents.
    """
    invoice_number: Optional[str] = Field(default=None, description="Unique invoice ID identifier.")
    vendor_name: Optional[str] = Field(default=None, description="Name of the creditor/vendor.")
    invoice_date: Optional[datetime.date] = Field(default=None, description="Date of invoice issue.")
    due_date: Optional[datetime.date] = Field(default=None, description="Date of payment deadline.")
    subtotal: Optional[float] = Field(default=None, description="Sum amount before tax.")
    tax_amount: Optional[float] = Field(default=None, description="Total sales/VAT tax amount.")
    total_amount: Optional[float] = Field(default=None, description="Net invoice billing total.")
    currency: str = Field(default="USD", description="Transactional ISO currency.")
    line_items: List[LineItemSchema] = Field(default_factory=list, description="Parsed invoice line items.")
    confidence_score: float = Field(default=0.0, description="Composite validation score from 0.0 to 1.0.")


class OCRAuditLogSchema(BaseModel):
    """
    Schema documenting execution telemetry for the audit logs database.
    """
    invoice_id: str = Field(..., description="The associated PostgreSQL invoice UUID.")
    engine_used: str = Field(..., description="The name of the OCR engine used (e.g. GPT-4o, Tesseract).")
    processing_time_ms: int = Field(..., description="Total extraction processing duration.")
    confidence_score: float = Field(..., description="Calculated aggregate parser confidence score.")
    validation_warnings: List[str] = Field(default_factory=list, description="List of checksum or verification alerts.")
    extracted_fields_count: int = Field(..., description="Number of financial attributes successfully populated.")
