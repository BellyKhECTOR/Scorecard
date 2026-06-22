"""SQLAlchemy ORM models."""

import uuid
from datetime import date, datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Topic(Base):
    __tablename__ = "topics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    qa_pairs: Mapped[list["QAPair"]] = relationship(back_populates="topic")


class Document(Base):
    __tablename__ = "documents"
    __table_args__ = (
        UniqueConstraint("s3_bucket", "s3_key", "s3_version_id", name="uq_documents_s3_object"),
        Index("ix_documents_client_type_year", "client_slug", "document_type", "document_year"),
        Index("ix_documents_uploaded_at", "uploaded_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    client_name: Mapped[str] = mapped_column(String(500), nullable=False)
    client_slug: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    document_type: Mapped[str] = mapped_column(String(50), nullable=False)
    strategy: Mapped[str] = mapped_column(String(200), nullable=False, default="firmwide")
    document_date: Mapped[date] = mapped_column(Date, nullable=False)
    document_year: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
    original_filename: Mapped[str] = mapped_column(String(500), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(500), nullable=False)
    file_extension: Mapped[str] = mapped_column(String(20), nullable=False)
    content_type: Mapped[str] = mapped_column(String(200), nullable=False)
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    s3_bucket: Mapped[str] = mapped_column(String(200), nullable=False)
    s3_key: Mapped[str] = mapped_column(String(1000), nullable=False)
    s3_version_id: Mapped[str | None] = mapped_column(String(200))
    s3_etag: Mapped[str | None] = mapped_column(String(200))
    content_hash_sha256: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    extraction_status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    extraction_method: Mapped[str | None] = mapped_column(String(100))
    extraction_error: Mapped[str | None] = mapped_column(Text)
    full_text: Mapped[str | None] = mapped_column(Text)
    search_vector: Mapped[str | None] = mapped_column(TSVECTOR)
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    extracted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    qa_pairs: Mapped[list["QAPair"]] = relationship(back_populates="document", cascade="all, delete-orphan")
    chunks: Mapped[list["DocumentChunk"]] = relationship(back_populates="document", cascade="all, delete-orphan")


class QAPair(Base):
    __tablename__ = "qa_pairs"
    __table_args__ = (
        UniqueConstraint(
            "document_id", "source_sheet", "source_row_number",
            name="uq_qa_pairs_document_sheet_row",
        ),
        Index("ix_qa_pairs_search_vector", "search_vector", postgresql_using="gin"),
        Index("ix_qa_pairs_question_trgm", "question", postgresql_using="gin", postgresql_ops={"question": "gin_trgm_ops"}),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    topic_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("topics.id"), index=True)
    source_sheet: Mapped[str | None] = mapped_column(String(200))
    source_row_number: Mapped[int | None] = mapped_column(Integer)
    source_page_number: Mapped[int | None] = mapped_column(Integer)
    section_heading: Mapped[str | None] = mapped_column(String(500))
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    question_normalised: Mapped[str | None] = mapped_column(Text)
    answer_status: Mapped[str] = mapped_column(String(50), nullable=False, default="historical")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    search_vector: Mapped[str | None] = mapped_column(TSVECTOR)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    document: Mapped["Document"] = relationship(back_populates="qa_pairs")
    topic: Mapped["Topic | None"] = relationship(back_populates="qa_pairs")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    __table_args__ = (
        Index("ix_document_chunks_search_vector", "search_vector", postgresql_using="gin"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    page_number: Mapped[int | None] = mapped_column(Integer)
    sheet_name: Mapped[str | None] = mapped_column(String(200))
    section_heading: Mapped[str | None] = mapped_column(String(500))
    content_type: Mapped[str] = mapped_column(String(50), nullable=False, default="text")
    content: Mapped[str] = mapped_column(Text, nullable=False)
    token_count: Mapped[int | None] = mapped_column(Integer)
    search_vector: Mapped[str | None] = mapped_column(TSVECTOR)
    embedding: Mapped[list[float] | None] = mapped_column(JSONB)  # nullable; pgvector optional
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    document: Mapped["Document"] = relationship(back_populates="chunks")


class GeneratedAnswer(Base):
    __tablename__ = "generated_answers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    generated_answer: Mapped[str] = mapped_column(Text, nullable=False)
    confidence_score: Mapped[float | None] = mapped_column(Float)
    confidence_label: Mapped[str | None] = mapped_column(String(50))
    model_provider: Mapped[str | None] = mapped_column(String(100))
    model_name: Mapped[str | None] = mapped_column(String(200))
    prompt_version: Mapped[str | None] = mapped_column(String(50))
    retrieval_query: Mapped[str | None] = mapped_column(Text)
    sources_json: Mapped[dict | None] = mapped_column(JSONB)
    warnings_json: Mapped[list | None] = mapped_column(JSONB)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="generated")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    feedback: Mapped[list["AnswerFeedback"]] = relationship(back_populates="generated_answer", cascade="all, delete-orphan")


class AnswerFeedback(Base):
    __tablename__ = "answer_feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    generated_answer_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("generated_answers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    reviewer_action: Mapped[str] = mapped_column(String(50), nullable=False)
    original_generated_answer: Mapped[str | None] = mapped_column(Text)
    edited_answer: Mapped[str | None] = mapped_column(Text)
    feedback_reason: Mapped[str | None] = mapped_column(Text)
    reviewer_name: Mapped[str | None] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    generated_answer: Mapped["GeneratedAnswer"] = relationship(back_populates="feedback")
