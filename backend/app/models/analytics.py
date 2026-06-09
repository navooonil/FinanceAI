import datetime
import uuid
from sqlalchemy import String, ForeignKey, DateTime, Numeric, Index, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDPrimaryKeyMixin


class Analytics(Base, UUIDPrimaryKeyMixin):
    """
    Analytics entity model. Stores aggregated operational metrics for dashboards.
    Inherits UUIDPrimaryKey but does not need TimeStampedModelMixin since it uses
    a custom explicit 'timestamp' column.
    """
    __tablename__ = "analytics"

    company_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("companies.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    metric_name: Mapped[str] = mapped_column(String(255), nullable=False)
    metric_value: Mapped[float] = mapped_column(Numeric(15, 4), nullable=False)
    dimensions: Mapped[dict] = mapped_column(JSONB, nullable=True)
    timestamp: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relationships
    company: Mapped["Company"] = relationship("Company", back_populates="analytics_records")

    # Composite index for metric lookups
    __table_args__ = (
        Index("idx_analytics_lookup", "company_id", "metric_name", "timestamp"),
    )
