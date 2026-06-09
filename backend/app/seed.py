import asyncio
import datetime
import uuid
import logging
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app.seed")

from app.database import engine, AsyncSessionLocal
from app.models import (
    Base,
    Company,
    User,
    Vendor,
    Invoice,
    Workflow,
    Report,
    AgentRun,
    ChatHistory,
    Analytics,
    BusinessMetric,
    Decision
)

# Seed Constants matching useFinanceStore.ts hardcoded values
COMPANY_ID = uuid.UUID('4b6f12d5-e2bb-41a4-b0e6-5778a87b415a')
USER_ID = uuid.UUID('a9a3b68f-bfd2-430b-9dfb-cb784f18a211')
SESSION_ID = uuid.UUID('7d9b32c6-302a-436f-b2bb-b072c49925e0')

# Vendor IDs
VENDOR_APEX = uuid.UUID('11111111-1111-1111-1111-111111111111')
VENDOR_SENTRY = uuid.UUID('22222222-2222-2222-2222-222222222222')
VENDOR_ZAXIS = uuid.UUID('33333333-3333-3333-3333-333333333333')

# Workflow IDs
WF_RISK_GATE = uuid.UUID('e8a5b9b9-d2df-4221-872e-d009b4395d90')
WF_AUTO_APPROVE = uuid.UUID('1e8df1aa-617a-42c2-8419-4a00494cf0ad')


async def clean_database(session: AsyncSession):
    """
    Cleans database records associated with the company to allow clean, repeatable seeding.
    """
    logger.info("Cleaning existing tenant database records...")
    
    # Order of deletion to respect foreign keys
    await session.execute(delete(Decision).where(Decision.company_id == COMPANY_ID))
    await session.execute(delete(Analytics).where(Analytics.company_id == COMPANY_ID))
    await session.execute(delete(BusinessMetric).where(BusinessMetric.company_id == COMPANY_ID))
    await session.execute(delete(ChatHistory).where(ChatHistory.company_id == COMPANY_ID))
    await session.execute(delete(AgentRun).where(AgentRun.company_id == COMPANY_ID))
    await session.execute(delete(Report).where(Report.company_id == COMPANY_ID))
    await session.execute(delete(Invoice).where(Invoice.company_id == COMPANY_ID))
    await session.execute(delete(Workflow).where(Workflow.company_id == COMPANY_ID))
    await session.execute(delete(Vendor).where(Vendor.company_id == COMPANY_ID))
    await session.execute(delete(User).where(User.company_id == COMPANY_ID))
    await session.execute(delete(Company).where(Company.id == COMPANY_ID))
    await session.commit()
    logger.info("Database cleaned successfully.")


async def seed_data(session: AsyncSession):
    """
    Seeds mock dataset.
    """
    await clean_database(session)

    # 1. Create Company
    logger.info("Seeding Company...")
    company = Company(
        id=COMPANY_ID,
        name="Acme Global Corp",
        domain="acme-global.com",
        is_active=True
    )
    session.add(company)
    await session.flush()

    # 2. Create User
    logger.info("Seeding User...")
    user = User(
        id=USER_ID,
        company_id=COMPANY_ID,
        email="alex@acme-global.com",
        hashed_password="scrypt:32768:8:1$mocked_hash_value_for_demo",
        full_name="Alex Chen",
        role="admin",
        is_active=True
    )
    session.add(user)
    await session.flush()

    # 3. Create Vendors
    logger.info("Seeding Vendors...")
    vendors_data = [
        Vendor(
            id=VENDOR_APEX,
            company_id=COMPANY_ID,
            name="Apex Global Logistics",
            tax_id="TX-8820-A",
            address="100 Logistics Blvd, Suite 400, Chicago, IL 60666",
            contact_email="billing@apexlogistics.com"
        ),
        Vendor(
            id=VENDOR_SENTRY,
            company_id=COMPANY_ID,
            name="Sentry Security Services",
            tax_id="TX-5510-C",
            address="20 Security Way, Dallas, TX 75201",
            contact_email="accounts@sentrysecurity.com"
        ),
        Vendor(
            id=VENDOR_ZAXIS,
            company_id=COMPANY_ID,
            name="Z-Axis Engineering Labs",
            tax_id="TX-9900-F",
            address="88 Innovators Row, San Francisco, CA 94107",
            contact_email="finance@zaxislabs.com"
        )
    ]
    for v in vendors_data:
        session.add(v)
    await session.flush()

    # 4. Create Invoices
    logger.info("Seeding Invoices...")
    today = datetime.date.today()
    invoices_data = [
        # Apex Global Logistics (Low Risk - A)
        Invoice(
            company_id=COMPANY_ID,
            vendor_id=VENDOR_APEX,
            invoice_number="INV-2026-001",
            issue_date=today - datetime.timedelta(days=150),
            due_date=today - datetime.timedelta(days=120),
            total_amount=12450.00,
            tax_amount=1245.00,
            status="completed"
        ),
        Invoice(
            company_id=COMPANY_ID,
            vendor_id=VENDOR_APEX,
            invoice_number="INV-2026-024",
            issue_date=today - datetime.timedelta(days=120),
            due_date=today - datetime.timedelta(days=90),
            total_amount=15800.00,
            tax_amount=1580.00,
            status="completed"
        ),
        Invoice(
            company_id=COMPANY_ID,
            vendor_id=VENDOR_APEX,
            invoice_number="INV-2026-050",
            issue_date=today - datetime.timedelta(days=90),
            due_date=today - datetime.timedelta(days=60),
            total_amount=18900.00,
            tax_amount=1890.00,
            status="completed"
        ),
        Invoice(
            company_id=COMPANY_ID,
            vendor_id=VENDOR_APEX,
            invoice_number="INV-2026-080",
            issue_date=today - datetime.timedelta(days=60),
            due_date=today - datetime.timedelta(days=30),
            total_amount=22100.00,
            tax_amount=2210.00,
            status="completed"
        ),
        Invoice(
            company_id=COMPANY_ID,
            vendor_id=VENDOR_APEX,
            invoice_number="INV-2026-110",
            issue_date=today - datetime.timedelta(days=30),
            due_date=today,
            total_amount=25300.00,
            tax_amount=2530.00,
            status="completed"
        ),
        Invoice(
            company_id=COMPANY_ID,
            vendor_id=VENDOR_APEX,
            invoice_number="INV-2026-140",
            issue_date=today - datetime.timedelta(days=5),
            due_date=today + datetime.timedelta(days=25),
            total_amount=28500.00,
            tax_amount=2850.00,
            status="completed"
        ),
        # Sentry Security Services (Medium Risk - C)
        Invoice(
            company_id=COMPANY_ID,
            vendor_id=VENDOR_SENTRY,
            invoice_number="INV-2026-015",
            issue_date=today - datetime.timedelta(days=120),
            due_date=today - datetime.timedelta(days=90),
            total_amount=8500.00,
            tax_amount=850.00,
            status="completed"
        ),
        Invoice(
            company_id=COMPANY_ID,
            vendor_id=VENDOR_SENTRY,
            invoice_number="INV-2026-042",
            issue_date=today - datetime.timedelta(days=90),
            due_date=today - datetime.timedelta(days=60),
            total_amount=9200.00,
            tax_amount=920.00,
            status="completed"
        ),
        Invoice(
            company_id=COMPANY_ID,
            vendor_id=VENDOR_SENTRY,
            invoice_number="INV-2026-075",
            issue_date=today - datetime.timedelta(days=60),
            due_date=today - datetime.timedelta(days=30),
            total_amount=10800.00,
            tax_amount=1080.00,
            status="completed"
        ),
        Invoice(
            company_id=COMPANY_ID,
            vendor_id=VENDOR_SENTRY,
            invoice_number="INV-2026-105",
            issue_date=today - datetime.timedelta(days=30),
            due_date=today,
            total_amount=12500.00,
            tax_amount=1250.00,
            status="completed"
        ),
        Invoice(
            company_id=COMPANY_ID,
            vendor_id=VENDOR_SENTRY,
            invoice_number="INV-2026-135",
            issue_date=today - datetime.timedelta(days=8),
            due_date=today + datetime.timedelta(days=22),
            total_amount=14200.00,
            tax_amount=1420.00,
            status="completed"
        ),
        # Outlier anomaly invoice for Sentry Security (dated Saturday, high value)
        Invoice(
            company_id=COMPANY_ID,
            vendor_id=VENDOR_SENTRY,
            invoice_number="INV-2026-160",
            # Determine previous Saturday
            issue_date=today - datetime.timedelta(days=((today.weekday() - 5) % 7 or 7)),
            due_date=today + datetime.timedelta(days=15),
            total_amount=30000.00,
            tax_amount=3000.00,
            status="pending_review"
        ),
        # Z-Axis Engineering Labs (High Risk - F)
        Invoice(
            company_id=COMPANY_ID,
            vendor_id=VENDOR_ZAXIS,
            invoice_number="INV-2026-003",
            issue_date=today - datetime.timedelta(days=140),
            due_date=today - datetime.timedelta(days=110),
            total_amount=45000.00,
            tax_amount=4500.00,
            status="completed"
        ),
        Invoice(
            company_id=COMPANY_ID,
            vendor_id=VENDOR_ZAXIS,
            invoice_number="INV-2026-033",
            issue_date=today - datetime.timedelta(days=90),
            due_date=today - datetime.timedelta(days=60),
            total_amount=52000.00,
            tax_amount=5200.00,
            status="completed"
        ),
        # Duplicate invoice check trigger
        Invoice(
            company_id=COMPANY_ID,
            vendor_id=VENDOR_ZAXIS,
            invoice_number="INV-2026-088",
            issue_date=today - datetime.timedelta(days=90),
            due_date=today - datetime.timedelta(days=60),
            total_amount=52000.00,
            tax_amount=5200.00,
            status="completed"
        ),
        # Trigger workflow pending review run
        Invoice(
            id=uuid.UUID('00000000-0000-0000-0000-000000000889'),
            company_id=COMPANY_ID,
            vendor_id=VENDOR_ZAXIS,
            invoice_number="INV-2026-889",
            issue_date=today - datetime.timedelta(days=3),
            due_date=today + datetime.timedelta(days=27),
            total_amount=68500.00,
            tax_amount=6850.00,
            status="pending_review"
        )
    ]
    for inv in invoices_data:
        session.add(inv)
    await session.flush()

    # 5. Create Workflows
    logger.info("Seeding Workflows...")
    workflows_data = [
        Workflow(
            id=WF_RISK_GATE,
            company_id=COMPANY_ID,
            name="High-Value Risk Gate",
            description="Require VP authorization for invoices exceeding $50,000.",
            trigger_type="invoice_ingested",
            definition={
                "trigger": {
                    "conditions": [
                        {"field": "invoice.total_amount", "operator": "greater_than", "value": 50000}
                    ]
                },
                "steps": [
                    {"type": "approval", "role": "VP_FINANCE", "label": "VP Spend Review"}
                ]
            },
            is_active=True
        ),
        Workflow(
            id=WF_AUTO_APPROVE,
            company_id=COMPANY_ID,
            name="Auto-Approve Micro-Spend",
            description="Instantly approve general bills under $1,000 with low-risk vendors.",
            trigger_type="invoice_ingested",
            definition={
                "trigger": {
                    "conditions": [
                        {"field": "invoice.total_amount", "operator": "less_than", "value": 1000},
                        {"field": "vendor.risk_score", "operator": "less_than", "value": 30}
                    ]
                },
                "steps": [
                    {"type": "update_status", "status": "completed", "label": "Mark Approved"}
                ]
            },
            is_active=True
        )
    ]
    for wf in workflows_data:
        session.add(wf)
    await session.flush()

    # 6. Create AgentRuns
    logger.info("Seeding AgentRuns...")
    agent_run = AgentRun(
        id=uuid.UUID('99999999-9999-9999-9999-999999999999'),
        company_id=COMPANY_ID,
        workflow_id=WF_RISK_GATE,
        agent_name="Workflow-High-Value Risk Gate",
        status="waiting_for_approval",
        input_parameters={"invoice_id": "00000000-0000-0000-0000-000000000889"},
        output_results={
            "current_step_id": "vp-approval-step",
            "audit_trail": [
                {
                    "timestamp": (datetime.datetime.now() - datetime.timedelta(hours=2)).isoformat(),
                    "step_id": "trigger",
                    "status": "success",
                    "detail": "Workflow invoked. Invoice amount $68,500 exceeds threshold $50,000."
                },
                {
                    "timestamp": (datetime.datetime.now() - datetime.timedelta(hours=2)).isoformat(),
                    "step_id": "vp-approval-step",
                    "status": "paused",
                    "detail": "High-Value risk gate pauses execution. Awaiting manual VP signoff approval decision."
                }
            ]
        },
        started_at=datetime.datetime.now() - datetime.timedelta(hours=2)
    )
    session.add(agent_run)
    await session.flush()

    # 7. Create Analytics Event logs
    logger.info("Seeding Analytics Logs...")
    analytics_records = [
        # Duplicate record check for INV-2026-088
        Analytics(
            company_id=COMPANY_ID,
            metric_name="invoice_duplicate",
            metric_value=1.0,
            dimensions={
                "invoice_id": "00000000-0000-0000-0000-000000000088",
                "is_duplicate": True,
                "matching_invoice_id": "00000000-0000-0000-0000-000000000033",
                "match_type": "exact_amount_date",
                "reasons": ["Matching invoice with identical amount ($52,000.00) and date exists."]
            },
            timestamp=datetime.datetime.now() - datetime.timedelta(days=90)
        ),
        # Anomaly check for INV-2026-160
        Analytics(
            company_id=COMPANY_ID,
            metric_name="invoice_anomaly",
            metric_value=1.0,
            dimensions={
                "invoice_id": "00000000-0000-0000-0000-000000000160",
                "is_anomaly": True,
                "anomaly_score": 0.85,
                "reasons": ["Transaction dated on a weekend (Saturday) with high total spend"]
            },
            timestamp=datetime.datetime.now() - datetime.timedelta(days=8)
        )
    ]
    for ar in analytics_records:
        session.add(ar)
    await session.flush()

    # 8. Create BusinessMetric monthly aggregates
    logger.info("Seeding BusinessMetrics...")
    business_metrics = [
        BusinessMetric(
            company_id=COMPANY_ID,
            month=datetime.date(2026, 1, 1),
            revenue=124000.00,
            expenses=95000.00,
            profit=29000.00,
            customers=124
        ),
        BusinessMetric(
            company_id=COMPANY_ID,
            month=datetime.date(2026, 2, 1),
            revenue=145000.00,
            expenses=115000.00,
            profit=30000.00,
            customers=142
        ),
        BusinessMetric(
            company_id=COMPANY_ID,
            month=datetime.date(2026, 3, 1),
            revenue=168000.00,
            expenses=124000.00,
            profit=44000.00,
            customers=165
        ),
        BusinessMetric(
            company_id=COMPANY_ID,
            month=datetime.date(2026, 4, 1),
            revenue=158000.00,
            expenses=132000.00,
            profit=26000.00,
            customers=172
        ),
        BusinessMetric(
            company_id=COMPANY_ID,
            month=datetime.date(2026, 5, 1),
            revenue=192000.00,
            expenses=148000.00,
            profit=44000.00,
            customers=194
        ),
        BusinessMetric(
            company_id=COMPANY_ID,
            month=datetime.date(2026, 6, 1),
            revenue=210000.00,
            expenses=152000.00,
            profit=58000.00,
            customers=215
        )
    ]
    for bm in business_metrics:
        session.add(bm)
    await session.flush()

    # 9. Create Decisions
    logger.info("Seeding Tracked Decisions...")
    decisions = [
        Decision(
            company_id=COMPANY_ID,
            problem_type="invoice_delay",
            problem_description="Oracle NetSuite sync connection latency spikes to 12.4s MoM.",
            selected_action="Reroute webhook transactions logs into memory queue brokers.",
            expected_impact="Reduces network transmission lag by over 80% to 2.4s.",
            priority="high",
            status="completed",
            outcome="Synchronized connection lag metrics dropped down to 1.8s in Sandbox testing.",
            performance_change="+85.4% sync velocity"
        ),
        Decision(
            company_id=COMPANY_ID,
            problem_type="outlier_billing",
            problem_description="Z-Axis Engineering invoices checksum failure rates increase to 24%.",
            selected_action="Enforce strict decimal mathematical match compliance rules on Z-Axis OCR templates.",
            expected_impact="Reduces auditing overhead errors from 4h to under 15m.",
            priority="medium",
            status="completed",
            outcome="Auto-held fuzzy checksum discrepancies on invoice uploads, saving human review cycles.",
            performance_change="-93.7% error rate"
        )
    ]
    for d in decisions:
        session.add(d)
    
    await session.commit()
    logger.info("Database seeding successfully completed!")


async def main():
    # Create all tables first
    logger.info("Creating all missing database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database schema initialized.")

    # Open session and run seeding
    async with AsyncSessionLocal() as session:
        try:
            await seed_data(session)
        except Exception as e:
            logger.error(f"Error during seeding: {str(e)}", exc_info=True)
            await session.rollback()
        finally:
            await session.close()


if __name__ == "__main__":
    asyncio.run(main())
