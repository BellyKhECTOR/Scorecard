"""PostgreSQL full-text search service."""

import logging
from uuid import UUID

from sqlalchemy import func, or_, text
from sqlalchemy.orm import Session

from src.aws import generate_presigned_url
from src.config import Settings, get_settings
from src.models import Document, DocumentChunk, QAPair, Topic
from src.schemas import DocumentSearchResult, QASearchResult, SearchResponse

logger = logging.getLogger(__name__)


class SearchService:
    def __init__(self, db: Session, settings: Settings | None = None):
        self.db = db
        self.settings = settings or get_settings()

    def search(
        self,
        query: str,
        client: str | None = None,
        document_type: str | None = None,
        topic: str | None = None,
        year: int | None = None,
        status: str | None = None,
        limit: int = 25,
    ) -> SearchResponse:
        if not query or not query.strip():
            return SearchResponse(query=query, ai_enabled=self.settings.ai_available)

        qa_matches = self._search_qa(query, client, document_type, topic, year, status, limit)
        doc_matches = self._search_documents(query, client, document_type, year, status, limit)

        ai_message = None
        if not self.settings.ai_available:
            ai_message = "AI drafting is unavailable, but document search is still working."

        return SearchResponse(
            query=query,
            qa_matches=qa_matches,
            document_matches=doc_matches,
            ai_enabled=self.settings.ai_available,
            ai_message=ai_message,
        )

    def _search_qa(
        self, query, client, document_type, topic, year, status, limit
    ) -> list[QASearchResult]:
        ts_query = func.websearch_to_tsquery("english", query)

        q = (
            self.db.query(
                QAPair,
                Document,
                Topic,
                func.ts_rank_cd(QAPair.search_vector, ts_query).label("rank"),
                func.ts_headline(
                    "english", QAPair.answer, ts_query,
                    "MaxWords=50, MinWords=15, StartSel=<mark>, StopSel=</mark>"
                ).label("headline"),
                func.similarity(QAPair.question, query).label("trgm_sim"),
            )
            .join(Document, QAPair.document_id == Document.id)
            .outerjoin(Topic, QAPair.topic_id == Topic.id)
            .filter(QAPair.is_active == True)
            .filter(
                or_(
                    QAPair.search_vector.op("@@")(ts_query),
                    func.similarity(QAPair.question, query) > 0.3,
                )
            )
        )

        q = self._apply_document_filters(q, Document, client, document_type, year, status)
        if topic:
            q = q.filter(Topic.slug == topic)

        q = q.order_by(
            func.similarity(QAPair.question, query).desc(),
            QAPair.answer_status.desc(),
            text("rank DESC"),
        ).limit(limit)

        results: list[QASearchResult] = []
        for row in q.all():
            qa, doc, top, rank, headline, trgm_sim = row
            boost = self._qa_rank_boost(qa, doc, trgm_sim or 0)
            source_url = self._presigned(doc)
            results.append(QASearchResult(
                id=qa.id,
                question=qa.question,
                answer=qa.answer,
                topic=top.display_name if top else None,
                client_name=doc.client_name,
                document_id=doc.id,
                document_name=doc.original_filename,
                source_sheet=qa.source_sheet,
                source_row_number=qa.source_row_number,
                section_heading=qa.section_heading,
                answer_status=qa.answer_status,
                rank_score=float(rank or 0) + boost,
                headline=headline,
                source_url=source_url,
            ))

        results.sort(key=lambda r: r.rank_score, reverse=True)
        return results

    def _search_documents(
        self, query, client, document_type, year, status, limit
    ) -> list[DocumentSearchResult]:
        ts_query = func.websearch_to_tsquery("english", query)

        chunk_q = (
            self.db.query(
                DocumentChunk,
                Document,
                func.ts_rank_cd(DocumentChunk.search_vector, ts_query).label("rank"),
                func.ts_headline(
                    "english", DocumentChunk.content, ts_query,
                    "MaxWords=60, MinWords=20, StartSel=<mark>, StopSel=</mark>"
                ).label("headline"),
            )
            .join(Document, DocumentChunk.document_id == Document.id)
            .filter(DocumentChunk.search_vector.op("@@")(ts_query))
        )
        chunk_q = self._apply_document_filters(chunk_q, Document, client, document_type, year, status)
        chunk_q = chunk_q.order_by(text("rank DESC")).limit(limit)

        results: list[DocumentSearchResult] = []
        seen_docs: set[UUID] = set()

        for row in chunk_q.all():
            chunk, doc, rank, headline = row
            if doc.id in seen_docs:
                continue
            seen_docs.add(doc.id)
            results.append(DocumentSearchResult(
                id=chunk.id,
                document_id=doc.id,
                content=chunk.content,
                excerpt=headline or chunk.content[:300],
                client_name=doc.client_name,
                document_name=doc.original_filename,
                page_number=chunk.page_number,
                sheet_name=chunk.sheet_name,
                section_heading=chunk.section_heading,
                file_extension=doc.file_extension,
                rank_score=float(rank or 0),
                source_url=self._presigned(doc),
            ))

        if len(results) < limit:
            doc_q = (
                self.db.query(
                    Document,
                    func.ts_rank_cd(Document.search_vector, ts_query).label("rank"),
                    func.ts_headline(
                        "english", Document.full_text, ts_query,
                        "MaxWords=60, MinWords=20, StartSel=<mark>, StopSel=</mark>"
                    ).label("headline"),
                )
                .filter(Document.search_vector.op("@@")(ts_query))
                .filter(Document.full_text.isnot(None))
            )
            doc_q = self._apply_document_filters(doc_q, Document, client, document_type, year, status)
            doc_q = doc_q.order_by(text("rank DESC")).limit(limit - len(results))

            for row in doc_q.all():
                doc, rank, headline = row
                if doc.id in seen_docs:
                    continue
                results.append(DocumentSearchResult(
                    id=0,
                    document_id=doc.id,
                    content=doc.full_text or "",
                    excerpt=headline or (doc.full_text or "")[:300],
                    client_name=doc.client_name,
                    document_name=doc.original_filename,
                    page_number=None,
                    sheet_name=None,
                    section_heading=None,
                    file_extension=doc.file_extension,
                    rank_score=float(rank or 0),
                    source_url=self._presigned(doc),
                ))

        return results

    def _apply_document_filters(self, q, Document, client, document_type, year, status):
        if client:
            q = q.filter(Document.client_slug == client)
        if document_type:
            q = q.filter(Document.document_type == document_type)
        if year:
            q = q.filter(Document.document_year == year)
        if status:
            q = q.filter(Document.status == status)
        return q

    def _qa_rank_boost(self, qa: QAPair, doc: Document, trgm_sim: float) -> float:
        boost = trgm_sim * 2
        if qa.answer_status == "approved":
            boost += 3.0
        elif qa.answer_status == "historical":
            boost += 1.0
        if doc.status == "final":
            boost += 1.5
        if trgm_sim > 0.8:
            boost += 5.0
        return boost

    def _presigned(self, doc: Document) -> str:
        try:
            return generate_presigned_url(
                doc.s3_bucket, doc.s3_key, version_id=doc.s3_version_id, settings=self.settings
            )
        except Exception:
            return ""
