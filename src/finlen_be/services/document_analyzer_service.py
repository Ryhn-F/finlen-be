import logging
from pathlib import Path
from typing import Set
from fastapi import HTTPException, UploadFile, status

from finlen_be.core.config import settings
from finlen_be.schemas.analyzer import DocumentAnalysisResponse
from finlen_be.services.azure_ocr_service import AzureOCRService, azure_ocr_service
from finlen_be.services.gemini_analyzer_service import (
    GeminiAnalyzerService,
    gemini_analyzer_service,
)

logger = logging.getLogger(__name__)

ALLOWED_MIME_TYPES: Set[str] = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "image/jpg",
    "image/pjpeg",
}

ALLOWED_EXTENSIONS: Set[str] = {
    ".pdf",
    ".jpeg",
    ".jpg",
    ".png",
}


class DocumentAnalyzerService:
    """Orchestrator for validating documents, performing Azure OCR extraction,

    and generating structured financial literacy analysis with Gemini.
    """

    def __init__(
        self,
        ocr_service: AzureOCRService | None = None,
        gemini_service: GeminiAnalyzerService | None = None,
        max_file_size_mb: int | None = None,
    ) -> None:
        self.ocr_service = ocr_service or azure_ocr_service
        self.gemini_service = gemini_service or gemini_analyzer_service
        self.max_file_size_mb = (
            max_file_size_mb if max_file_size_mb is not None else settings.document_max_file_size_mb
        )

    async def _read_and_validate_file(self, file: UploadFile) -> bytes:
        """Validate filename extension, MIME type, and enforce max file size limit.

        Returns file bytes in memory (stateless).
        """
        filename = file.filename or ""
        ext = Path(filename).suffix.lower()

        # 1. Validate file extension
        if ext not in ALLOWED_EXTENSIONS:
            logger.warning("Rejected file with invalid extension: %s", ext)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported file format. Allowed formats: PDF, JPEG, PNG.",
            )

        # 2. Validate declared MIME type
        content_type = (file.content_type or "").lower().split(";")[0].strip()
        if content_type not in ALLOWED_MIME_TYPES:
            logger.warning("Rejected file with invalid MIME type: %s", content_type)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported file format. Allowed formats: PDF, JPEG, PNG.",
            )

        # 3. Read content and validate size limit
        max_bytes = self.max_file_size_mb * 1024 * 1024
        content = await file.read()

        if len(content) > max_bytes:
            logger.warning(
                "Document file size (%d bytes) exceeds maximum limit (%d bytes)",
                len(content),
                max_bytes,
            )
            raise HTTPException(
                status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                detail="Document file size exceeds the maximum allowed limit.",
            )

        if len(content) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty.",
            )

        return content

    async def analyze(self, file: UploadFile) -> DocumentAnalysisResponse:
        """Complete pipeline:

        1. Validate metadata, MIME type, and size
        2. Extract OCR text via Azure AI Document Intelligence
        3. Validate extracted text is non-empty
        4. Analyze financial literacy & risks via Gemini
        5. Return structured Pydantic response
        """
        logger.info("Document analysis started for file: %s", file.filename)

        # Step 1: Read and validate file
        file_bytes = await self._read_and_validate_file(file)

        # Step 2: Azure OCR
        extracted_text = await self.ocr_service.extract_text(
            file=file_bytes,
            content_type=file.content_type,
        )

        # Step 3: Validate OCR output is non-empty
        if not extracted_text or not extracted_text.strip():
            logger.warning("Document OCR returned empty content for file: %s", file.filename)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="No readable text could be extracted from the document.",
            )

        # Step 4: Gemini Analysis
        analysis = await self.gemini_service.analyze_document(extracted_text)

        logger.info("Document analysis completed successfully for file: %s", file.filename)
        return DocumentAnalysisResponse(analysis=analysis)


document_analyzer_service = DocumentAnalyzerService()
