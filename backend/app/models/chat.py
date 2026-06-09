import uuid
from sqlalchemy import String, ForeignKey, Text, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDPrimaryKeyMixin, TimeStampedModelMixin


class ChatHistory(Base, UUIDPrimaryKeyMixin, TimeStampedModelMixin):
    """
    ChatHistory entity model. Persists conversational lines for RAG sessions
    associated with users and tenants.
    """
    __tablename__ = "chat_history"

    company_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("companies.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    session_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_info: Mapped[dict] = mapped_column(JSONB, nullable=True)

    # Relationships
    company: Mapped["Company"] = relationship("Company", back_populates="chat_histories")
    user: Mapped["User"] = relationship("User", back_populates="chat_histories")

    # Composite Index to speed up conversation loading
    __table_args__ = (
        Index("idx_chat_history_company_session_created", "company_id", "session_id", "created_at"),
    )
