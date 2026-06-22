"""Transparent confidence scoring logic."""

from src.services.retrieval_service import RetrievedSource


def compute_confidence(sources: list[RetrievedSource], answer: str) -> tuple[float, str]:
    if not sources:
        return 0.0, "Insufficient evidence"

    if not answer or "insufficient" in answer.lower() or "no reliable" in answer.lower():
        return 0.1, "Insufficient evidence"

    approved = [s for s in sources if s.answer_status == "approved"]
    qa_sources = [s for s in sources if s.source_type == "qa_pair"]

    if len(approved) >= 2:
        answers = {s.answer for s in approved if s.answer}
        if len(answers) <= 1:
            return 0.9, "High"

    if len(approved) == 1:
        return 0.75, "High"

    if len(qa_sources) >= 2:
        answers = {s.answer for s in qa_sources if s.answer}
        if len(answers) == 1:
            return 0.65, "Medium"

    if len(qa_sources) == 1:
        return 0.55, "Medium"

    if len(sources) >= 1:
        statuses = {s.answer_status for s in sources}
        if "approved" not in statuses:
            return 0.35, "Low"
        return 0.45, "Low"

    return 0.1, "Insufficient evidence"
