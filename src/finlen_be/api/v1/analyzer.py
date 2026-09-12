import logging
from typing import Annotated
from fastapi import APIRouter, File, HTTPException, UploadFile, status

from finlen_be.api.deps import CurrentUserDep, DocumentAnalyzerServiceDep
from finlen_be.schemas.analyzer import DocumentAnalysisResponse
from finlen_be.schemas.error import ErrorResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analyzer", tags=["Document Analyzer"])


@router.post(
    "/documents",
    response_model=DocumentAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze financial document",
    description=(
        "Upload a financial document (PDF, JPEG, PNG) to extract OCR text via Azure AI Document Intelligence, "
        "analyze financial terms and risks using Google Gemini, and return structured financial literacy insights."
    ),
    responses={
        400: {"model": ErrorResponse, "description": "Unsupported file format or empty file"},
        401: {"model": ErrorResponse, "description": "Authentication required"},
        413: {"model": ErrorResponse, "description": "Document file size exceeds the maximum allowed limit"},
        422: {"model": ErrorResponse, "description": "No readable text could be extracted from the document"},
        502: {"model": ErrorResponse, "description": "Document OCR or analysis service is temporarily unavailable or returned invalid data"},
        504: {"model": ErrorResponse, "description": "Document analysis timed out"},
        500: {"model": ErrorResponse, "description": "An unexpected internal server error occurred"},
    },
)
async def analyze_document(
    file: Annotated[UploadFile, File(description="Financial document file to analyze (PDF, JPEG, or PNG)")],
    current_user: CurrentUserDep,
    service: DocumentAnalyzerServiceDep,
) -> DocumentAnalysisResponse:
    """Analyze an uploaded financial document for an authenticated user."""
    try:
        return await service.analyze(file)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Unexpected error analyzing document: %s", type(e).__name__, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected internal server error occurred.",
        )
