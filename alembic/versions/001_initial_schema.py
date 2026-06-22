"""Initial schema with extensions, tables, indexes and search triggers."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    op.execute("CREATE EXTENSION IF NOT EXISTS unaccent")

    op.create_table(
        "topics",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("display_name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )

    op.create_table(
        "documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("client_name", sa.String(500), nullable=False),
        sa.Column("client_slug", sa.String(200), nullable=False),
        sa.Column("document_type", sa.String(50), nullable=False),
        sa.Column("strategy", sa.String(200), nullable=False),
        sa.Column("document_date", sa.Date(), nullable=False),
        sa.Column("document_year", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("original_filename", sa.String(500), nullable=False),
        sa.Column("stored_filename", sa.String(500), nullable=False),
        sa.Column("file_extension", sa.String(20), nullable=False),
        sa.Column("content_type", sa.String(200), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("s3_bucket", sa.String(200), nullable=False),
        sa.Column("s3_key", sa.String(1000), nullable=False),
        sa.Column("s3_version_id", sa.String(200), nullable=True),
        sa.Column("s3_etag", sa.String(200), nullable=True),
        sa.Column("content_hash_sha256", sa.String(64), nullable=False),
        sa.Column("extraction_status", sa.String(50), nullable=False),
        sa.Column("extraction_method", sa.String(100), nullable=True),
        sa.Column("extraction_error", sa.Text(), nullable=True),
        sa.Column("full_text", sa.Text(), nullable=True),
        sa.Column("search_vector", postgresql.TSVECTOR(), nullable=True),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("extracted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("s3_bucket", "s3_key", "s3_version_id", name="uq_documents_s3_object"),
    )
    op.create_index("ix_documents_client_slug", "documents", ["client_slug"])
    op.create_index("ix_documents_content_hash", "documents", ["content_hash_sha256"])
    op.create_index("ix_documents_client_type_year", "documents", ["client_slug", "document_type", "document_year"])
    op.create_index("ix_documents_uploaded_at", "documents", ["uploaded_at"])
    op.create_index("ix_documents_search_vector", "documents", ["search_vector"], postgresql_using="gin")

    op.create_table(
        "qa_pairs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("topic_id", sa.Integer(), nullable=True),
        sa.Column("source_sheet", sa.String(200), nullable=True),
        sa.Column("source_row_number", sa.Integer(), nullable=True),
        sa.Column("source_page_number", sa.Integer(), nullable=True),
        sa.Column("section_heading", sa.String(500), nullable=True),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column("question_normalised", sa.Text(), nullable=True),
        sa.Column("answer_status", sa.String(50), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("search_vector", postgresql.TSVECTOR(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["topic_id"], ["topics.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("document_id", "source_sheet", "source_row_number", name="uq_qa_pairs_document_sheet_row"),
    )
    op.create_index("ix_qa_pairs_document_id", "qa_pairs", ["document_id"])
    op.create_index("ix_qa_pairs_topic_id", "qa_pairs", ["topic_id"])
    op.create_index("ix_qa_pairs_search_vector", "qa_pairs", ["search_vector"], postgresql_using="gin")
    op.execute(
        "CREATE INDEX ix_qa_pairs_question_trgm ON qa_pairs "
        "USING gin (question gin_trgm_ops)"
    )

    op.create_table(
        "document_chunks",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("page_number", sa.Integer(), nullable=True),
        sa.Column("sheet_name", sa.String(200), nullable=True),
        sa.Column("section_heading", sa.String(500), nullable=True),
        sa.Column("content_type", sa.String(50), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("token_count", sa.Integer(), nullable=True),
        sa.Column("search_vector", postgresql.TSVECTOR(), nullable=True),
        sa.Column("embedding", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_document_chunks_document_id", "document_chunks", ["document_id"])
    op.create_index("ix_document_chunks_search_vector", "document_chunks", ["search_vector"], postgresql_using="gin")

    op.create_table(
        "generated_answers",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("generated_answer", sa.Text(), nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=True),
        sa.Column("confidence_label", sa.String(50), nullable=True),
        sa.Column("model_provider", sa.String(100), nullable=True),
        sa.Column("model_name", sa.String(200), nullable=True),
        sa.Column("prompt_version", sa.String(50), nullable=True),
        sa.Column("retrieval_query", sa.Text(), nullable=True),
        sa.Column("sources_json", postgresql.JSONB(), nullable=True),
        sa.Column("warnings_json", postgresql.JSONB(), nullable=True),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "answer_feedback",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("generated_answer_id", sa.Integer(), nullable=False),
        sa.Column("reviewer_action", sa.String(50), nullable=False),
        sa.Column("original_generated_answer", sa.Text(), nullable=True),
        sa.Column("edited_answer", sa.Text(), nullable=True),
        sa.Column("feedback_reason", sa.Text(), nullable=True),
        sa.Column("reviewer_name", sa.String(200), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["generated_answer_id"], ["generated_answers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_answer_feedback_generated_answer_id", "answer_feedback", ["generated_answer_id"])

    # Search vector triggers
    op.execute("""
        CREATE OR REPLACE FUNCTION documents_search_vector_update() RETURNS trigger AS $$
        BEGIN
            NEW.search_vector :=
                setweight(to_tsvector('english', coalesce(NEW.client_name, '')), 'B') ||
                setweight(to_tsvector('english', coalesce(NEW.full_text, '')), 'C');
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    op.execute("""
        CREATE TRIGGER documents_search_vector_trigger
        BEFORE INSERT OR UPDATE OF client_name, full_text ON documents
        FOR EACH ROW EXECUTE FUNCTION documents_search_vector_update();
    """)

    op.execute("""
        CREATE OR REPLACE FUNCTION qa_pairs_search_vector_update() RETURNS trigger AS $$
        BEGIN
            NEW.search_vector :=
                setweight(to_tsvector('english', coalesce(NEW.question, '')), 'A') ||
                setweight(to_tsvector('english', coalesce(NEW.answer, '')), 'B') ||
                setweight(to_tsvector('english', coalesce(NEW.section_heading, '')), 'C');
            NEW.question_normalised := lower(regexp_replace(coalesce(NEW.question, ''), '[^a-zA-Z0-9]+', ' ', 'g'));
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    op.execute("""
        CREATE TRIGGER qa_pairs_search_vector_trigger
        BEFORE INSERT OR UPDATE OF question, answer, section_heading ON qa_pairs
        FOR EACH ROW EXECUTE FUNCTION qa_pairs_search_vector_update();
    """)

    op.execute("""
        CREATE OR REPLACE FUNCTION document_chunks_search_vector_update() RETURNS trigger AS $$
        BEGIN
            NEW.search_vector :=
                setweight(to_tsvector('english', coalesce(NEW.content, '')), 'B') ||
                setweight(to_tsvector('english', coalesce(NEW.section_heading, '')), 'C');
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    op.execute("""
        CREATE TRIGGER document_chunks_search_vector_trigger
        BEFORE INSERT OR UPDATE OF content, section_heading ON document_chunks
        FOR EACH ROW EXECUTE FUNCTION document_chunks_search_vector_update();
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS document_chunks_search_vector_trigger ON document_chunks")
    op.execute("DROP FUNCTION IF EXISTS document_chunks_search_vector_update()")
    op.execute("DROP TRIGGER IF EXISTS qa_pairs_search_vector_trigger ON qa_pairs")
    op.execute("DROP FUNCTION IF EXISTS qa_pairs_search_vector_update()")
    op.execute("DROP TRIGGER IF EXISTS documents_search_vector_trigger ON documents")
    op.execute("DROP FUNCTION IF EXISTS documents_search_vector_update()")
    op.drop_table("answer_feedback")
    op.drop_table("generated_answers")
    op.drop_table("document_chunks")
    op.drop_table("qa_pairs")
    op.drop_table("documents")
    op.drop_table("topics")
