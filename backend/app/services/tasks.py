import asyncio
import logging
import uuid
from celery import shared_task
from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.invoice import Invoice
from app.models.agent import AgentRun
from app.services.storage import storage_service
from app.services.ocr import OCRService
from app.worker import celery_app

logger = logging.getLogger(__name__)


async def _async_process_document(invoice_id: str) -> None:
    """
    Core async document ingestion logic.
    Retrieves the invoice from DB, downloads file from storage, validates the file,
    and updates metadata transaction state.
    """
    invoice_uuid = uuid.UUID(invoice_id)
    
    async with AsyncSessionLocal() as session:
        # 1. Retrieve the target invoice record
        result = await session.execute(select(Invoice).where(Invoice.id == invoice_uuid))
        invoice = result.scalar_one_or_none()
        
        if not invoice:
            logger.error(f"Invoice record '{invoice_id}' not found in database. Ingestion aborted.")
            return

        logger.info(f"Processing ingestion pipeline for invoice: {invoice.id} (key: {invoice.s3_key})")
        
        # 2. Update status to 'processing'
        invoice.status = "processing"
        await session.commit()

        # 3. Fetch file content from Storage (S3 / Local Fallback)
        try:
            file_bytes = storage_service.download_file(invoice.s3_key)
            if not file_bytes:
                raise ValueError("File content retrieved from storage is empty.")
            
            logger.info(f"Retrieved {len(file_bytes)} bytes for invoice {invoice.id}. Starting OCR Intelligence Extraction...")
            
            # Initialize OCR Service
            ocr_service = OCRService()
            extracted_data, warnings, processing_time = ocr_service.process_document(file_bytes)
            
            # 4. Update Invoice relational fields with extracted attributes
            invoice.invoice_number = extracted_data.invoice_number
            invoice.issue_date = extracted_data.invoice_date
            invoice.due_date = extracted_data.due_date
            invoice.total_amount = extracted_data.total_amount
            invoice.tax_amount = extracted_data.tax_amount
            invoice.currency = extracted_data.currency
            invoice.ocr_raw_text = (
                f"Vendor: {extracted_data.vendor_name}\n"
                f"Subtotal: {extracted_data.subtotal}\n"
                f"Line Items Count: {len(extracted_data.line_items)}\n"
                f"Confidence Score: {extracted_data.confidence_score}\n"
                f"Warnings: {len(warnings)}"
            )

            # Determine status based on confidence threshold
            if extracted_data.confidence_score >= 0.70:
                invoice.status = "completed"
            else:
                invoice.status = "pending_review"
                logger.warning(
                    f"Invoice {invoice.id} flagged for human audit. "
                    f"Confidence score {extracted_data.confidence_score} is below the 0.70 threshold."
                )

            # 5. Record Audit log details inside agent_runs table
            audit_run = AgentRun(
                company_id=invoice.company_id,
                agent_name="OCRParserAgent",
                status="completed" if extracted_data.confidence_score >= 0.70 else "pending_review",
                input_parameters={"invoice_id": str(invoice.id), "file_key": invoice.s3_key},
                output_results={
                    "extracted_data": extracted_data.model_dump(mode="json"),
                    "warnings": warnings,
                    "processing_time_ms": processing_time
                }
            )
            session.add(audit_run)
            
        except Exception as e:
            logger.error(f"Failed to process OCR ingestion for invoice {invoice.id}: {str(e)}", exc_info=True)
            raise e

        # 6. Commit all transactional updates
        await session.commit()
        logger.info(f"Successfully completed OCR processing pipeline for invoice {invoice.id}. Status: {invoice.status}")


async def _async_mark_invoice_failed(invoice_id: str, error_message: str) -> None:
    """
    Updates the target database record to failed state.
    """
    invoice_uuid = uuid.UUID(invoice_id)
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Invoice).where(Invoice.id == invoice_uuid))
        invoice = result.scalar_one_or_none()
        if invoice:
            invoice.status = "failed"
            # In a full app, we would store the traceback/error log in the record or an event table
            logger.error(f"Marking invoice {invoice_id} as FAILED. Reason: {error_message}")
            await session.commit()


@celery_app.task(bind=True, max_retries=5)
def process_document_task(self, invoice_id: str) -> None:
    """
    Celery Task wrapper for document processing.
    Executes the async logic using an event loop context.
    Implements transient failure retries with exponential backoff.
    """
    try:
        # Run async function within a synchronous thread-safe event loop execution
        asyncio.run(_async_process_document(invoice_id))
    except Exception as e:
        # Determine delay using exponential backoff: 2^retries (e.g. 1s, 2s, 4s, 8s, 16s...)
        backoff_countdown = 2 ** self.request.retries
        logger.warning(
            f"Transient processing failure for invoice {invoice_id}. "
            f"Scheduling retry {self.request.retries + 1}/5 in {backoff_countdown}s. Error: {str(e)}"
        )
        try:
            # Trigger Celery retry mechanism
            raise self.retry(exc=e, countdown=backoff_countdown)
        except Exception as retry_ex:
            # Check if we have exhausted retries or encountered a permanent failure
            if self.request.retries >= self.max_retries:
                logger.error(f"Max retries exhausted for invoice {invoice_id}. Marking as permanently failed.")
                asyncio.run(_async_mark_invoice_failed(invoice_id, str(e)))
            raise retry_ex
