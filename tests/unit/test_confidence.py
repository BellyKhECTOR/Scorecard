"""Unit tests for confidence scoring."""

from src.ai.confidence import compute_confidence
from src.services.retrieval_service import RetrievedSource


def _source(answer_status=None, source_type="qa_pair", answer="test"):
    return RetrievedSource(
        source_type=source_type,
        content=f"A: {answer}",
        question="Q?",
        answer=answer,
        client_name="EPPF",
        document_name="test.xlsx",
        document_id="1",
        page_number=None,
        sheet_name=None,
        row_number=1,
        section_heading=None,
        answer_status=answer_status,
        document_date="2025-01-01",
        rank_score=1.0,
    )


class TestConfidence:
    def test_no_sources(self):
        score, label = compute_confidence([], "answer")
        assert label == "Insufficient evidence"
        assert score == 0.0

    def test_approved_sources(self):
        sources = [_source("approved", answer="Same"), _source("approved", answer="Same")]
        score, label = compute_confidence(sources, "Based on approved sources")
        assert label == "High"

    def test_historical_only(self):
        sources = [_source("historical")]
        score, label = compute_confidence(sources, "answer")
        assert label in ("Medium", "Low")
