import asyncio
import concurrent.futures
import datetime
import logging
import time
import uuid
from typing import TypedDict, List, Dict, Any, Optional

from sqlalchemy import select
from tenacity import retry, stop_after_attempt, wait_exponential

from app.database import AsyncSessionLocal
from app.models.agent import AgentRun
from app.models.invoice import Invoice

# LangGraph imports
from langgraph.graph import StateGraph, END

logger = logging.getLogger(__name__)


def run_async(coro):
    """
    Utility helper to execute an asynchronous coroutine inside a synchronous node context.
    Safely handles both cases when an event loop is already running in the current thread and when not.
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(asyncio.run, coro)
            return future.result()
    else:
        return asyncio.run(coro)


class FinanceOpsState(TypedDict):
    """
    TypedDict representing the global shared memory state across the multi-agent graph.
    """
    invoice_id: str
    company_id: str
    plan: List[str]
    current_step_index: int
    ocr_raw_text: str
    extracted_data: Dict[str, Any]
    validation_results: Dict[str, Any]
    research_context: str
    financial_analysis: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    generated_report: str
    errors: List[str]
    agent_run_id: str


# ==========================================================
# Tracing Helper: Updates PostgreSQL Audit Log
# ==========================================================
async def trace_agent_execution_step(
    agent_run_id: str,
    node_name: str,
    status: str,
    outputs: Dict[str, Any]
) -> None:
    """
    Records trace telemetry for each agent node execution inside agent_runs table.
    """
    run_uuid = uuid.UUID(agent_run_id)
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(AgentRun).where(AgentRun.id == run_uuid))
        agent_run = result.scalar_one_or_none()
        if agent_run:
            # Append step trace parameters inside output_results JSONB column
            current_results = agent_run.output_results or {}
            current_results[node_name] = {
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                "status": status,
                "data": outputs
            }
            agent_run.output_results = current_results
            await session.commit()
            logger.info(f"Trace recorded in database for agent step '{node_name}' (Run: {agent_run_id})")


# ==========================================================
# Agent Node Handlers
# ==========================================================

def planner_node(state: FinanceOpsState) -> Dict[str, Any]:
    """
    Planner Agent: Analyzes the target transaction and establishes
    a customized execution plan sequence.
    """
    start_time = time.time()
    logger.info(f"Planner Agent starting step allocation...")
    
    # Establish sequential execution steps
    plan = ["ocr", "validation", "research", "finance_analysis", "risk_assessment", "report_generation"]
    
    outputs = {
        "plan": plan,
        "current_step_index": 0,
        "processing_time_ms": int((time.time() - start_time) * 1000)
    }
    
    # Dispatches database trace asynchronously (synchronous execution wrapper helper)
    run_async(trace_agent_execution_step(state["agent_run_id"], "planner", "completed", outputs))
    
    return outputs


def ocr_node(state: FinanceOpsState) -> Dict[str, Any]:
    """
    OCR Agent: Extracts document metadata and text from store.
    """
    start_time = time.time()
    logger.info(f"OCR Agent starting extraction pipeline...")
    
    # Simulate extraction
    ocr_raw = "Vendor: TechParts Corp\nSubtotal: $2000.00\nTax: $200.00\nTotal: $2200.00"
    extracted = {
        "vendor_name": "TechParts Corp",
        "subtotal": 2000.00,
        "tax_amount": 200.00,
        "total_amount": 2200.00,
        "invoice_number": "INV-2026-88"
    }
    
    outputs = {
        "ocr_raw_text": ocr_raw,
        "extracted_data": extracted,
        "current_step_index": state.get("current_step_index", 0) + 1,
        "processing_time_ms": int((time.time() - start_time) * 1000)
    }
    
    run_async(trace_agent_execution_step(state["agent_run_id"], "ocr", "completed", outputs))
    
    return outputs


def validation_node(state: FinanceOpsState) -> Dict[str, Any]:
    """
    Validation Agent: Performs strict mathematical checksum checks on extracted invoice data.
    """
    start_time = time.time()
    logger.info(f"Validation Agent executing checksum verifications...")
    
    extracted = state.get("extracted_data", {})
    subtotal = extracted.get("subtotal", 0.0)
    tax = extracted.get("tax_amount", 0.0)
    total = extracted.get("total_amount", 0.0)
    
    checksum_passed = round(subtotal + tax, 2) == round(total, 2)
    
    validation_results = {
        "checksum_passed": checksum_passed,
        "subtotal_tax_sum": subtotal + tax,
        "recorded_total": total,
        "warnings": [] if checksum_passed else ["Mathematical checksum mismatch detected."]
    }
    
    outputs = {
        "validation_results": validation_results,
        "current_step_index": state.get("current_step_index", 0) + 1,
        "processing_time_ms": int((time.time() - start_time) * 1000)
    }
    
    run_async(trace_agent_execution_step(state["agent_run_id"], "validation", "completed", outputs))
    
    return outputs


def research_node(state: FinanceOpsState) -> Dict[str, Any]:
    """
    Research Agent: Queries knowledge stores / database for historical vendor information.
    """
    start_time = time.time()
    logger.info(f"Research Agent querying vendor metrics...")
    
    extracted = state.get("extracted_data", {})
    vendor = extracted.get("vendor_name", "Unknown")
    
    research_context = f"Vendor '{vendor}' is registered. Historical average invoice total is $1800. No active audit alerts."
    
    outputs = {
        "research_context": research_context,
        "current_step_index": state.get("current_step_index", 0) + 1,
        "processing_time_ms": int((time.time() - start_time) * 1000)
    }
    
    run_async(trace_agent_execution_step(state["agent_run_id"], "research", "completed", outputs))
    
    return outputs


def finance_analysis_node(state: FinanceOpsState) -> Dict[str, Any]:
    """
    Finance Analysis Agent: Reviews transactions against budget metrics.
    """
    start_time = time.time()
    logger.info(f"Finance Analysis Agent evaluating budget compliance...")
    
    extracted = state.get("extracted_data", {})
    total = extracted.get("total_amount", 0.0)
    
    # Simulate analysis
    analysis = {
        "budget_limit": 5000.00,
        "allocated_balance": 15000.00,
        "approved": total <= 5000.00,
        "notes": "Transaction falls within departmental budget thresholds."
    }
    
    outputs = {
        "financial_analysis": analysis,
        "current_step_index": state.get("current_step_index", 0) + 1,
        "processing_time_ms": int((time.time() - start_time) * 1000)
    }
    
    run_async(trace_agent_execution_step(state["agent_run_id"], "finance_analysis", "completed", outputs))
    
    return outputs


def risk_assessment_node(state: FinanceOpsState) -> Dict[str, Any]:
    """
    Risk Assessment Agent: Evaluates fraud indicators and records risk flags.
    """
    start_time = time.time()
    logger.info(f"Risk Assessment Agent calculating transaction fraud risks...")
    
    # Simulate analysis
    risk = {
        "risk_rating": "low",
        "fraud_score": 0.05,
        "compliance_check": "passed",
        "notes": "No duplicate invoice numbers or mismatched parameters found."
    }
    
    outputs = {
        "risk_assessment": risk,
        "current_step_index": state.get("current_step_index", 0) + 1,
        "processing_time_ms": int((time.time() - start_time) * 1000)
    }
    
    run_async(trace_agent_execution_step(state["agent_run_id"], "risk_assessment", "completed", outputs))
    
    return outputs


def report_generation_node(state: FinanceOpsState) -> Dict[str, Any]:
    """
    Report Generation Agent: Compiles all structured inputs into a grounded audit summary.
    """
    start_time = time.time()
    logger.info(f"Report Generation Agent compiling final audit file...")
    
    extracted = state.get("extracted_data", {})
    validation = state.get("validation_results", {})
    finance = state.get("financial_analysis", {})
    risk = state.get("risk_assessment", {})
    
    report = (
        f"--- FINANCIAL AUDIT REPORT ---\n"
        f"Invoice Ref: {extracted.get('invoice_number')}\n"
        f"Vendor: {extracted.get('vendor_name')}\n"
        f"Amount: ${extracted.get('total_amount')}\n"
        f"Checksum Validated: {validation.get('checksum_passed')}\n"
        f"Budget Status: Approved={finance.get('approved')}\n"
        f"Risk Profile: Rating={risk.get('risk_rating')}\n"
        f"Audit Complete. Transaction recommended for payment."
    )
    
    outputs = {
        "generated_report": report,
        "current_step_index": state.get("current_step_index", 0) + 1,
        "processing_time_ms": int((time.time() - start_time) * 1000)
    }
    
    run_async(trace_agent_execution_step(state["agent_run_id"], "report_generation", "completed", outputs))
    
    return outputs


# ==========================================================
# Graph Definition & Routing Layout
# ==========================================================

# Initialize state graph structure
workflow = StateGraph(FinanceOpsState)

# Add node configurations
workflow.add_node("planner", planner_node)
workflow.add_node("ocr", ocr_node)
workflow.add_node("validation", validation_node)
workflow.add_node("research", research_node)
workflow.add_node("finance_analysis", finance_analysis_node)
workflow.add_node("risk_assessment", risk_assessment_node)
workflow.add_node("report_generation", report_generation_node)

# Set Entrypoint
workflow.set_entry_point("planner")


def step_router(state: FinanceOpsState) -> str:
    """
    Router coordinating conditional edges transitions.
    Navigates sequentially through the planned steps, routing to END when complete,
    or immediately aborting to END if critical errors are encountered.
    """
    if state.get("errors"):
        logger.error(f"Critical execution errors present in graph state: {state['errors']}. Ending graph.")
        return END

    plan = state.get("plan", [])
    index = state.get("current_step_index", 0)

    if index >= len(plan):
        return END

    # Fetch next scheduled node name
    next_node = plan[index]
    
    logger.info(f"Router routing to next step: '{next_node}' (Step {index + 1}/{len(plan)})")
    return next_node


# Link conditional routing maps from each executor node back to router
# LangGraph evaluates router output to choose the next node or exit the graph
workflow.add_conditional_edges("planner", step_router, {
    "ocr": "ocr",
    "validation": "validation",
    "research": "research",
    "finance_analysis": "finance_analysis",
    "risk_assessment": "risk_assessment",
    "report_generation": "report_generation",
    END: END
})

for node in ["ocr", "validation", "research", "finance_analysis", "risk_assessment", "report_generation"]:
    workflow.add_conditional_edges(node, step_router, {
        "ocr": "ocr",
        "validation": "validation",
        "research": "research",
        "finance_analysis": "finance_analysis",
        "risk_assessment": "risk_assessment",
        "report_generation": "report_generation",
        END: END
    })

# Compile state graph
compiled_graph = workflow.compile()
