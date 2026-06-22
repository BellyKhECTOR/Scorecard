"""Document library routes."""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.dependencies import get_session, get_settings_dep
from src.config import Settings
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
    if document.extraction_status not in ("failed", "partial", "unsupported"):
        return RedirectResponse(
            url=f"/?message=Document extraction status is {document.extraction_status}",
            status_code=303,
        )
    document.extraction_status = "pending"
    document.extraction_error = "Reprocessing requested. Please re-upload the file."
    db.commit()
    return RedirectResponse(
        url="/?message=Reprocessing flagged. Please re-upload the source file to reprocess.",
        status_code=303,
    )
