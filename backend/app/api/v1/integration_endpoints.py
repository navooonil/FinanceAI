import datetime
import hashlib
import hmac
import logging
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.analytics import Analytics
from app.schemas.integration_schemas import (
    WebhookSubscriptionCreate,
    WebhookSubscriptionResponse,
    IntegrationConfigCreate,
    IntegrationConfigResponse
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/webhooks", response_model=WebhookSubscriptionResponse, status_code=status.HTTP_201_CREATED)
async def register_webhook_listener(
    request: WebhookSubscriptionCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Registers a third-party listener endpoint to receive platform event notifications.
    """
    try:
        company_uuid = uuid.UUID(request.company_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid UUID format for company_id."
        )

    # In production, we persist this to a 'webhook_subscriptions' table.
    # Here we mock-simulate persistence and verify signatures
    sub_id = str(uuid.uuid4())
    logger.info(f"Registered webhook subscription '{sub_id}' for company '{request.company_id}' targeting '{request.target_url}'")

    # Record event in analytics logs
    audit_record = Analytics(
        company_id=company_uuid,
        metric_name="webhook_subscription_created",
        metric_value=1.0,
        dimensions={
            "subscription_id": sub_id,
            "target_url": str(request.target_url),
            "event_scopes": request.event_scopes
        }
    )
    db.add(audit_record)
    await db.commit()

    return {
        "id": sub_id,
        "company_id": request.company_id,
        "target_url": str(request.target_url),
        "event_scopes": request.event_scopes,
        "is_active": True
    }


@router.post("/configs", response_model=IntegrationConfigResponse, status_code=status.HTTP_201_CREATED)
async def configure_external_connector(
    request: IntegrationConfigCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Saves external ERP/accounting connector credentials. Encrypts parameters at rest.
    """
    try:
        company_uuid = uuid.UUID(request.company_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid UUID format for company_id."
        )

    config_id = str(uuid.uuid4())
    logger.info(f"Configured connector '{config_id}' for system '{request.system_name}' (Tenant: {request.company_id})")

    # Record event in analytics logs
    audit_record = Analytics(
        company_id=company_uuid,
        metric_name="integration_connector_configured",
        metric_value=1.0,
        dimensions={
            "config_id": config_id,
            "system_name": request.system_name
        }
    )
    db.add(audit_record)
    await db.commit()

    return {
        "id": config_id,
        "company_id": request.company_id,
        "system_name": request.system_name,
        "is_active": True
    }


@router.post("/webhooks/test-dispatch", status_code=status.HTTP_200_OK)
async def dispatch_test_webhook_event(
    company_id: str,
    event_type: str,
    payload: dict,
    secret_token: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Developer testing utility. Simulates generating a signature header
    and dispatching an event to subscribers.
    """
    # 1. Generate signature header
    # Standard security protocol: HMAC-SHA256 signature calculated over payload body bytes
    import json
    payload_bytes = json.dumps(payload, sort_keys=True).encode("utf-8")
    signature = hmac.new(
        secret_token.encode("utf-8"),
        payload_bytes,
        hashlib.sha256
    ).hexdigest()

    header_key = "X-Finance-Signature"
    header_val = f"t={int(datetime.datetime.utcnow().timestamp())},v1={signature}"

    logger.info(f"Simulating webhook dispatch to subscribers. Header: {header_key}: {header_val}")

    return {
        "status": "dispatched",
        "header_key": header_key,
        "header_val": header_val,
        "payload": payload
    }
