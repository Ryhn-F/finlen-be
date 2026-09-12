import asyncio
import io
import logging
import re
from typing import Union
from azure.ai.documentintelligence.aio import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from fastapi import HTTPException, UploadFile, status

from finlen_be.core.config import settings

logger = logging.getLogger(__name__)


class AzureOCRService:
    """Isolated service for extracting readable textual content from financial documents

    using Azure AI Document Intelligence.
    """

    def __init__(
        self,
        endpoint: str | None = None,
        key: str | None = None,
        model_id: str = "prebuilt-layout",
        timeout: float | None = None,
    ) -> None:
        self.endpoint = endpoint or settings.azure_document_intelligence_endpoint
        self.key = key or settings.azure_document_intelligence_key
        self.model_id = model_id
        self.timeout = timeout or float(settings.document_analysis_timeout_seconds)

    def normalize_ocr_text(self, text: str) -> str:
        """Normalize extracted OCR text while strictly preserving financial values,

        dates, percentages, and structural line breaks.
        """
        if not text:
            return ""

        # Normalize windows/mac line breaks
        normalized = text.replace("\r\n", "\n").replace("\r", "\n")

        # Strip trailing spaces on each line
        lines = [re.sub(r"[ \t]+$", "", line) for line in normalized.split("\n")]

        # Collapse more than 2 consecutive blank lines into 2
        collapsed_lines = []
        consecutive_blanks = 0
        for line in lines:
            if not line.strip():
                consecutive_blanks += 1
                if consecutive_blanks <= 2:
                    collapsed_lines.append("")
            else:
                consecutive_blanks = 0
                collapsed_lines.append(line)

        result = "\n".join(collapsed_lines).strip()
        return result

    async def extract_text(
        self,
        file: Union[UploadFile, bytes],
        content_type: str | None = None,
    ) -> str:
        """Send document to Azure AI Document Intelligence, poll for completion,

        normalize and return extracted text.
        """
        if isinstance(file, UploadFile):
            file_bytes = await file.read()
            # Rewind file pointer for downstream consumers if needed
            await file.seek(0)
        else:
            file_bytes = file

        if not self.endpoint or not self.key:
            logger.error("Azure Document Intelligence credentials are not configured.")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Document OCR service is temporarily unavailable.",
            )

        try:
            async with DocumentIntelligenceClient(
                endpoint=self.endpoint,
                credential=AzureKeyCredential(self.key),
            ) as client:
                body_io = io.BytesIO(file_bytes)
                poller = await asyncio.wait_for(
                    client.begin_analyze_document(
                        model_id=self.model_id,
                        body=body_io,
                        content_type="application/octet-stream",
                    ),
                    timeout=self.timeout,
                )
                analyze_result = await asyncio.wait_for(
                    poller.result(),
                    timeout=self.timeout,
                )

                extracted_pages = []
                if analyze_result.pages:
                    for page in analyze_result.pages:
                        page_num = page.page_number or (len(extracted_pages) + 1)
                        page_lines = []
                        if page.lines:
                            for line in page.lines:
                                if line.content and line.content.strip():
                                    page_lines.append(line.content.strip())
                        if page_lines:
                            extracted_pages.append(f"Page {page_num}:\n" + "\n".join(page_lines))

                if extracted_pages:
                    raw_text = "\n\n".join(extracted_pages)
                else:
                    raw_text = analyze_result.content or ""

                normalized_text = self.normalize_ocr_text(raw_text)

                if not normalized_text or not normalized_text.strip():
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                        detail="No readable text could be extracted from the document.",
                    )

                return normalized_text

        except HTTPException:
            raise
        except asyncio.TimeoutError:
            logger.warning("Azure OCR request timed out after %s seconds", self.timeout)
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Document analysis timed out. Please try again.",
            )
        except Exception as e:
            # Never log sensitive credentials, headers, or document content
            logger.error("Azure OCR service error: %s", type(e).__name__)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Document OCR service is temporarily unavailable.",
            )


azure_ocr_service = AzureOCRService()
