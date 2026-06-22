"""Reviewer feedback capture service."""

import logging

from sqlalchemy.orm import Session

from src.models import AnswerFeedback, GeneratedAnswer

logger = logging.getLogger(__name__)

VALID_ACTIONS = {
    "accepted",
    "edited",
    "rejected",
    "escalated",
    "outdated",
    "incorrect",
    "replaced",
}


class FeedbackService:
    def __init__(self, db: Session):
        self.db = db

    def submit_feedback(
        self,
        generated_answer_id: int,
        reviewer_action: str,
        edited_answer: str | None = None,
        feedback_reason: str | None = None,
        reviewer_name: str | None = None,
    ) -> AnswerFeedback:
        if reviewer_action not in VALID_ACTIONS:
            raise ValueError(f"Invalid reviewer action: {reviewer_action}")

        answer = self.db.get(GeneratedAnswer, generated_answer_id)
        if not answer:
            raise ValueError("Generated answer not found.")

        feedback = AnswerFeedback(
            generated_answer_id=generated_answer_id,
            reviewer_action=reviewer_action,
            original_generated_answer=answer.generated_answer,
            edited_answer=edited_answer,
            feedback_reason=feedback_reason,
            reviewer_name=reviewer_name,
        )

        status_map = {
            "accepted": "accepted",
            "edited": "edited",
            "rejected": "rejected",
            "escalated": "escalated",
            "outdated": "rejected",
            "incorrect": "rejected",
            "replaced": "edited",
        }
        answer.status = status_map.get(reviewer_action, answer.status)
        if reviewer_action == "edited" and edited_answer:
            answer.generated_answer = edited_answer

        self.db.add(feedback)
        self.db.commit()
        self.db.refresh(feedback)
        logger.info(
            "Feedback recorded answer_id=%s action=%s", generated_answer_id, reviewer_action
        )
        return feedback
