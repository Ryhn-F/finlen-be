import asyncio
import io
import json
import uuid
import pytest
from fastapi import HTTPException
from httpx import AsyncClient
from unittest.mock import AsyncMock, MagicMock, patch

from finlen_be.schemas.analyzer import DocumentAnalysis, DocumentAnalysisResponse
from finlen_be.services.azure_ocr_service import AzureOCRService
from finlen_be.services.gemini_analyzer_service import GeminiAnalyzerService
from finlen_be.services.document_analyzer_service import (
    DocumentAnalyzerService,
    document_analyzer_service,
)

SAMPLE_ANALYSIS_DICT = {
    "document_type": "loan_agreement",
    "summary": "Dokumen menunjukkan pinjaman sebesar Rp3.000.000 dengan bunga 5% per bulan.",
    "financial_terms": {
        "principal": 3000000.0,
        "interest_rate": 5.0,
        "interest_period": "monthly",
        "due_date": "2026-09-15",
        "currency": "IDR",
    },
    "risk_level": "high",
    "risk_factors": [
        {
            "title": "Bunga bulanan tinggi",
            "description": "Dokumen mencantumkan bunga sebesar 5% per bulan.",
            "severity": "high",
        }
    ],
    "red_flags": ["Bunga bulanan relatif tinggi"],
    "recommended_actions": [
        "Periksa kembali seluruh biaya dan ketentuan pembayaran.",
        "Hitung total kewajiban sebelum mengambil keputusan pembayaran.",
    ],
    "financial_literacy": [
        {
            "concept": "Interest Rate",
            "explanation": "Bunga bulanan dapat meningkatkan total kewajiban secara signifikan sehingga perlu dipahami sebelum mengambil keputusan.",
        }
    ],
}


async def get_authenticated_headers(client: AsyncClient, suffix: str) -> dict[str, str]:
    """Helper to create a user and get authorization bearer headers."""
    username = f"user_{suffix}"
    email = f"user_{suffix}@example.com"
    password = "SuperPassword123!"

    reg = await client.post(
        "/api/v1/auth/register",
        json={"username": username, "email": email, "password": password},
    )
    assert reg.status_code == 201

    login = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ── File Validation Tests ───────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_unauthenticated_request_returns_401(client: AsyncClient):
    """Calling /api/v1/analyzer/documents without auth token must return 401."""
    files = {"file": ("contract.pdf", b"%PDF-1.4 dummy", "application/pdf")}
    res = await client.post("/api/v1/analyzer/documents", files=files)
    assert res.status_code == 401
    assert "detail" in res.json()


@pytest.mark.asyncio
async def test_unsupported_file_extension_returns_400(client: AsyncClient):
    """Uploading files with forbidden extensions (.txt, .exe, .zip) must return 400."""
    headers = await get_authenticated_headers(client, uuid.uuid4().hex[:8])

    # Forbidden .txt extension
    files = {"file": ("malicious.txt", b"plain text", "text/plain")}
    res = await client.post("/api/v1/analyzer/documents", headers=headers, files=files)
    assert res.status_code == 400
    assert "Unsupported file format" in res.json()["detail"]

    # Forbidden .exe extension with spoofed MIME
    files_exe = {"file": ("malware.exe", b"MZ...", "application/pdf")}
    res_exe = await client.post("/api/v1/analyzer/documents", headers=headers, files=files_exe)
    assert res_exe.status_code == 400
    assert "Unsupported file format" in res_exe.json()["detail"]


@pytest.mark.asyncio
async def test_unsupported_mime_type_returns_400(client: AsyncClient):
    """Uploading files with mismatched or forbidden MIME types must return 400."""
    headers = await get_authenticated_headers(client, uuid.uuid4().hex[:8])

    files = {"file": ("fake.pdf", b"something", "application/zip")}
    res = await client.post("/api/v1/analyzer/documents", headers=headers, files=files)
    assert res.status_code == 400
    assert "Unsupported file format" in res.json()["detail"]


@pytest.mark.asyncio
async def test_empty_file_returns_400(client: AsyncClient):
    """Uploading a 0-byte file must return 400."""
    headers = await get_authenticated_headers(client, uuid.uuid4().hex[:8])

    files = {"file": ("empty.pdf", b"", "application/pdf")}
    res = await client.post("/api/v1/analyzer/documents", headers=headers, files=files)
    assert res.status_code == 400
    assert "empty" in res.json()["detail"].lower()


@pytest.mark.asyncio
async def test_oversized_file_returns_413(client: AsyncClient, monkeypatch: pytest.MonkeyPatch):
    """Uploading a file exceeding DOCUMENT_MAX_FILE_SIZE_MB must return 413 without calling Azure."""
    headers = await get_authenticated_headers(client, uuid.uuid4().hex[:8])

    # Set limit to 1MB for quick testing
    monkeypatch.setattr(document_analyzer_service, "max_file_size_mb", 1)

    oversized_data = b"x" * (1 * 1024 * 1024 + 100)  # > 1MB
    files = {"file": ("large.pdf", oversized_data, "application/pdf")}
    res = await client.post("/api/v1/analyzer/documents", headers=headers, files=files)
    assert res.status_code == 413
    assert "exceeds the maximum allowed limit" in res.json()["detail"]


# ── OCR & Azure Provider Tests ──────────────────────────────────────────────


@pytest.mark.asyncio
async def test_empty_ocr_text_returns_422(client: AsyncClient, monkeypatch: pytest.MonkeyPatch):
    """When Azure OCR returns no readable text, endpoint must return 422."""
    headers = await get_authenticated_headers(client, uuid.uuid4().hex[:8])

    mock_ocr = AsyncMock()
    mock_ocr.extract_text.return_value = "   \n\n  "
    mock_gemini = AsyncMock()

    monkeypatch.setattr(document_analyzer_service, "ocr_service", mock_ocr)
    monkeypatch.setattr(document_analyzer_service, "gemini_service", mock_gemini)

    files = {"file": ("blank.png", b"\x89PNG\r\n\x1a\n" + b"\x00" * 50, "image/png")}
    res = await client.post("/api/v1/analyzer/documents", headers=headers, files=files)
    assert res.status_code == 422
    assert "No readable text could be extracted" in res.json()["detail"]
    # Gemini must NOT be called when OCR text is empty
    mock_gemini.analyze_document.assert_not_called()


@pytest.mark.asyncio
async def test_azure_ocr_failure_returns_502(client: AsyncClient, monkeypatch: pytest.MonkeyPatch):
    """When Azure OCR raises an unexpected exception or 502, return 502."""
    headers = await get_authenticated_headers(client, uuid.uuid4().hex[:8])

    mock_ocr = AsyncMock()
    mock_ocr.extract_text.side_effect = HTTPException(
        status_code=502,
        detail="Document OCR service is temporarily unavailable.",
    )

    monkeypatch.setattr(document_analyzer_service, "ocr_service", mock_ocr)

    files = {"file": ("test.pdf", b"%PDF-1.4 dummy", "application/pdf")}
    res = await client.post("/api/v1/analyzer/documents", headers=headers, files=files)
    assert res.status_code == 502
    assert "Document OCR service is temporarily unavailable." in res.json()["detail"]


@pytest.mark.asyncio
async def test_azure_ocr_timeout_returns_504(client: AsyncClient, monkeypatch: pytest.MonkeyPatch):
    """When Azure OCR times out, endpoint must return 504."""
    headers = await get_authenticated_headers(client, uuid.uuid4().hex[:8])

    mock_ocr = AsyncMock()
    mock_ocr.extract_text.side_effect = HTTPException(
        status_code=504,
        detail="Document analysis timed out. Please try again.",
    )

    monkeypatch.setattr(document_analyzer_service, "ocr_service", mock_ocr)

    files = {"file": ("test.pdf", b"%PDF-1.4 dummy", "application/pdf")}
    res = await client.post("/api/v1/analyzer/documents", headers=headers, files=files)
    assert res.status_code == 504
    assert "timed out" in res.json()["detail"].lower()


def test_azure_ocr_normalization():
    """Verify normalization collapses excess empty lines and strips trailing spaces."""
    service = AzureOCRService()
    raw = "Header   \r\n\r\n\r\n\r\nRp3.000.000\t  \r\nInterest: 5%   \n\n\n\nFooter"
    normalized = service.normalize_ocr_text(raw)
    assert "Header" in normalized
    assert "Rp3.000.000" in normalized
    assert "Interest: 5%" in normalized
    # Max consecutive blank lines should be 2
    assert "\n\n\n\n" not in normalized


# ── Gemini Provider & Schema Validation Tests ───────────────────────────────


@pytest.mark.asyncio
async def test_gemini_valid_analysis_success(client: AsyncClient, monkeypatch: pytest.MonkeyPatch):
    """Valid PDF, JPEG, and PNG uploads succeed with 200 and strict DocumentAnalysis structure."""
    headers = await get_authenticated_headers(client, uuid.uuid4().hex[:8])

    expected_analysis = DocumentAnalysis.model_validate(SAMPLE_ANALYSIS_DICT)

    mock_ocr = AsyncMock()
    mock_ocr.extract_text.return_value = "LOAN AGREEMENT\nPrincipal: Rp3.000.000\nInterest: 5% per month\nDue Date: 2026-09-15"

    mock_gemini = AsyncMock()
    mock_gemini.analyze_document.return_value = expected_analysis

    monkeypatch.setattr(document_analyzer_service, "ocr_service", mock_ocr)
    monkeypatch.setattr(document_analyzer_service, "gemini_service", mock_gemini)

    # 1. Test PDF
    pdf_files = {"file": ("loan.pdf", b"%PDF-1.4 header", "application/pdf")}
    pdf_res = await client.post("/api/v1/analyzer/documents", headers=headers, files=pdf_files)
    assert pdf_res.status_code == 200
    pdf_json = pdf_res.json()
    assert pdf_json["analysis"]["document_type"] == "loan_agreement"
    assert pdf_json["analysis"]["financial_terms"]["principal"] == 3000000.0
    assert pdf_json["analysis"]["risk_level"] == "high"

    # 2. Test JPEG
    jpg_files = {"file": ("statement.jpeg", b"\xff\xd8\xff dummy", "image/jpeg")}
    jpg_res = await client.post("/api/v1/analyzer/documents", headers=headers, files=jpg_files)
    assert jpg_res.status_code == 200

    # 3. Test PNG
    png_files = {"file": ("receipt.png", b"\x89PNG\r\n\x1a\n dummy", "image/png")}
    png_res = await client.post("/api/v1/analyzer/documents", headers=headers, files=png_files)
    assert png_res.status_code == 200


@pytest.mark.asyncio
async def test_gemini_service_unit_correction_retry():
    """When Gemini returns malformed JSON on the first attempt, it must retry once

    with a correction prompt and succeed if the second attempt is valid.
    """
    mock_genai_client = MagicMock()
    first_bad_response = MagicMock()
    first_bad_response.text = "This is not json at all!"

    second_good_response = MagicMock()
    second_good_response.text = json.dumps(SAMPLE_ANALYSIS_DICT)

    # Mock async client.aio.models.generate_content
    mock_genai_client.aio.models.generate_content = AsyncMock(
        side_effect=[first_bad_response, second_good_response]
    )

    service = GeminiAnalyzerService(api_key="test-key", client=mock_genai_client)
    result = await service.analyze_document("Sample OCR document text")

    assert result.document_type == "loan_agreement"
    assert result.risk_level == "high"
    assert mock_genai_client.aio.models.generate_content.call_count == 2


@pytest.mark.asyncio
async def test_gemini_service_unit_double_failure_returns_502():
    """When Gemini returns invalid JSON twice, service raises 502 with specific detail."""
    mock_genai_client = MagicMock()
    bad_response = MagicMock()
    bad_response.text = "Still invalid json {"

    mock_genai_client.aio.models.generate_content = AsyncMock(
        side_effect=[bad_response, bad_response]
    )

    service = GeminiAnalyzerService(api_key="test-key", client=mock_genai_client)
    with pytest.raises(HTTPException) as exc_info:
        await service.analyze_document("Sample OCR document text")

    assert exc_info.value.status_code == 502
    assert "Document analysis service returned an invalid response." in exc_info.value.detail
    assert mock_genai_client.aio.models.generate_content.call_count == 2


@pytest.mark.asyncio
async def test_gemini_failure_returns_502(client: AsyncClient, monkeypatch: pytest.MonkeyPatch):
    """When Gemini service fails / is unavailable, endpoint must return 502."""
    headers = await get_authenticated_headers(client, uuid.uuid4().hex[:8])

    mock_ocr = AsyncMock()
    mock_ocr.extract_text.return_value = "Sample valid extracted text"

    mock_gemini = AsyncMock()
    mock_gemini.analyze_document.side_effect = HTTPException(
        status_code=502,
        detail="Document analysis service is temporarily unavailable.",
    )

    monkeypatch.setattr(document_analyzer_service, "ocr_service", mock_ocr)
    monkeypatch.setattr(document_analyzer_service, "gemini_service", mock_gemini)

    files = {"file": ("test.pdf", b"%PDF-1.4 dummy", "application/pdf")}
    res = await client.post("/api/v1/analyzer/documents", headers=headers, files=files)
    assert res.status_code == 502
    assert "Document analysis service is temporarily unavailable." in res.json()["detail"]


@pytest.mark.asyncio
async def test_gemini_timeout_returns_504(client: AsyncClient, monkeypatch: pytest.MonkeyPatch):
    """When Gemini service times out, endpoint must return 504."""
    headers = await get_authenticated_headers(client, uuid.uuid4().hex[:8])

    mock_ocr = AsyncMock()
    mock_ocr.extract_text.return_value = "Sample valid extracted text"

    mock_gemini = AsyncMock()
    mock_gemini.analyze_document.side_effect = HTTPException(
        status_code=504,
        detail="Document analysis timed out. Please try again.",
    )

    monkeypatch.setattr(document_analyzer_service, "ocr_service", mock_ocr)
    monkeypatch.setattr(document_analyzer_service, "gemini_service", mock_gemini)

    files = {"file": ("test.pdf", b"%PDF-1.4 dummy", "application/pdf")}
    res = await client.post("/api/v1/analyzer/documents", headers=headers, files=files)
    assert res.status_code == 504
    assert "timed out" in res.json()["detail"].lower()


# ── End-to-End Mocked Pipeline Test ─────────────────────────────────────────


@pytest.mark.asyncio
async def test_end_to_end_mocked_pipeline(client: AsyncClient, monkeypatch: pytest.MonkeyPatch):
    """Full E2E test verifying:

    POST document -> auth -> validation -> mock Azure OCR -> mock Gemini -> Pydantic -> 200 response
    """
    headers = await get_authenticated_headers(client, uuid.uuid4().hex[:8])

    ocr_text = (
        "Page 1:\n"
        "PERJANJIAN PINJAMAN DANA\n"
        "Peminjam: John Doe\n"
        "Pokok Pinjaman: Rp 3.000.000\n"
        "Bunga: 5% per bulan\n"
        "Jatuh Tempo: 2026-09-15\n"
    )

    mock_ocr = AsyncMock()
    mock_ocr.extract_text.return_value = ocr_text

    mock_gemini = AsyncMock()
    mock_gemini.analyze_document.return_value = DocumentAnalysis.model_validate(SAMPLE_ANALYSIS_DICT)

    monkeypatch.setattr(document_analyzer_service, "ocr_service", mock_ocr)
    monkeypatch.setattr(document_analyzer_service, "gemini_service", mock_gemini)

    files = {"file": ("loan_agreement.pdf", b"%PDF-1.4 sample content", "application/pdf")}
    response = await client.post("/api/v1/analyzer/documents", headers=headers, files=files)

    assert response.status_code == 200
    data = response.json()

    # Validate response adheres exactly to frontend contract
    assert "analysis" in data
    analysis = data["analysis"]
    assert analysis["document_type"] == "loan_agreement"
    assert analysis["summary"] != ""
    assert analysis["financial_terms"]["principal"] == 3000000.0
    assert analysis["financial_terms"]["interest_rate"] == 5.0
    assert analysis["financial_terms"]["currency"] == "IDR"
    assert analysis["risk_level"] == "high"
    assert len(analysis["risk_factors"]) > 0
    assert len(analysis["red_flags"]) > 0
    assert len(analysis["recommended_actions"]) > 0
    assert len(analysis["financial_literacy"]) > 0

    # Verify Gemini was invoked with the exact OCR text
    mock_gemini.analyze_document.assert_called_once_with(ocr_text)
