import logging
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.agent import AgentRun
from app.models.invoice import Invoice
from app.services.agents import compiled_graph

logger = logging.getLogger(__name__)

router = APIRouter()


class AgentProcessRequest(BaseModel):
    """
    Schema requesting autonomous processing of an ingested document transaction.
    """
    company_id: str = Field(..., description="The tenant UUID.")
    invoice_id: str = Field(..., description="The target invoice UUID.")


@router.post("/process", status_code=status.HTTP_200_OK)
async def process_financial_transaction(
    request: AgentProcessRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Gateway endpoint executing the multi-agent LangGraph orchestration pipeline.
    Assembles initial state, triggers graph nodes, records trace checkpoints, and commits outputs.
    """
    try:
        tenant_uuid = uuid.UUID(request.company_id)
        invoice_uuid = uuid.UUID(request.invoice_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid UUID format for company_id or invoice_id."
        )

    # 1. Fetch document invoice record
    result = await db.execute(select(Invoice).where(Invoice.id == invoice_uuid))
    invoice = result.scalar_one_or_none()
    
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice document record not found."
        )

    # 2. Persist parent agent_runs audit header
    agent_run = AgentRun(
        company_id=tenant_uuid,
        agent_name="FinanceOperationsOrchestrator",
        status="running",
        input_parameters={"invoice_id": str(invoice_uuid)},
        output_results={}
    )
    db.add(agent_run)
    await db.flush()
    agent_run_id = str(agent_run.id)

    # 3. Assemble LangGraph execution state
    initial_state = {
        "invoice_id": str(invoice_uuid),
        "company_id": str(tenant_uuid),
        "plan": [],
        "current_step_index": 0,
        "ocr_raw_text": "",
        "extracted_data": {},
        "validation_results": {},
        "research_context": "",
        "financial_analysis": {},
        "risk_assessment": {},
        "generated_report": "",
        "errors": [],
        "agent_run_id": agent_run_id
    }

    # 4. Invoke LangGraph multi-agent pipeline
    try:
        # Run graph execution synchronously inside endpoint thread context
        final_state = compiled_graph.invoke(initial_state)
    except Exception as e:
        logger.error(f"LangGraph execution crashed: {str(e)}", exc_info=True)
        agent_run.status = "failed"
        invoice.status = "failed"
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent graph execution aborted due to system crash: {str(e)}"
        )

    # 5. Evaluate final execution state & persist updates
    if final_state.get("errors"):
        agent_run.status = "failed"
        invoice.status = "failed"
        message = "Autonomous pipeline completed with validation or processing errors."
    else:
        # Update invoice parameters from extracted context
        extracted = final_state.get("extracted_data", {})
        invoice.invoice_number = extracted.get("invoice_number")
        invoice.total_amount = extracted.get("total_amount")
        invoice.ocr_raw_text = final_state.get("generated_report")
        invoice.status = "completed"
        
        agent_run.status = "completed"
        message = "Autonomous pipeline execution finished successfully."

    # Save final tracing aggregates
    agent_run.output_results["final_report"] = final_state.get("generated_report")
    await db.commit()

    return {
        "status": agent_run.status,
        "message": message,
        "agent_run_id": agent_run_id,
        "report": final_state.get("generated_report")
    }
