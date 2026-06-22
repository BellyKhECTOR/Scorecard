"""AI-assisted answer generation service."""

import logging

from uuid import UUID

from sqlalchemy.orm import Session

from src.ai.openai_provider import get_llm_provider
from src.ai.prompts import PROMPT_VERSION
from src.aws import generate_presigned_url
from src.config import Settings, get_settings
from src.models import Document, GeneratedAnswer
from src.schemas import GeneratedAnswerResponse
from src.services.retrieval_service import RetrievalService

logger = logging.getLogger(__name__)


class AnswerService:
    def __init__(self, db: Session, settings: Settings | None = None):
        self.db = db
        self.settings = settings or get_settings()
        self.retrieval_service = RetrievalService(db, settings)
        self.llm = get_llm_provider(self.settings)

    def draft_answer(
        self,
        question: str,
        client: str | None = None,
    ) -> GeneratedAnswerResponse:
        sources = self.retrieval_service.retrieve(question, client=client)
        freshness_warnings = self.retrieval_service.check_freshness_warnings(sources)

        result = self.llm.generate_answer(question, sources)
        all_warnings = result.warnings + freshness_warnings
        enriched_sources = self._enrich_sources(result.sources)

        if not self.settings.ai_available:
            return GeneratedAnswerResponse(
                question=question,
                generated_answer=result.answer,
                confidence_score=result.confidence_score,
                confidence_label=result.confidence_label,
                sources=enriched_sources,
                warnings=all_warnings,
            )

        record = GeneratedAnswer(
            question=question,
            generated_answer=result.answer,
            confidence_score=result.confidence_score,
            confidence_label=result.confidence_label,
            model_provider=result.model_provider,
            model_name=result.model_name,
            prompt_version=PROMPT_VERSION,
            retrieval_query=question,
            sources_json=enriched_sources,
            warnings_json=all_warnings,
            status="generated",
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)

        return GeneratedAnswerResponse(
            id=record.id,
            question=question,
            generated_answer=result.answer,
            confidence_score=result.confidence_score,
            confidence_label=result.confidence_label,
            sources=enriched_sources,
            warnings=all_warnings,
        )

    def _enrich_sources(self, sources: list[dict]) -> list[dict]:
        enriched = []
        for src in sources:
            item = dict(src)
            doc_id = item.get("document_id")
            if doc_id and not item.get("source_url"):
                try:
                    doc = self.db.get(Document, UUID(str(doc_id)))
                    if doc:
                        item["source_url"] = generate_presigned_url(
                            doc.s3_bucket, doc.s3_key,
                            version_id=doc.s3_version_id,
                            settings=self.settings,
                        )
                except Exception:
                    pass
            enriched.append(item)
        return enriched
