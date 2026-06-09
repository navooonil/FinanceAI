import datetime
import uuid
from unittest.mock import MagicMock, patch
import pytest

from app.schemas.ocr_schemas import ExtractedInvoiceSchema, LineItemSchema
from app.services.ocr import OCRService, BaseOCREngine


class SimpleTestEngine(BaseOCREngine):
    """
    Test engine that yields custom defined extraction schemas.
    """
    def __init__(self, data: ExtractedInvoiceSchema):
        self.data = data

    def extract_document(self, file_content: bytes) -> ExtractedInvoiceSchema:
        return self.data


def test_ocr_validation_perfect_match():
    """
    Asserts a document with correct mathematical and date parameters obtains maximum confidence.
    """
    data = ExtractedInvoiceSchema(
        invoice_number="INV-1234",
        vendor_name="Test Vendor",
        invoice_date=datetime.date(2026, 6, 1),
        due_date=datetime.date(2026, 6, 15),
        subtotal=100.0,
        tax_amount=10.0,
        total_amount=110.0,
        currency="USD",
        line_items=[
            LineItemSchema(description="Item A", quantity=1.0, unit_price=100.0, total_amount=100.0)
        ],
        confidence_score=0.60  # Initial base score
    )

    ocr_service = OCRService(engine=SimpleTestEngine(data))
    extracted, warnings, duration = ocr_service.process_document(b"contents")

    # +0.15 (subtotal+tax==total)
    # +0.15 (line_sum==subtotal)
    # +0.05 (due_date>=invoice_date)
    # Total adjustment = +0.35 -> final = 0.95
    assert extracted.confidence_score == 0.95
    assert len(warnings) == 0


def test_ocr_validation_checksum_mismatch():
    """
    Asserts a total checksum discrepancy results in confidence penalty and warnings.
    """
    data = ExtractedInvoiceSchema(
        invoice_number="INV-1234",
        vendor_name="Test Vendor",
        invoice_date=datetime.date(2026, 6, 1),
        due_date=datetime.date(2026, 6, 15),
        subtotal=100.0,
        tax_amount=10.0,
        total_amount=150.0,  # Math mismatch (100+10 != 150)
        currency="USD",
        line_items=[
            LineItemSchema(description="Item A", quantity=1.0, unit_price=100.0, total_amount=100.0)
        ],
        confidence_score=0.80
    )

    ocr_service = OCRService(engine=SimpleTestEngine(data))
    extracted, warnings, duration = ocr_service.process_document(b"contents")

    # -0.20 (checksum mismatch)
    # +0.15 (line items match subtotal)
    # +0.05 (due_date >= invoice_date)
    # Total adjustment = 0.0 -> final = 0.80
    assert extracted.confidence_score == 0.80
    assert any("Checksum mismatch" in w for w in warnings)


def test_ocr_validation_chronology_mismatch():
    """
    Asserts due date prior to issue date results in confidence penalty and warnings.
    """
    data = ExtractedInvoiceSchema(
        invoice_number="INV-1234",
        vendor_name="Test Vendor",
        invoice_date=datetime.date(2026, 6, 15),
        due_date=datetime.date(2026, 6, 1),  # Chronology mismatch
        subtotal=100.0,
        tax_amount=10.0,
        total_amount=110.0,
        currency="USD",
        line_items=[],
        confidence_score=0.80
    )

    ocr_service = OCRService(engine=SimpleTestEngine(data))
    extracted, warnings, duration = ocr_service.process_document(b"contents")

    # +0.15 (checksum matches)
    # -0.10 (due date is before invoice date)
    # Total adjustment = +0.05 -> final = 0.85
    assert extracted.confidence_score == 0.85
    assert any("Chronology violation" in w for w in warnings)


class AsyncSessionMock:
    """
    Class-based mock for SQLAlchemy async session.
    Bypasses MagicMock context manager complexity.
    """
    def __init__(self, mock_invoice):
        self.mock_invoice = mock_invoice
        self.added = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def execute(self, *args, **kwargs):
        mock_res = MagicMock()
        mock_res.scalar_one_or_none.return_value = self.mock_invoice
        return mock_res

    async def commit(self):
        pass

    def add(self, obj):
        self.added.append(obj)


@pytest.mark.asyncio
async def test_worker_ocr_low_confidence_flags_pending_review():
    """
    Asserts that if the OCR service yields low confidence, the invoice
    status is updated to 'pending_review' and an audit run is logged.
    """
    low_confidence_data = ExtractedInvoiceSchema(
        invoice_number=None,  # Missing field
        vendor_name="Test Vendor",
        invoice_date=datetime.date(2026, 6, 1),
        due_date=datetime.date(2026, 6, 15),
        subtotal=100.0,
        tax_amount=10.0,
        total_amount=110.0,
        currency="USD",
        line_items=[],
        confidence_score=0.40  # Very low base score
    )

    invoice_id = str(uuid.uuid4())
    mock_invoice = MagicMock()
    mock_invoice.id = uuid.UUID(invoice_id)
    mock_invoice.company_id = uuid.uuid4()
    mock_invoice.s3_key = "tenants/test/invoices/test.pdf"
    mock_invoice.status = "processing"
    
    # Mocking storage return bytes
    with patch("app.services.tasks.storage_service.download_file") as mock_download, \
         patch("app.services.tasks.OCRService") as mock_ocr_class:
        
        mock_download.return_value = b"%PDF fake bytes"
        
        # Instantiate fake ocr service returning Low Confidence
        mock_ocr_service = MagicMock()
        mock_ocr_service.process_document.return_value = (low_confidence_data, ["low confidence warning"], 150)
        mock_ocr_class.return_value = mock_ocr_service

        from app.services.tasks import _async_process_document
        
        mock_session = AsyncSessionMock(mock_invoice)
        
        # Patch local Session maker instance inside app.services.tasks module
        with patch("app.services.tasks.AsyncSessionLocal", return_value=mock_session):
            await _async_process_document(invoice_id)
            
            # Assert low confidence redirected status to pending_review
            assert mock_invoice.status == "pending_review"
            
            # Assert audit run was added to session
            assert len(mock_session.added) > 0
            added_object = mock_session.added[0]
            assert added_object.agent_name == "OCRParserAgent"
            assert added_object.status == "pending_review"
