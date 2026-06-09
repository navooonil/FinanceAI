import uuid
from sqlalchemy import String, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDPrimaryKeyMixin, TimeStampedModelMixin


class Vendor(Base, UUIDPrimaryKeyMixin, TimeStampedModelMixin):
    """
    Vendor entity model representing suppliers/creditors billing the company.
    """
    __tablename__ = "vendors"

    company_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("companies.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    tax_id: Mapped[str] = mapped_column(String(100), nullable=True)
    address: Mapped[str] = mapped_column(String(500), nullable=True)
    contact_email: Mapped[str] = mapped_column(String(255), nullable=True)

    # Relationships
    company: Mapped["Company"] = relationship("Company", back_populates="vendors")
    invoices: Mapped[list["Invoice"]] = relationship("Invoice", back_populates="vendor")

    # Table arguments for multi-tenant compound indexes
    __table_args__ = (
        Index("idx_vendors_company_name", "company_id", "name"),
        Index("idx_vendors_company_tax_id", "company_id", "tax_id"),
    )
