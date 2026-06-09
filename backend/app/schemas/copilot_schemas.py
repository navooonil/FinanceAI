from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.schemas.base import APIResponseBase


class CopilotChatRequestSchema(BaseModel):
    """
    Standard request payload for interacting with the AI Finance Copilot.
    """
    company_id: str = Field(..., description="Tenant UUID identifier.")
    user_id: Optional[str] = Field(None, description="Requesting User UUID identifier.")
    session_id: str = Field(..., description="Conversational session UUID tracker.")
    message: str = Field(..., description="Natural language input message.")


class CopilotChatResponseSchema(APIResponseBase):
    """
    Structured output response returning formatted context, resolved intent, and DB metadata.
    """
    answer: str = Field(..., description="Natural language answer text.")
    session_id: str = Field(..., description="Session UUID tracker.")
    intent: str = Field(..., description="Classified intent key (e.g. 'overdue_invoices').")
    citations: List[str] = Field(default_factory=list, description="Citations of documents or tables referenced.")
    structured_data: Optional[Dict[str, Any]] = Field(None, description="Metadata JSON payload returning raw values for rendering tables/charts.")
