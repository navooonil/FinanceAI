import datetime
import uuid
from sqlalchemy import String, ForeignKey, DateTime, Text, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDPrimaryKeyMixin, TimeStampedModelMixin


class AgentRun(Base, UUIDPrimaryKeyMixin, TimeStampedModelMixin):
    """
    AgentRun entity model. Logs telemetry regarding asynchronous agent executions,
    inputs, outputs, and failures.
    """
    __tablename__ = "agent_runs"

    company_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("companies.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    workflow_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workflows.id", ondelete="RESTRICT"),
        nullable=True,
        index=True
    )
    agent_name: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)
    input_parameters: Mapped[dict] = mapped_column(JSONB, nullable=True)
    output_results: Mapped[dict] = mapped_column(JSONB, nullable=True)
    error_message: Mapped[str] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    company: Mapped["Company"] = relationship("Company", back_populates="agent_runs")
    workflow: Mapped["Workflow"] = relationship("Workflow", back_populates="agent_runs")

    # Table Indexes
    __table_args__ = (
        Index("idx_agent_runs_company_status", "company_id", "status"),
    )
