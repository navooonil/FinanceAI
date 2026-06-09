import uuid
from sqlalchemy import String, Boolean, ForeignKey, Text, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDPrimaryKeyMixin, TimeStampedModelMixin


class Workflow(Base, UUIDPrimaryKeyMixin, TimeStampedModelMixin):
    """
    Workflow entity model. Stores user-defined pipeline graphs (triggers, conditions, steps)
    executed by automated financial agents.
    """
    __tablename__ = "workflows"

    company_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("companies.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    trigger_type: Mapped[str] = mapped_column(String(100), nullable=False)
    definition: Mapped[dict] = mapped_column(JSONB, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    company: Mapped["Company"] = relationship("Company", back_populates="workflows")
    agent_runs: Mapped[list["AgentRun"]] = relationship("AgentRun", back_populates="workflow")

    # Composite Index
    __table_args__ = (
        Index("idx_workflows_company_is_active", "company_id", "is_active"),
    )
