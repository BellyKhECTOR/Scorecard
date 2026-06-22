"""Document extraction orchestration."""

import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.config import Settings, get_settings
from src.exceptions import ExtractionError
from src.extractors.registry import get_extractor
from src.models import Document, DocumentChunk, QAPair, Topic

logger = logging.getLogger(__name__)


class ExtractionService:
    def __init__(self, db: Session, settings: Settings | None = None):
        self.db = db
        self.settings = settings or get_settings()

    def extract_and_persist(self, document: Document, file_data: bytes) -> None:
        document.extraction_status = "processing"
        self.db.commit()

        extractor = get_extractor(document.file_extension)
        if extractor is None:
            document.extraction_status = "unsupported"
            document.extraction_method = None
            document.extraction_error = f"No extractor for {document.file_extension}"
            self.db.commit()
            logger.info("Unsupported format: %s", document.file_extension)
            return

        try:
            result = extractor.extract(file_data, document.file_extension)
        except Exception as exc:
            document.extraction_status = "failed"
            document.extraction_error = str(exc)[:2000]
            self.db.commit()
            raise ExtractionError(
                "The source file was saved successfully, but text extraction failed. "
                "The document remains available and can be reprocessed."
            ) from exc

        self._clear_existing_extractions(document)

        document.full_text = result.full_text or None
        document.extraction_method = result.method
        document.extraction_status = result.status
        document.extraction_error = "; ".join(result.warnings) if result.warnings else None
        document.extracted_at = datetime.now(timezone.utc)

        topic_map = self._load_topic_map()

        for qa_draft in result.qa_pairs:
            topic_id = topic_map.get(qa_draft.topic_slug) if qa_draft.topic_slug else None
            answer_status = "historical"
            if document.status in ("final", "completed", "submitted"):
                answer_status = "approved" if document.status == "final" else "historical"
            self.db.add(QAPair(
                document_id=document.id,
                topic_id=topic_id,
                source_sheet=qa_draft.source_sheet,
                source_row_number=qa_draft.source_row_number,
                source_page_number=qa_draft.source_page_number,
                section_heading=qa_draft.section_heading,
                question=qa_draft.question,
                answer=qa_draft.answer,
                answer_status=answer_status,
                is_active=True,
            ))

        for chunk_draft in result.chunks:
            self.db.add(DocumentChunk(
                document_id=document.id,
                chunk_index=chunk_draft.chunk_index,
                page_number=chunk_draft.page_number,
                sheet_name=chunk_draft.sheet_name,
                section_heading=chunk_draft.section_heading,
                content_type=chunk_draft.content_type,
                content=chunk_draft.content,
                token_count=chunk_draft.token_count,
            ))

        self.db.commit()
        logger.info(
            "Extraction complete document_id=%s status=%s qa_pairs=%d chunks=%d",
            document.id, result.status, len(result.qa_pairs), len(result.chunks),
        )

    def _clear_existing_extractions(self, document: Document) -> None:
        self.db.query(QAPair).filter(QAPair.document_id == document.id).delete()
        self.db.query(DocumentChunk).filter(DocumentChunk.document_id == document.id).delete()

    def _load_topic_map(self) -> dict[str, int]:
        topics = self.db.execute(select(Topic)).scalars().all()
        return {t.slug: t.id for t in topics}
