"""Tests for feedback service."""

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from src.services.feedback_service import FeedbackService


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE generated_answers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                generated_answer TEXT NOT NULL,
                confidence_score REAL,
                confidence_label TEXT,
                model_provider TEXT,
                model_name TEXT,
                prompt_version TEXT,
                retrieval_query TEXT,
                sources_json TEXT,
                warnings_json TEXT,
                status TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """))
        conn.execute(text("""
            CREATE TABLE answer_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                generated_answer_id INTEGER NOT NULL,
                reviewer_action TEXT NOT NULL,
                original_generated_answer TEXT,
                edited_answer TEXT,
                feedback_reason TEXT,
                reviewer_name TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """))
        conn.execute(text(
            "INSERT INTO generated_answers (question, generated_answer, status) "
            "VALUES ('Test?', 'Test answer', 'generated')"
        ))
        conn.commit()
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


class TestFeedbackService:
    def test_submit_accepted(self, db_session):
        service = FeedbackService(db_session)
        feedback = service.submit_feedback(
            generated_answer_id=1,
            reviewer_action="accepted",
            reviewer_name="Tester",
        )
        assert feedback.reviewer_action == "accepted"
        row = db_session.execute(text("SELECT status FROM generated_answers WHERE id=1")).fetchone()
        assert row[0] == "accepted"

    def test_submit_rejected(self, db_session):
        service = FeedbackService(db_session)
        service.submit_feedback(
            generated_answer_id=1,
            reviewer_action="rejected",
            feedback_reason="Incorrect",
        )
        row = db_session.execute(text("SELECT status FROM generated_answers WHERE id=1")).fetchone()
        assert row[0] == "rejected"

    def test_invalid_action(self, db_session):
        service = FeedbackService(db_session)
        with pytest.raises(ValueError):
            service.submit_feedback(1, "invalid_action")
