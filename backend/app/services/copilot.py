import datetime
import logging
from typing import Any, Dict, List, Tuple, Optional
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat import ChatHistory
from app.models.invoice import Invoice
from app.models.vendor import Vendor
from app.services.financial_intelligence import VendorRiskScorer, TrendAnalyzer, PaymentPrioritizer
from app.services.rag import RAGService

logger = logging.getLogger(__name__)


class AICopilotService:
    """
    AI Finance Copilot Service. Integrates database data lookups,
    conversational history context memory, RAG fallback, and structured citations.
    """
    @staticmethod
    async def process_message(
        session: AsyncSession,
        company_id: str,
        user_id: Optional[str],
        session_id: str,
        message: str
    ) -> Dict[str, Any]:
        """
        Routes the natural language message, executes data calls, builds grounded answers,
        saves conversation exchange to chat_history, and returns structured outputs.
        """
        company_uuid = uuid.UUID(company_id)
        session_uuid = uuid.UUID(session_id)
        user_uuid = uuid.UUID(user_id) if user_id else None

        # 1. Load context memory: fetch last 5 messages from session history
        history_stmt = (
            select(ChatHistory)
            .where(
                ChatHistory.company_id == company_uuid,
                ChatHistory.session_id == session_uuid
            )
            .order_by(ChatHistory.created_at.desc())
            .limit(5)
        )
        history_res = await session.execute(history_stmt)
        # We read them in reverse order to feed them as context if needed
        chat_lines = list(reversed([row[0] for row in history_res.all()]))
        
        # 2. Intent Routing Heuristics
        msg_clean = message.strip().lower()
        
        if any(x in msg_clean for x in ["overdue", "unpaid", "outstanding", "late"]):
            intent = "overdue_invoices"
        elif any(x in msg_clean for x in ["risk", "risky", "danger", "anomalous"]):
            intent = "risky_vendors"
        elif any(x in msg_clean for x in ["trend", "trends", "spend", "growth"]):
            intent = "spending_trends"
        elif any(x in msg_clean for x in ["cashflow", "runway", "forecast", "predict"]):
            intent = "cashflow_projection"
        else:
            intent = "document_rag"

        # 3. Execute data lookups based on intent
        citations = []
        structured_data = None
        answer = ""

        if intent == "overdue_invoices":
            # Select outstanding invoices where due_date < today
            today = datetime.date.today()
            stmt = (
                select(Invoice)
                .where(
                    Invoice.company_id == company_uuid,
                    Invoice.status.in_(["completed", "pending_review"]),
                    Invoice.due_date < today
                )
            )
            res = await session.execute(stmt)
            invoices = [row[0] for row in res.all()]

            if not invoices:
                answer = "There are currently no overdue invoices registered for your company."
            else:
                lines = [
                    "| Invoice Ref | Supplier | Due Date | Amount | Status |",
                    "| :--- | :--- | :--- | :--- | :--- |"
                ]
                for inv in invoices:
                    vendor_name = "Unknown Vendor"
                    if inv.vendor_id:
                        v_res = await session.execute(select(Vendor.name).where(Vendor.id == inv.vendor_id))
                        vendor_name = v_res.scalar_one_or_none() or "Unknown Vendor"
                    lines.append(
                        f"| {inv.invoice_number or 'N/A'} | {vendor_name} | {inv.due_date} | "
                        f"${inv.total_amount:.2f} | {inv.status} |"
                    )
                answer = "Here are the overdue invoices detected on your ledger:\n\n" + "\n".join(lines)

            citations = ["Database (invoices table)"]
            structured_data = {
                "overdue_invoices": [
                    {
                        "invoice_id": str(i.id),
                        "invoice_number": i.invoice_number,
                        "amount": float(i.total_amount) if i.total_amount is not None else 0.0,
                        "due_date": str(i.due_date)
                    }
                    for i in invoices
                ]
            }

        elif intent == "risky_vendors":
            # Fetch all vendor IDs invoiced
            stmt = select(Invoice.vendor_id).where(Invoice.company_id == company_uuid).distinct()
            res = await session.execute(stmt)
            vendor_ids = [row[0] for row in res.all() if row[0] is not None]

            reports = []
            for v_id in vendor_ids:
                risk_info = await VendorRiskScorer.compute_vendor_risk(session, v_id, company_uuid)
                if risk_info.get("risk_score", 0) > 20:
                    reports.append(risk_info)

            if not reports:
                answer = "All active counterparty vendors have an A risk rating profile."
            else:
                lines = [
                    "| Vendor | Grade | Score | Risk Factors |",
                    "| :--- | :--- | :--- | :--- |"
                ]
                for report in reports:
                    factors_str = "; ".join([x["description"] for x in report["risk_factors"]]) or "None"
                    lines.append(f"| {report['vendor_name']} | {report['risk_grade']} | {report['risk_score']:.1f} | {factors_str} |")
                answer = "Here is the risk matrix audit for your suppliers:\n\n" + "\n".join(lines)

            citations = ["Database (vendors table, analytics table)"]
            structured_data = {"risky_vendors": reports}

        elif intent == "spending_trends":
            trends_data = await TrendAnalyzer.get_spend_trends(session, company_uuid)
            
            if not trends_data.get("trends"):
                answer = "No spending trends available. Ingest more documents to establish history."
            else:
                lines = [
                    "| Period | Total Spend | MoM % Change | Invoice Count |",
                    "| :--- | :--- | :--- | :--- |"
                ]
                for item in trends_data["trends"]:
                    lines.append(f"| {item['period']} | ${item['total_spend']:.2f} | {item['mom_percent_change']:.1f}% | {item['invoice_count']} |")
                answer = f"Here is the monthly spending breakdown (Overall MoM Growth: {trends_data['overall_growth_rate']:.1f}%):\n\n" + "\n".join(lines)

            citations = ["Database (analytics table, invoices table)"]
            structured_data = trends_data

        elif intent == "cashflow_projection":
            trends_data = await TrendAnalyzer.get_spend_trends(session, company_uuid)
            
            # Fetch historic monthly averages
            if trends_data.get("trends"):
                avg_outflow = sum(x["total_spend"] for x in trends_data["trends"]) / len(trends_data["trends"])
            else:
                avg_outflow = 1000.00  # Default fallback benchmark

            priorities = await PaymentPrioritizer.get_payment_priorities(session, company_uuid)
            total_unpaid = sum(x["total_amount"] for x in priorities["queue"])

            # Forecast warning logic
            if total_unpaid > avg_outflow * 1.5:
                warning = f"WARNING: Outflow requirements are Z% ({((total_unpaid - avg_outflow)/avg_outflow)*100:.1f}%) higher than historical averages."
            else:
                warning = "Forecast: No cashflow runway shortages predicted."

            answer = (
                f"Projected outflow requirements over the next 30 days are **${total_unpaid:.2f}**.\n"
                f"Historical average monthly spend benchmark: **${avg_outflow:.2f}**.\n\n"
                f"{warning}"
            )
            citations = ["Database (invoices table, analytics table)"]
            structured_data = {
                "projected_outflow_30d": total_unpaid,
                "historical_monthly_avg": avg_outflow,
                "outflow_alert": total_unpaid > avg_outflow * 1.5
            }

        else:
            # Fallback to Document RAG
            rag_service = RAGService()
            rag_answer, chunks = rag_service.generate_chat_response(company_id, message)
            
            answer = rag_answer
            citations = list(set([x.document_id for x in chunks]))
            structured_data = {"retrieved_chunks": [x.model_dump() for x in chunks]}

        # 4. Save Chat exchange to chat_history database table
        user_line = ChatHistory(
            company_id=company_uuid,
            user_id=user_uuid,
            session_id=session_uuid,
            role="user",
            message=message,
            metadata_info={}
        )
        
        assistant_line = ChatHistory(
            company_id=company_uuid,
            user_id=user_uuid,
            session_id=session_uuid,
            role="assistant",
            message=answer,
            metadata_info={
                "intent": intent,
                "citations": citations,
                "structured_data": structured_data
            }
        )
        
        session.add(user_line)
        session.add(assistant_line)
        await session.commit()

        return {
            "answer": answer,
            "session_id": str(session_uuid),
            "intent": intent,
            "citations": citations,
            "structured_data": structured_data
        }
