import datetime
import math
import logging
from typing import List, Dict, Any, Tuple, Optional
import uuid
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.invoice import Invoice
from app.models.vendor import Vendor
from app.models.analytics import Analytics

logger = logging.getLogger(__name__)


def levenshtein_similarity(s1: str, s2: str) -> float:
    """
    Computes Levenshtein similarity ratio between two strings.
    Used for fuzzy duplicate invoice number checks.
    """
    if not s1 or not s2:
        return 0.0
    s1, s2 = s1.strip().lower(), s2.strip().lower()
    if s1 == s2:
        return 1.0
        
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
        
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1]) + 1
                
    distance = dp[m][n]
    max_len = max(m, n)
    if max_len == 0:
        return 1.0
    return 1.0 - (distance / max_len)


class AnomalyDetector:
    """
    Statistical and ML-based anomaly detector evaluating transaction amounts and timing.
    """
    @staticmethod
    async def analyze_invoice(session: AsyncSession, invoice: Invoice) -> Tuple[bool, float, List[str]]:
        """
        Runs Z-Score, IQR, and Mock Isolation Forest anomalies on a given invoice.
        """
        is_anomaly = False
        reasons = []
        scores = []
        
        # 1. Fetch vendor history
        stmt = (
            select(Invoice.total_amount)
            .where(
                Invoice.vendor_id == invoice.vendor_id,
                Invoice.company_id == invoice.company_id,
                Invoice.id != invoice.id,
                Invoice.status == "completed"
            )
        )
        res = await session.execute(stmt)
        history = [float(row[0]) for row in res.all() if row[0] is not None]
        
        current_amount = float(invoice.total_amount) if invoice.total_amount is not None else 0.0

        if len(history) >= 3:
            # Z-Score computation
            mean_amount = sum(history) / len(history)
            variance = sum((x - mean_amount) ** 2 for x in history) / len(history)
            std_dev = math.sqrt(variance)
            
            if std_dev > 0:
                z_score = abs(current_amount - mean_amount) / std_dev
                z_score_flag = z_score > 2.5
                scores.append(min(1.0, z_score / 5.0))
                if z_score_flag:
                    is_anomaly = True
                    reasons.append(
                        f"Amount ${current_amount:.2f} is an outlier for vendor (Z-Score: {z_score:.2f}, "
                        f"historical mean: ${mean_amount:.2f}, std_dev: ${std_dev:.2f})"
                    )
            else:
                if current_amount != mean_amount:
                    is_anomaly = True
                    scores.append(1.0)
                    reasons.append(f"Amount ${current_amount:.2f} deviates from historical constant of ${mean_amount:.2f}")
                else:
                    scores.append(0.0)

            # IQR computation
            sorted_history = sorted(history)
            q1_idx = int(len(sorted_history) * 0.25)
            q3_idx = int(len(sorted_history) * 0.75)
            q1 = sorted_history[q1_idx]
            q3 = sorted_history[q3_idx]
            iqr = q3 - q1
            iqr_lower = q1 - 1.5 * iqr
            iqr_upper = q3 + 1.5 * iqr
            
            if current_amount < iqr_lower or current_amount > iqr_upper:
                is_anomaly = True
                reasons.append(
                    f"Amount ${current_amount:.2f} falls outside non-Gaussian IQR range "
                    f"[${iqr_lower:.2f}, ${iqr_upper:.2f}]"
                )
        else:
            # Not enough data for Z-score; perform global heuristic check
            if current_amount > 10000.0:
                is_anomaly = True
                scores.append(0.75)
                reasons.append(f"Amount ${current_amount:.2f} triggers high global spend threshold flag (> $10k)")
            else:
                scores.append(0.1)

        # 2. ML Mock Isolation Forest (evaluating day of week combined with high amount values)
        issue_date = invoice.issue_date or datetime.date.today()
        day_of_week = issue_date.weekday()  # 5=Saturday, 6=Sunday
        if day_of_week >= 5 and current_amount > 500.0:
            is_anomaly = True
            scores.append(0.8)
            reasons.append(f"Transaction dated on a weekend ({issue_date.strftime('%A')}) with high total spend")
            
        final_score = max(scores) if scores else 0.0
        return is_anomaly, final_score, reasons


class DuplicateDetector:
    """
    Fuzzy and exact duplicate invoice detector.
    """
    @staticmethod
    async def find_duplicates(session: AsyncSession, invoice: Invoice) -> Tuple[bool, Optional[str], Optional[str], List[str]]:
        """
        Scans DB for matching parameters. Returns duplicate status, matching invoice UUID, match type, and reasons.
        """
        is_duplicate = False
        matching_id = None
        match_type = None
        reasons = []

        if not invoice.vendor_id:
            return is_duplicate, matching_id, match_type, reasons

        # Fetch candidate invoices from same vendor/company
        stmt = (
            select(Invoice)
            .where(
                Invoice.vendor_id == invoice.vendor_id,
                Invoice.company_id == invoice.company_id,
                Invoice.id != invoice.id,
                Invoice.status != "failed"
            )
        )
        res = await session.execute(stmt)
        candidates = [row[0] for row in res.all()]

        current_num = invoice.invoice_number or ""
        current_amount = float(invoice.total_amount) if invoice.total_amount is not None else 0.0
        current_date = invoice.issue_date

        for cand in candidates:
            cand_num = cand.invoice_number or ""
            cand_amount = float(cand.total_amount) if cand.total_amount is not None else 0.0
            cand_date = cand.issue_date

            # 1. Exact Invoice Number match
            if current_num and cand_num and current_num.strip().lower() == cand_num.strip().lower():
                return True, str(cand.id), "exact_number", [
                    f"Exact duplicate invoice number '{current_num}' already exists (Invoice ID: {cand.id})"
                ]

            # 2. Exact Amount + Issue Date match
            if current_amount > 0 and cand_amount > 0 and current_amount == cand_amount and current_date == cand_date:
                return True, str(cand.id), "exact_amount_date", [
                    f"Matching invoice with identical amount (${current_amount:.2f}) and date ({current_date}) exists (Invoice ID: {cand.id})"
                ]

            # 3. Fuzzy invoice number check (Levenshtein distance similarity)
            if current_num and cand_num:
                sim = levenshtein_similarity(current_num, cand_num)
                if sim > 0.85:
                    is_duplicate = True
                    matching_id = str(cand.id)
                    match_type = "fuzzy_number"
                    reasons.append(
                        f"Fuzzy duplicate invoice number variation found: '{current_num}' matches '{cand_num}' "
                        f"(Similarity score: {sim:.2f})"
                    )

            # 4. Same amount with close date window (e.g. within 5 days)
            if current_amount > 0 and cand_amount == current_amount and current_date and cand_date:
                date_diff = abs((current_date - cand_date).days)
                if date_diff <= 5:
                    is_duplicate = True
                    matching_id = str(cand.id)
                    match_type = "close_date_proximity"
                    reasons.append(
                        f"Duplicate transaction amount of ${current_amount:.2f} found within close proximity window "
                        f"({date_diff} days difference, date: {cand_date})"
                    )

        return is_duplicate, matching_id, match_type, reasons


class VendorRiskScorer:
    """
    Evaluates suppliers based on data ingestion, anomaly, and duplicate metrics.
    """
    @staticmethod
    async def compute_vendor_risk(session: AsyncSession, vendor_id: uuid.UUID, company_id: uuid.UUID) -> Dict[str, Any]:
        """
        Compiles risk grades and scores.
        """
        # Fetch vendor model to get name
        vendor_res = await session.execute(select(Vendor).where(Vendor.id == vendor_id))
        vendor = vendor_res.scalar_one_or_none()
        vendor_name = vendor.name if vendor else "Unknown"

        # Fetch historical invoices for the vendor
        stmt = (
            select(Invoice)
            .where(
                Invoice.vendor_id == vendor_id,
                Invoice.company_id == company_id
            )
        )
        res = await session.execute(stmt)
        invoices = [row[0] for row in res.all()]

        total_invoices = len(invoices)
        if total_invoices == 0:
            return {
                "vendor_id": str(vendor_id),
                "vendor_name": vendor_name,
                "risk_grade": "A",
                "risk_score": 0.0,
                "risk_factors": [{"factor": "no_history", "description": "No invoices recorded for this supplier."}],
                "confidence_score": 0.5
            }

        checksum_failures = 0
        duplicate_occurrences = 0
        outlier_occurrences = 0

        # We will query the analytics records for anomaly flags or compute inline
        for inv in invoices:
            # Check if invoice is pending_review due to confidence score
            if inv.status == "pending_review":
                checksum_failures += 1
            
            # Simple heuristic flags for risk compilation
            if inv.total_amount and float(inv.total_amount) > 10000.0:
                outlier_occurrences += 1

        # Check for actual duplicate runs registered in database
        dup_stmt = (
            select(Analytics.dimensions)
            .where(
                Analytics.company_id == company_id,
                Analytics.metric_name == "invoice_duplicate"
            )
        )
        dup_res = await session.execute(dup_stmt)
        for row in dup_res.all():
            dim = row[0] or {}
            # If the duplicate check belongs to one of our invoices and was flagged True
            inv_ids = [str(i.id) for i in invoices]
            if dim.get("invoice_id") in inv_ids and dim.get("is_duplicate") is True:
                duplicate_occurrences += 1

        # Check for anomalies registered in database
        anom_stmt = (
            select(Analytics.dimensions)
            .where(
                Analytics.company_id == company_id,
                Analytics.metric_name == "invoice_anomaly"
            )
        )
        anom_res = await session.execute(anom_stmt)
        for row in anom_res.all():
            dim = row[0] or {}
            inv_ids = [str(i.id) for i in invoices]
            if dim.get("invoice_id") in inv_ids and dim.get("is_anomaly") is True:
                outlier_occurrences += 1

        # Scoring weights
        checksum_rate = checksum_failures / total_invoices
        duplicate_rate = duplicate_occurrences / total_invoices
        outlier_rate = outlier_occurrences / total_invoices

        # Compute numeric score: 0 (safe) to 100 (high risk)
        risk_score = 0.0
        risk_factors = []

        if checksum_rate > 0.2:
            risk_score += 25.0
            risk_factors.append({
                "factor": "high_checksum_failure_rate",
                "description": f"{checksum_rate * 100:.1f}% of invoices have failed parser checks / checksums."
            })
        if duplicate_rate > 0.0:
            risk_score += 40.0
            risk_factors.append({
                "factor": "duplicate_invoice_history",
                "description": f"Duplicate invoice submissions detected in vendor history ({duplicate_occurrences} found)."
            })
        if outlier_rate > 0.3:
            risk_score += 20.0
            risk_factors.append({
                "factor": "high_outlier_spend_frequency",
                "description": f"Frequently submits invoices flagged as amount anomalies ({outlier_occurrences} flags)."
            })

        # Cap score at 100
        risk_score = min(100.0, risk_score)

        # Grade boundaries
        if risk_score < 20.0:
            risk_grade = "A"
        elif risk_score < 40.0:
            risk_grade = "B"
        elif risk_score < 60.0:
            risk_grade = "C"
        elif risk_score < 80.0:
            risk_grade = "D"
        else:
            risk_grade = "F"

        confidence = 0.9 if total_invoices >= 5 else 0.7

        return {
            "vendor_id": str(vendor_id),
            "vendor_name": vendor_name,
            "risk_grade": risk_grade,
            "risk_score": risk_score,
            "risk_factors": risk_factors,
            "confidence_score": confidence
        }


class TrendAnalyzer:
    """
    Computes aggregated period-over-period spend patterns.
    """
    @staticmethod
    async def get_spend_trends(session: AsyncSession, company_id: uuid.UUID) -> Dict[str, Any]:
        """
        Assembles list of monthly aggregates and growth margins.
        """
        # Fetch completed invoices for the company
        stmt = (
            select(Invoice)
            .where(
                Invoice.company_id == company_id,
                Invoice.status == "completed"
            )
            .order_by(Invoice.issue_date.asc())
        )
        res = await session.execute(stmt)
        invoices = [row[0] for row in res.all()]

        # Group amounts by YYYY-MM
        monthly_spend: Dict[str, Tuple[float, int]] = {}
        for inv in invoices:
            date_val = inv.issue_date or datetime.date.today()
            period = date_val.strftime("%Y-%m")
            amount = float(inv.total_amount) if inv.total_amount is not None else 0.0
            
            curr_spend, curr_count = monthly_spend.get(period, (0.0, 0))
            monthly_spend[period] = (curr_spend + amount, curr_count + 1)

        # Sort periods chronologically
        sorted_periods = sorted(monthly_spend.keys())
        trends = []
        
        for idx, period in enumerate(sorted_periods):
            total_spend, count = monthly_spend[period]
            mom_change = 0.0
            if idx > 0:
                prev_period = sorted_periods[idx - 1]
                prev_spend, _ = monthly_spend[prev_period]
                if prev_spend > 0:
                    mom_change = ((total_spend - prev_spend) / prev_spend) * 100.0

            trends.append({
                "period": period,
                "total_spend": total_spend,
                "mom_percent_change": mom_change,
                "invoice_count": count
            })

        # Calculate overall growth
        overall_growth = 0.0
        if len(trends) >= 2:
            first = trends[0]["total_spend"]
            last = trends[-1]["total_spend"]
            if first > 0:
                overall_growth = ((last - first) / first) * 100.0

        return {
            "company_id": str(company_id),
            "overall_growth_rate": overall_growth,
            "trends": trends
        }


class PaymentPrioritizer:
    """
    Evaluates early payment discount urgency combined with counterparty risk rankings.
    """
    @staticmethod
    async def get_payment_priorities(session: AsyncSession, company_id: uuid.UUID) -> Dict[str, Any]:
        """
        Prioritizes all unpaid invoices.
        """
        # Fetch unpaid invoices (status could be completed, pending_review, or pending_ocr, but unpaid)
        # For this logic, we will select completed/pending_review invoices that are not paid.
        # Since we don't have a paid column in invoices, we filter by status in ['completed', 'pending_review']
        # to identify active records that need cash operations.
        stmt = (
            select(Invoice)
            .where(
                Invoice.company_id == company_id,
                Invoice.status.in_(["completed", "pending_review"])
            )
        )
        res = await session.execute(stmt)
        invoices = [row[0] for row in res.all()]

        today = datetime.date.today()
        queue_items = []

        for inv in invoices:
            vendor_res = await session.execute(select(Vendor).where(Vendor.id == inv.vendor_id))
            vendor = vendor_res.scalar_one_or_none()
            vendor_name = vendor.name if vendor else "Unknown"

            # Determine due date proximity
            due_date = inv.due_date or (today + datetime.timedelta(days=30))
            days_to_due = (due_date - today).days

            # Early dynamic discount check
            # We mock discounts: e.g. if due_date is > 10 days out, it's eligible
            discount_available = days_to_due > 10

            # Fetch vendor risk factor
            risk_grade = "A"
            if inv.vendor_id:
                risk_info = await VendorRiskScorer.compute_vendor_risk(session, inv.vendor_id, company_id)
                risk_grade = risk_info.get("risk_grade", "A")

            # Urgency Score Formula
            # Base score derived from due date proximity (maximum of 30 points if close to or past due)
            base_urgency = max(0.0, 30.0 - float(days_to_due))
            
            # Plus 15 points if early discount is active
            discount_bonus = 15.0 if discount_available else 0.0
            
            # Less 20 points penalty if supplier has operational warnings (risk grade D or F)
            risk_penalty = -20.0 if risk_grade in ["D", "F"] else 0.0
            
            urgency_score = base_urgency + discount_bonus + risk_penalty

            # Final payment recommendation: recommend paying early if high score
            payment_recommended = urgency_score >= 25.0

            queue_items.append({
                "invoice_id": str(inv.id),
                "invoice_number": inv.invoice_number,
                "vendor_name": vendor_name,
                "total_amount": float(inv.total_amount) if inv.total_amount is not None else 0.0,
                "due_date": due_date,
                "urgency_score": urgency_score,
                "discount_available": discount_available,
                "payment_recommended": payment_recommended
            })

        # Sort queue items descending by urgency score
        queue_items.sort(key=lambda x: x["urgency_score"], reverse=True)

        return {
            "company_id": str(company_id),
            "queue": queue_items
        }
