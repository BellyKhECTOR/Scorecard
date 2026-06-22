"""LLM provider protocol and types."""

from dataclasses import dataclass
from typing import Protocol

from src.services.retrieval_service import RetrievedSource


@dataclass
class GeneratedAnswerResult:
    answer: str
    confidence_score: float
    confidence_label: str
    sources: list[dict]
    warnings: list[str]
    model_provider: str
    model_name: str


class LLMProvider(Protocol):
    def generate_answer(
        self,
        question: str,
        context: list[RetrievedSource],
    ) -> GeneratedAnswerResult:
        ...
