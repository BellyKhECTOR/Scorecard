"""Pydantic schemas for API and service layer."""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field


class DocumentUploadForm(BaseModel):
    client_name: str
    document_type: str
    strategy: str = "firmwide"
    document_date: date
    status: str
    notes: str | None = None


class DocumentResponse(BaseModel):
    id: UUID
    client_name: str
    client_slug: str
    document_type: str
    strategy: str
    document_date: date
    document_year: int
    status: str
    notes: str | None
    original_filename: str
    stored_filename: str
    file_extension: str
    content_type: str
    size_bytes: int
    extraction_status: str
    extraction_method: str | None
    extraction_error: str | None
    uploaded_at: datetime
    source_url: str | None = None

    model_config = {"from_attributes": True}


class QASearchResult(BaseModel):
    id: int
    question: str
    answer: str
    topic: str | None
    client_name: str
    document_id: UUID
    document_name: str
    source_sheet: str | None
    source_row_number: int | None
    section_heading: str | None
    answer_status: str
    rank_score: float
    headline: str | None = None
    source_url: str | None = None


class DocumentSearchResult(BaseModel):
    id: int
    document_id: UUID
    content: str
    excerpt: str
    client_name: str
    document_name: str
    page_number: int | None
    sheet_name: str | None
    section_heading: str | None
    file_extension: str
    rank_score: float
    source_url: str | None = None


class SearchResponse(BaseModel):
    query: str
    qa_matches: list[QASearchResult] = Field(default_factory=list)
    document_matches: list[DocumentSearchResult] = Field(default_factory=list)
    ai_enabled: bool = False
    ai_message: str | None = None


class GeneratedAnswerResponse(BaseModel):
    id: int | None = None
    question: str
    generated_answer: str
    confidence_score: float | None
    confidence_label: str
    sources: list[dict]
    warnings: list[str]
    status: str = "generated"


class FeedbackRequest(BaseModel):
    generated_answer_id: int
    reviewer_action: str
    edited_answer: str | None = None
    feedback_reason: str | None = None
    reviewer_name: str | None = None


class HealthResponse(BaseModel):
    application: str
    database: str
    s3: str
    ai: str
