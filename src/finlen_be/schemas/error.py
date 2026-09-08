from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Standardized error response returned by all API endpoints."""

    detail: str
    error_code: str | None = None
