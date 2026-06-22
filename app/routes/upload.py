"""Upload routes."""

import logging
from datetime import date

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.dependencies import get_session, get_settings_dep
from src.config import Settings
from src.exceptions import DocumentValidationError, MaziDDQError
from src.naming import DOCUMENT_STATUSES, DOCUMENT_TYPES
from src.services.upload_service import UploadService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["upload"])


@router.get("/", response_class=HTMLResponse)
async def upload_page(request: Request, db: Session = Depends(get_session)):
    from app.main import app
    templates = app.state.templates
    from src.models import Document
    documents = (
        db.query(Document)
        .order_by(Document.uploaded_at.desc())
        .limit(50)
        .all()
    )
    upload_service = UploadService(db)
    doc_rows = []
    for doc in documents:
        try:
            source_url = upload_service.get_presigned_url(doc)
        except Exception:
            source_url = None
        doc_rows.append({"doc": doc, "source_url": source_url})

    return templates.TemplateResponse(
        request,
        "upload.html",
        {
            "document_types": sorted(DOCUMENT_TYPES),
            "statuses": sorted(DOCUMENT_STATUSES),
            "documents": doc_rows,
            "message": request.query_params.get("message"),
            "error": request.query_params.get("error"),
        },
    )


@router.post("/upload")
async def upload_document(
    request: Request,
    client_name: str = Form(...),
    document_type: str = Form(...),
    strategy: str = Form("firmwide"),
    document_date: date = Form(...),
    status: str = Form(...),
    notes: str = Form(""),
    file: UploadFile = File(...),
    db: Session = Depends(get_session),
    settings: Settings = Depends(get_settings_dep),
):
    try:
        file_data = await file.read()
        if len(file_data) > settings.max_upload_bytes:
            raise DocumentValidationError(
                f"File exceeds maximum upload size of {settings.max_upload_size_mb} MB."
            )

        service = UploadService(db, settings)
        document = service.upload(
            file_data=file_data,
            original_filename=file.filename or "unknown",
            client_name=client_name,
            document_type=document_type,
            strategy=strategy,
            document_date=document_date,
            status=status,
            notes=notes or None,
            content_type=file.content_type,
        )
        msg = (
            f"Upload successful: {document.original_filename} "
            f"(extraction: {document.extraction_status})"
        )
        return RedirectResponse(url=f"/?message={msg}", status_code=303)
    except DocumentValidationError as exc:
        return RedirectResponse(url=f"/?error={exc}", status_code=303)
    except MaziDDQError as exc:
        logger.exception("Upload failed")
        return RedirectResponse(url=f"/?error={exc}", status_code=303)
    except Exception as exc:
        logger.exception("Unexpected upload error")
        return RedirectResponse(
            url="/?error=Upload failed before any S3 change was made.",
            status_code=303,
        )
