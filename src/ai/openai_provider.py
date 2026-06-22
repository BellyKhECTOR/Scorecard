"""OpenAI-compatible LLM provider."""

import json
import logging

import httpx

from src.ai.confidence import compute_confidence
from src.ai.prompts import PROMPT_VERSION, SYSTEM_PROMPT, build_user_prompt
from src.ai.provider import GeneratedAnswerResult
from src.config import Settings
from src.services.retrieval_service import RetrievedSource

logger = logging.getLogger(__name__)


class OpenAIProvider:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.api_key = settings.llm_api_key.get_secret_value() if settings.llm_api_key else ""
        self.model = settings.llm_model or "gpt-4o-mini"

    def generate_answer(
        self,
        question: str,
        context: list[RetrievedSource],
    ) -> GeneratedAnswerResult:
        if not context:
            return GeneratedAnswerResult(
                answer="No reliable Mazi source was found for this question.",
                confidence_score=0.0,
                confidence_label="Insufficient evidence",
                sources=[],
                warnings=["No matching sources in the knowledge base."],
                model_provider="openai",
                model_name=self.model,
            )

        user_prompt = build_user_prompt(question, context)
        try:
            response = httpx.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                    "temperature": 0.2,
                },
                timeout=60,
            )
            response.raise_for_status()
            answer = response.json()["choices"][0]["message"]["content"]
        except Exception as exc:
            logger.exception("LLM API call failed")
            answer = f"AI generation failed: {exc}. Please review retrieved sources manually."

        score, label = compute_confidence(context, answer)
        sources = [
            {
                "document_name": s.document_name,
                "client_name": s.client_name,
                "sheet_name": s.sheet_name,
                "row_number": s.row_number,
                "page_number": s.page_number,
                "section_heading": s.section_heading,
            }
            for s in context[:5]
        ]
        return GeneratedAnswerResult(
            answer=answer,
            confidence_score=score,
            confidence_label=label,
            sources=sources,
            warnings=[],
            model_provider="openai",
            model_name=self.model,
        )


def get_llm_provider(settings: Settings):
    if not settings.ai_available:
        from src.ai.disabled_provider import DisabledLLMProvider
        return DisabledLLMProvider()
    provider = (settings.llm_provider or "").lower()
    if provider in ("openai", "gpt"):
        return OpenAIProvider(settings)
    from src.ai.disabled_provider import DisabledLLMProvider
    return DisabledLLMProvider()
