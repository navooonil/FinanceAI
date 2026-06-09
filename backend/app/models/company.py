from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDPrimaryKeyMixin, TimeStampedModelMixin


class Company(Base, UUIDPrimaryKeyMixin, TimeStampedModelMixin):
    """
    Company (Tenant) entity model.
    Encapsulates a distinct tenant in the multi-tenant SaaS environment.
    All business data must be scoped to a company.
    """
    __tablename__ = "companies"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    domain: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships (Using string-based types to avoid circular imports)
    users: Mapped[list["User"]] = relationship(
        "User", back_populates="company", cascade="all, delete-orphan"
    )
    vendors: Mapped[list["Vendor"]] = relationship(
        "Vendor", back_populates="company", cascade="all, delete-orphan"
    )
    invoices: Mapped[list["Invoice"]] = relationship(
        "Invoice", back_populates="company", cascade="all, delete-orphan"
    )
    workflows: Mapped[list["Workflow"]] = relationship(
        "Workflow", back_populates="company", cascade="all, delete-orphan"
    )
    reports: Mapped[list["Report"]] = relationship(
        "Report", back_populates="company", cascade="all, delete-orphan"
    )
    agent_runs: Mapped[list["AgentRun"]] = relationship(
        "AgentRun", back_populates="company", cascade="all, delete-orphan"
    )
    chat_histories: Mapped[list["ChatHistory"]] = relationship(
        "ChatHistory", back_populates="company", cascade="all, delete-orphan"
    )
    analytics_records: Mapped[list["Analytics"]] = relationship(
        "Analytics", back_populates="company", cascade="all, delete-orphan"
    )
    business_metrics: Mapped[list["BusinessMetric"]] = relationship(
        "BusinessMetric", back_populates="company", cascade="all, delete-orphan"
    )
    tracked_decisions: Mapped[list["Decision"]] = relationship(
        "Decision", back_populates="company", cascade="all, delete-orphan"
    )

