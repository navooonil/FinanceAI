import uuid
import datetime
from sqlalchemy import ForeignKey, Date, Numeric, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDPrimaryKeyMixin, TimeStampedModelMixin


class BusinessMetric(Base, UUIDPrimaryKeyMixin, TimeStampedModelMixin):
    """
    BusinessMetric model stores parsed monthly financial metrics uploaded via CSV.
    """
    __tablename__ = "business_metrics"

    company_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    month: Mapped[datetime.date] = mapped_column(Date, nullable=False, unique=False, index=True)
    revenue: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    expenses: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    profit: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    customers: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relationships
    company: Mapped["Company"] = relationship("Company", back_populates="business_metrics")
