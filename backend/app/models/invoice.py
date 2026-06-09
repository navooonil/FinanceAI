import datetime
import uuid
from sqlalchemy import String, ForeignKey, Date, Numeric, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDPrimaryKeyMixin, TimeStampedModelMixin


class Invoice(Base, UUIDPrimaryKeyMixin, TimeStampedModelMixin):
    """
    Invoice entity model representing bill transactions, status, and processing outputs.
    """
    __tablename__ = "invoices"

    company_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("companies.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    vendor_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("vendors.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    invoice_number: Mapped[str] = mapped_column(String(100), nullable=True)
    issue_date: Mapped[datetime.date] = mapped_column(Date, nullable=True)
    due_date: Mapped[datetime.date] = mapped_column(Date, nullable=True)
    total_amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=True)
    tax_amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(10), default="USD", nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending_ocr", nullable=False)
    s3_key: Mapped[str] = mapped_column(String(500), nullable=True)
    ocr_raw_text: Mapped[str] = mapped_column(Text, nullable=True)

    # Relationships
    company: Mapped["Company"] = relationship("Company", back_populates="invoices")
    vendor: Mapped["Vendor"] = relationship("Vendor", back_populates="invoices")

    # Table indexes for query optimization
    __table_args__ = (
        Index("idx_invoices_company_status_issue_date", "company_id", "status", "issue_date"),
        Index("idx_invoices_company_invoice_number", "company_id", "invoice_number"),
    )
