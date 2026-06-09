from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, HttpUrl

from app.schemas.base import APIResponseBase


class WebhookSubscriptionCreate(BaseModel):
    """
    Payload schema for registering an external webhook listener endpoint.
    """
    company_id: str = Field(..., description="Tenant UUID context.")
    target_url: HttpUrl = Field(..., description="The subscriber's HTTP endpoint URL.")
    event_scopes: List[str] = Field(
        ...,
        description="Event names to subscribe to (e.g. ['invoice.completed', 'workflow.waiting_for_approval'])."
    )
    secret_token: str = Field(
        ...,
        min_length=16,
        description="Shared secret key to verify webhook signature header (HMAC-SHA256)."
    )


class WebhookSubscriptionResponse(APIResponseBase):
    """
    Response schema returning registered webhook listener details.
    """
    id: str = Field(..., description="Webhook subscription UUID.")
    company_id: str
    target_url: str
    event_scopes: List[str]
    is_active: bool


class IntegrationConfigCreate(BaseModel):
    """
    Payload to register external accounting/ERP system connection parameters.
    """
    company_id: str = Field(..., description="Tenant UUID context.")
    system_name: str = Field(..., description="ERP/Software system key (e.g. 'quickbooks', 'netsuite', 'slack').")
    auth_credentials: Dict[str, Any] = Field(
        ...,
        description="Access tokens or authentication credentials. Encrypted at rest."
    )


class IntegrationConfigResponse(APIResponseBase):
    """
    Response schema returning registered integration configurations.
    """
    id: str = Field(..., description="Integration configuration UUID.")
    company_id: str
    system_name: str
    is_active: bool
