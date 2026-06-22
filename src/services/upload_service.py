"""Document upload orchestration service."""

import logging
import uuid
from datetime import date

from sqlalchemy.orm import Session

from src.aws import (
    build_upload_metadata,
    generate_presigned_url,
    upload_document,
    verify_object_exists,
)
from src.config import Settings, get_settings
from src.exceptions import DatabasePersistenceError, DocumentValidationError, S3UploadError
from src.models import Document
from src.naming import build_canonical_filename, build_s3_key, parse_document_year, slugify
from src.services.extraction_service import ExtractionService
from src.validation import (
    compute_sha256,
    validate_extension,
    validate_file_size,
    validate_filename,
    validate_metadata,
    validate_mime_type,
)

logger = logging.getLogger(__name__)


class UploadService:
    def __init__(self, db: Session, settings: Settings | None = None):
        self.db = db
        self.settings = settings or get_settings()
        self.extraction_service = ExtractionService(db, self.settings)

    def upload(
        self,
        file_data: bytes,
        original_filename: str,
        client_name: str,
        document_type: str,
        strategy: str,
        document_date: date,
        status: str,
        notes: str | None = None,
        content_type: str | None = None,
    ) -> Document:
        request_id = str(uuid.uuid4())[:8]
        logger.info(
            "Upload started request_id=%s filename=%s client=%s",
            request_id, original_filename, client_name,
        )

        validate_filename(original_filename)
        validate_metadata(document_type, status, client_name)
        validate_file_size(len(file_data), self.settings.max_upload_bytes)
        extension = validate_extension(original_filename)
        mime_type = validate_mime_type(original_filename, content_type)

        client_slug = slugify(client_name)
        doc_year = parse_document_year(document_date)
        stored_filename = build_canonical_filename(
            client_slug, document_type, strategy, document_date, status, extension
        )
        s3_key = build_s3_key(client_slug, document_type, doc_year, stored_filename)
        sha256 = compute_sha256(file_data)

        existing = (
            self.db.query(Document)
            .filter(Document.content_hash_sha256 == sha256)
            .first()
        )
        if existing:
            logger.info("Duplicate checksum found: %s", existing.id)

        metadata = build_upload_metadata(
            original_filename, sha256, client_slug, document_type, strategy, status
        )

        try:
            upload_result = upload_document(
                file_data=file_data,
                bucket=self.settings.s3_bucket,
                key=s3_key,
                content_type=mime_type,
                metadata=metadata,
                settings=self.settings,
            )
            verify_object_exists(
                bucket=self.settings.s3_bucket,
                key=s3_key,
                expected_size=len(file_data),
                version_id=upload_result.version_id,
                settings=self.settings,
            )
        except S3UploadError:
            logger.exception("S3 upload failed before database record")
            raise

        document = Document(
            id=uuid.uuid4(),
            client_name=client_name.strip(),
            client_slug=client_slug,
            document_type=document_type,
            strategy=strategy or "firmwide",
            document_date=document_date,
            document_year=doc_year,
            status=status,
            notes=notes,
            original_filename=original_filename,
            stored_filename=stored_filename,
            file_extension=extension,
            content_type=mime_type,
            size_bytes=len(file_data),
            s3_bucket=self.settings.s3_bucket,
            s3_key=s3_key,
            s3_version_id=upload_result.version_id,
            s3_etag=upload_result.etag,
            content_hash_sha256=sha256,
            extraction_status="pending",
        )

        try:
            self.db.add(document)
            self.db.commit()
            self.db.refresh(document)
        except Exception as exc:
            self.db.rollback()
            logger.exception(
                "Database record failed; S3 object flagged for reconciliation key=%s", s3_key
            )
            raise DatabasePersistenceError(
                "The database record could not be created. "
                "The newly uploaded S3 object has been flagged for reconciliation."
            ) from exc

        logger.info(
            "Upload complete document_id=%s s3_key=%s", document.id, s3_key
        )

        try:
            self.extraction_service.extract_and_persist(document, file_data)
        except Exception as exc:
            logger.exception("Extraction failed for document %s", document.id)
            document.extraction_status = "failed"
            document.extraction_error = str(exc)[:2000]
            self.db.commit()

        return document

    def get_presigned_url(self, document: Document) -> str:
        return generate_presigned_url(
            bucket=document.s3_bucket,
            key=document.s3_key,
            version_id=document.s3_version_id,
            settings=self.settings,
        )

    def reprocess(self, document_id: uuid.UUID, file_data: bytes | None = None) -> Document:
        document = self.db.get(Document, document_id)
        if not document:
            raise DocumentValidationError("Document not found.")
        if file_data is None:
            raise DocumentValidationError("File data required for reprocessing.")
        document.extraction_status = "processing"
        document.extraction_error = None
        self.db.commit()
        self.extraction_service.extract_and_persist(document, file_data)
        return document
