import datetime
import uuid
from sqlalchemy import String, ForeignKey, Date, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDPrimaryKeyMixin, TimeStampedModelMixin


class Report(Base, UUIDPrimaryKeyMixin, TimeStampedModelMixin):
    """
    Report entity model. Stores compiled financial summaries and metrics generated
    either by schedules or user requests.
    """
    __tablename__ = "reports"

    company_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("companies.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    creator_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    report_type: Mapped[str] = mapped_column(String(100), nullable=False)
    start_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    end_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    content: Mapped[dict] = mapped_column(JSONB, nullable=False)

    # Relationships
    company: Mapped["Company"] = relationship("Company", back_populates="reports")
    creator: Mapped["User"] = relationship("User", back_populates="reports")

    # Composite indexing for dashboard filtering
    __table_args__ = (
        Index("idx_reports_company_type_created", "company_id", "report_type", "created_at"),
    )
