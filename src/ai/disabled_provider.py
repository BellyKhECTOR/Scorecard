"""Disabled LLM provider when AI is not configured."""

from src.ai.confidence import compute_confidence
from src.ai.provider import GeneratedAnswerResult
from src.ai.prompts import PROMPT_VERSION
from src.services.retrieval_service import RetrievedSource


class DisabledLLMProvider:
    def generate_answer(
        self,
        question: str,
        context: list[RetrievedSource],
    ) -> GeneratedAnswerResult:
        if not context:
            answer = (
                "No reliable Mazi source was found for this question. "
                "Please upload relevant documents or search the knowledge base manually."
            )
        else:
            best = context[0]
            if best.answer:
                answer = best.answer
            else:
                answer = best.content[:1000]

        score, label = compute_confidence(context, answer)
        sources = [
            {
                "document_name": s.document_name,
                "document_id": s.document_id,
                "client_name": s.client_name,
                "sheet_name": s.sheet_name,
                "row_number": s.row_number,
                "page_number": s.page_number,
                "section_heading": s.section_heading,
            }
            for s in context[:5]
        ]
        warnings = ["AI drafting is disabled. Showing best retrieved source only."]
        return GeneratedAnswerResult(
            answer=answer,
            confidence_score=score,
            confidence_label=label,
            sources=sources,
            warnings=warnings,
            model_provider="disabled",
            model_name="retrieval-only",
        )
