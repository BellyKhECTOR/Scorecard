"""Retrieval service for AI-assisted answer generation."""

import logging
from dataclasses import dataclass
from datetime import datetime, timezone

from datetime import timedelta
from sqlalchemy.orm import Session

from src.config import Settings, get_settings
from src.models import Document, QAPair
from src.services.search_service import SearchService

logger = logging.getLogger(__name__)


@dataclass
class RetrievedSource:
    source_type: str
    content: str
    question: str | None
    answer: str | None
    client_name: str
    document_name: str
    document_id: str
    page_number: int | None
    sheet_name: str | None
    row_number: int | None
    section_heading: str | None
    answer_status: str | None
    document_date: str | None
    rank_score: float


class RetrievalService:
    def __init__(self, db: Session, settings: Settings | None = None):
        self.db = db
        self.settings = settings or get_settings()
        self.search_service = SearchService(db, settings)

    def retrieve(self, question: str, client: str | None = None, limit: int = 10) -> list[RetrievedSource]:
        search_results = self.search_service.search(question, client=client, limit=limit)
        sources: list[RetrievedSource] = []

        for qa in search_results.qa_matches:
            doc = self.db.get(Document, qa.document_id)
            sources.append(RetrievedSource(
                source_type="qa_pair",
                content=f"Q: {qa.question}\nA: {qa.answer}",
                question=qa.question,
                answer=qa.answer,
                client_name=qa.client_name,
                document_name=qa.document_name,
                document_id=str(qa.document_id),
                page_number=None,
                sheet_name=qa.source_sheet,
                row_number=qa.source_row_number,
                section_heading=qa.section_heading,
                answer_status=qa.answer_status,
                document_date=str(doc.document_date) if doc else None,
                rank_score=qa.rank_score,
            ))

        for doc_match in search_results.document_matches:
            sources.append(RetrievedSource(
                source_type="document_chunk",
                content=doc_match.excerpt,
                question=None,
                answer=None,
                client_name=doc_match.client_name,
                document_name=doc_match.document_name,
                document_id=str(doc_match.document_id),
                page_number=doc_match.page_number,
                sheet_name=doc_match.sheet_name,
                row_number=None,
                section_heading=doc_match.section_heading,
                answer_status=None,
                document_date=None,
                rank_score=doc_match.rank_score,
            ))

        sources.sort(key=lambda s: self._priority_score(s), reverse=True)
        return sources[:limit]

    def _priority_score(self, source: RetrievedSource) -> float:
        score = source.rank_score
        if source.answer_status == "approved":
            score += 5
        if source.source_type == "qa_pair":
            score += 2
        if source.document_date:
            try:
                doc_date = datetime.fromisoformat(source.document_date)
                months_old = (datetime.now(timezone.utc).date() - doc_date.date()).days / 30
                if months_old < 12:
                    score += 2
            except ValueError:
                pass
        return score

    def check_freshness_warnings(self, sources: list[RetrievedSource]) -> list[str]:
        warnings: list[str] = []
        stale_months = self.settings.source_stale_after_months
        cutoff = datetime.now(timezone.utc).date() - timedelta(days=stale_months * 30)

        dates = []
        for s in sources:
            if s.document_date:
                try:
                    dates.append(datetime.fromisoformat(s.document_date).date())
                except ValueError:
                    pass

        if dates and max(dates) < cutoff:
            warnings.append(
                f"The newest source is older than {stale_months} months. "
                "People, AUM, fees, licences or policies may have changed."
            )

        approved = [s for s in sources if s.answer_status == "approved"]
        if sources and not approved:
            warnings.append("No approved sources were found; answers are from historical material only.")

        answers = [s.answer for s in sources if s.answer]
        if len(set(answers)) > 1 and len(answers) > 1:
            warnings.append("Sources contain potentially conflicting information.")

        return warnings
