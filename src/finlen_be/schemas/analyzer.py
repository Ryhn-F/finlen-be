from typing import List, Literal
from pydantic import BaseModel, Field


class FinancialTerms(BaseModel):
    """Authoritative financial numbers extracted from the document."""

    principal: float | None = Field(default=None, description="Principal or initial loan/invoice amount")
    interest_rate: float | None = Field(default=None, description="Interest rate percentage value (e.g. 5 for 5%)")
    interest_period: str | None = Field(default=None, description="Period of interest (e.g. 'monthly', 'annual', 'daily')")
    due_date: str | None = Field(default=None, description="Payment or repayment due date in YYYY-MM-DD or readable format")
    currency: str | None = Field(default=None, description="Currency code (e.g. 'IDR', 'USD')")


class RiskFactor(BaseModel):
    """A financial risk factor identified from the document."""

    title: str = Field(description="Brief title of the risk factor")
    description: str = Field(description="Detailed explanation of the risk factor based on document facts")
    severity: Literal["low", "medium", "high", "critical"] = Field(
        description="Severity level of the identified risk"
    )


class FinancialLiteracyConcept(BaseModel):
    """Educational financial concept explanation tailored to the document."""

    concept: str = Field(description="Financial literacy concept name (e.g. 'Interest Rate', 'Tenor', 'Late Fee')")
    explanation: str = Field(description="Contextual educational explanation for Indonesian users")


class DocumentAnalysis(BaseModel):
    """Structured financial literacy analysis of a financial document."""

    document_type: str = Field(
        description="Type of financial document (e.g. 'loan_agreement', 'paylater_statement', 'invoice', 'bill')"
    )
    summary: str = Field(description="Concise educational summary of the document's key financial terms and context")
    financial_terms: FinancialTerms = Field(
        default_factory=FinancialTerms,
        description="Extracted key financial terms",
    )
    risk_level: Literal["low", "medium", "high", "critical", "unknown"] = Field(
        description="Overall risk level assessment"
    )
    risk_factors: List[RiskFactor] = Field(
        default_factory=list,
        description="List of specific risk factors identified in the document",
    )
    red_flags: List[str] = Field(
        default_factory=list,
        description="Critical warning signs or unusual contractual terms",
    )
    recommended_actions: List[str] = Field(
        default_factory=list,
        description="Practical steps and verification actions recommended before signing or paying",
    )
    financial_literacy: List[FinancialLiteracyConcept] = Field(
        default_factory=list,
        description="Educational concepts explaining the financial implications of this document",
    )


class DocumentAnalysisResponse(BaseModel):
    """API response contract containing structured document analysis."""

    analysis: DocumentAnalysis
