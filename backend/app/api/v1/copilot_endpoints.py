import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.copilot_schemas import CopilotChatRequestSchema, CopilotChatResponseSchema
from app.services.copilot import AICopilotService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/chat", response_model=CopilotChatResponseSchema, status_code=status.HTTP_200_OK)
async def interact_with_finance_copilot(
    request: CopilotChatRequestSchema,
    db: AsyncSession = Depends(get_db)
):
    """
    Gateway endpoint for natural language queries against company financial data.
    Analyzes message query parameters, runs matching intents, and returns grounded answers.
    """
    try:
        response_payload = await AICopilotService.process_message(
            session=db,
            company_id=request.company_id,
            user_id=request.user_id,
            session_id=request.session_id,
            message=request.message
        )
        return response_payload
    except Exception as e:
        logger.error(f"Failed to process message inside Copilot: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Finance Copilot encountered an operational error: {str(e)}"
        )
