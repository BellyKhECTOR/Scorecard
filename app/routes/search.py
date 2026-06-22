"""Search and draft answer routes."""

import logging

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session

from app.dependencies import get_session, get_settings_dep
from src.config import Settings
from src.naming import DOCUMENT_STATUSES, DOCUMENT_TYPES
from src.models import Topic
from src.services.answer_service import AnswerService
from src.services.search_service import SearchService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["search"])


@router.get("/search", response_class=HTMLResponse)
async def search_page(
    request: Request,
    q: str = "",
    client: str = "",
    document_type: str = "",
    topic: str = "",
    year: str = "",
    status: str = "",
    db: Session = Depends(get_session),
    settings: Settings = Depends(get_settings_dep),
):
    from app.main import app
    templates = app.state.templates

    results = None
    draft = None
    if q.strip():
        search_service = SearchService(db, settings)
        results = search_service.search(
            query=q,
            client=client or None,
            document_type=document_type or None,
            topic=topic or None,
            year=int(year) if year else None,
            status=status or None,
        )
        answer_service = AnswerService(db, settings)
        draft = answer_service.draft_answer(q, client=client or None)

    topics = db.query(Topic).order_by(Topic.display_name).all()

    return templates.TemplateResponse(
        "search.html",
        {
            "request": request,
            "query": q,
            "client": client,
            "document_type": document_type,
            "topic": topic,
            "year": year,
            "status": status,
            "document_types": sorted(DOCUMENT_TYPES),
            "statuses": sorted(DOCUMENT_STATUSES),
            "topics": topics,
            "results": results,
            "draft": draft,
            "ai_enabled": settings.ai_available,
        },
    )


@router.post("/api/search")
async def api_search(
    q: str = Form(...),
    client: str = Form(""),
    document_type: str = Form(""),
    topic: str = Form(""),
    year: str = Form(""),
    status: str = Form(""),
    db: Session = Depends(get_session),
    settings: Settings = Depends(get_settings_dep),
):
    search_service = SearchService(db, settings)
    results = search_service.search(
        query=q,
        client=client or None,
        document_type=document_type or None,
        topic=topic or None,
        year=int(year) if year else None,
        status=status or None,
    )
    return JSONResponse(content=results.model_dump())
