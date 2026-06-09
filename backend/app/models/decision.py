import uuid
import datetime
from sqlalchemy import String, ForeignKey, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDPrimaryKeyMixin


class Decision(Base, UUIDPrimaryKeyMixin):
    """
    Decision model stores user choices from the Decision Center, outcomes, and performance changes.
    """
    __tablename__ = "tracked_decisions"

    company_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    problem_type: Mapped[str] = mapped_column(String(100), nullable=False)
    problem_description: Mapped[str] = mapped_column(Text, nullable=False)
    selected_action: Mapped[str] = mapped_column(String(255), nullable=False)
    expected_impact: Mapped[str] = mapped_column(String(255), nullable=False)
    priority: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False) # pending, implemented, completed
    outcome: Mapped[str] = mapped_column(Text, nullable=True)
    performance_change: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relationships
    company: Mapped["Company"] = relationship("Company", back_populates="tracked_decisions")
