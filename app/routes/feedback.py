"""Feedback routes."""

import logging

from fastapi import APIRouter, Depends, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.dependencies import get_session
from src.services.feedback_service import FeedbackService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("/")
async def submit_feedback(
    generated_answer_id: int = Form(...),
    reviewer_action: str = Form(...),
    edited_answer: str = Form(""),
    feedback_reason: str = Form(""),
    reviewer_name: str = Form(""),
    return_query: str = Form(""),
    db: Session = Depends(get_session),
):
    try:
        service = FeedbackService(db)
        service.submit_feedback(
            generated_answer_id=generated_answer_id,
            reviewer_action=reviewer_action,
            edited_answer=edited_answer or None,
            feedback_reason=feedback_reason or None,
            reviewer_name=reviewer_name or None,
        )
        q = return_query or ""
        return RedirectResponse(
            url=f"/search?q={q}&message=Feedback recorded: {reviewer_action}",
            status_code=303,
        )
    except Exception as exc:
        logger.exception("Feedback submission failed")
        return RedirectResponse(url=f"/search?error={exc}", status_code=303)
