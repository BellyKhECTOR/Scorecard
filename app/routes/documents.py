"""Document library routes."""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.dependencies import get_session, get_settings_dep
from src.config import Settings
from src.exceptions import ExtractionError, S3UploadError
from src.models import Document
from src.services.upload_service import UploadService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("/{document_id}/download")
async def download_document(
    document_id: UUID,
    db: Session = Depends(get_session),
    settings: Settings = Depends(get_settings_dep),
):
    document = db.get(Document, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found.")
    service = UploadService(db, settings)
    url = service.get_presigned_url(document)
    return RedirectResponse(url=url)


@router.post("/{document_id}/reprocess")
async def reprocess_document(
    document_id: UUID,
    db: Session = Depends(get_session),
    settings: Settings = Depends(get_settings_dep),
):
    document = db.get(Document, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found.")

    service = UploadService(db, settings)
    try:
        document = service.reprocess(document_id)
        msg = (
            f"Reprocessing complete: {document.original_filename} "
            f"(status: {document.extraction_status})"
        )
        return RedirectResponse(url=f"/?message={msg}", status_code=303)
    except S3UploadError as exc:
        logger.exception("S3 download failed during reprocess")
        return RedirectResponse(
            url=f"/?error=Could not download source from S3: {exc}",
            status_code=303,
        )
    except ExtractionError as exc:
        return RedirectResponse(
            url=f"/?error={exc}",
            status_code=303,
        )
    except Exception as exc:
        logger.exception("Reprocess failed")
        return RedirectResponse(
            url=f"/?error=Reprocessing failed: {exc}",
            status_code=303,
        )
