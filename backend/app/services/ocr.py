import abc
import datetime
import logging
import time
from typing import List, Tuple

from app.schemas.ocr_schemas import ExtractedInvoiceSchema, LineItemSchema

logger = logging.getLogger(__name__)


class BaseOCREngine(abc.ABC):
    """
    Abstract Base Class for OCR Parsing Engines.
    Different engines (Tesseract, Paddle, GPT-4o) implement this interface.
    """

    @abc.abstractmethod
    def extract_document(self, file_content: bytes) -> ExtractedInvoiceSchema:
        """
        Executes OCR engine and parses structured financial data.
        """
        pass


class MockOCREngine(BaseOCREngine):
    """
    Mock OCR engine designed for local development and test verification.
    Parses a mock invoice dynamically.
    """

    def extract_document(self, file_content: bytes) -> ExtractedInvoiceSchema:
        # Simulate processing delay
        time.sleep(0.1)
        
        # Returns standard valid mock data
        return ExtractedInvoiceSchema(
            invoice_number="INV-2026-9901",
            vendor_name="Acme Corporate Supplies",
            invoice_date=datetime.date(2026, 6, 1),
            due_date=datetime.date(2026, 7, 1),
            subtotal=1000.0,
            tax_amount=100.0,
            total_amount=1100.0,
            currency="USD",
            line_items=[
                LineItemSchema(description="Enterprise Licenses", quantity=2.0, unit_price=400.0, total_amount=800.0),
                LineItemSchema(description="Support Contract SLA", quantity=1.0, unit_price=200.0, total_amount=200.0)
            ],
            confidence_score=0.90
        )


class TesseractEngine(BaseOCREngine):
    """
    Tesseract Engine stub implementation.
    """

    def extract_document(self, file_content: bytes) -> ExtractedInvoiceSchema:
        logger.info("Invoking local Tesseract OCR engine...")
        # Production would run: text = pytesseract.image_to_string(PIL.Image.open(io.BytesIO(file_content)))
        raise NotImplementedError("Tesseract engine is currently in design stub phase.")


class GPT4oVisionEngine(BaseOCREngine):
    """
    GPT-4o Vision API Engine stub implementation.
    """

    def extract_document(self, file_content: bytes) -> ExtractedInvoiceSchema:
        logger.info("Invoking OpenAI GPT-4o Vision API...")
        # Production would send base64 encoded document to chat.completions API with structured output schema.
        raise NotImplementedError("GPT-4o Vision API is currently in design stub phase.")


class OCRService:
    """
    Orchestration layer managing OCR execution, field validations,
    mathematical checks, confidence scoring, and telemetry compilation.
    """

    def __init__(self, engine: BaseOCREngine = MockOCREngine()):
        self.engine = engine

    def process_document(self, file_content: bytes) -> Tuple[ExtractedInvoiceSchema, List[str], int]:
        """
        Processes document, executes validations, adjusts confidence, and compiles logs.
        Returns: Tuple[ExtractedInvoiceSchema, List[warnings], processing_time_ms]
        """
        start_time = time.time()
        
        # 1. Run core OCR extraction
        extracted_data = self.engine.extract_document(file_content)
        
        # 2. Execute Validation Checks & Adjust Confidence
        warnings = []
        base_confidence = extracted_data.confidence_score
        confidence_adjustment = 0.0

        # Math Check 1: subtotal + tax_amount == total_amount
        if (
            extracted_data.subtotal is not None 
            and extracted_data.tax_amount is not None 
            and extracted_data.total_amount is not None
        ):
            checksum = round(extracted_data.subtotal + extracted_data.tax_amount, 2)
            expected_total = round(extracted_data.total_amount, 2)
            if checksum == expected_total:
                confidence_adjustment += 0.15
            else:
                warnings.append(
                    f"Checksum mismatch: subtotal ({extracted_data.subtotal}) + tax ({extracted_data.tax_amount}) "
                    f"does not equal total ({extracted_data.total_amount}). Diff: {round(abs(checksum - expected_total), 2)}"
                )
                confidence_adjustment -= 0.20

        # Math Check 2: line items sum == subtotal
        if extracted_data.line_items and extracted_data.subtotal is not None:
            line_sum = sum(item.total_amount for item in extracted_data.line_items)
            if round(line_sum, 2) == round(extracted_data.subtotal, 2):
                confidence_adjustment += 0.15
            else:
                warnings.append(
                    f"Line items total mismatch: sum of line items ({line_sum}) "
                    f"does not equal subtotal ({extracted_data.subtotal})."
                )
                confidence_adjustment -= 0.15

        # Check 3: Due date >= Invoice date
        if extracted_data.invoice_date and extracted_data.due_date:
            if extracted_data.due_date >= extracted_data.invoice_date:
                confidence_adjustment += 0.05
            else:
                warnings.append(
                    f"Chronology violation: due_date ({extracted_data.due_date}) is "
                    f"before invoice_date ({extracted_data.invoice_date})."
                )
                confidence_adjustment -= 0.10

        # Check 4: Check if key attributes are missing
        missing_fields = []
        if not extracted_data.invoice_number:
            missing_fields.append("invoice_number")
        if not extracted_data.vendor_name:
            missing_fields.append("vendor_name")
        if not extracted_data.total_amount:
            missing_fields.append("total_amount")

        if missing_fields:
            warnings.append(f"Missing key invoice fields: {', '.join(missing_fields)}")
            confidence_adjustment -= 0.10 * len(missing_fields)

        # Apply adjusted confidence score bound between 0.0 and 1.0
        final_confidence = max(0.0, min(1.0, base_confidence + confidence_adjustment))
        extracted_data.confidence_score = round(final_confidence, 2)

        # Calculate processing duration
        processing_time_ms = int((time.time() - start_time) * 1000)

        logger.info(
            f"OCR parsing completed. Processing time: {processing_time_ms}ms. "
            f"Adjusted confidence: {extracted_data.confidence_score}. Warnings: {len(warnings)}"
        )
        
        return extracted_data, warnings, processing_time_ms
