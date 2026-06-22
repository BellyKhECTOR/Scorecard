"""File upload validation utilities."""

import hashlib
import mimetypes
from pathlib import Path

from src.exceptions import DocumentValidationError
from src.naming import DOCUMENT_STATUSES, DOCUMENT_TYPES

ALLOWED_EXTENSIONS = {
    ".xlsx", ".xls", ".csv",
    ".docx", ".pdf", ".txt",
    ".html", ".htm", ".pptx",
    ".eml",
    ".png", ".jpg", ".jpeg", ".gif", ".tiff", ".tif", ".bmp",
    ".zip",
}

EXTENSION_MIME_MAP = {
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".xls": "application/vnd.ms-excel",
    ".csv": "text/csv",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".pdf": "application/pdf",
    ".txt": "text/plain",
    ".html": "text/html",
    ".htm": "text/html",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ".eml": "message/rfc822",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".tiff": "image/tiff",
    ".tif": "image/tiff",
    ".bmp": "image/bmp",
    ".zip": "application/zip",
}


def compute_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def get_extension(filename: str) -> str:
    return Path(filename).suffix.lower()


def validate_filename(filename: str) -> None:
    if not filename or filename.strip() == "":
        raise DocumentValidationError("Filename is required.")
    if ".." in filename or "/" in filename or "\\" in filename:
        raise DocumentValidationError("Filename contains invalid path characters.")
    if "\x00" in filename:
        raise DocumentValidationError("Filename contains null bytes.")


def validate_extension(filename: str) -> str:
    ext = get_extension(filename)
    if ext not in ALLOWED_EXTENSIONS:
        raise DocumentValidationError(
            f"File extension '{ext}' is not supported. "
            f"Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )
    return ext


def validate_file_size(size_bytes: int, max_bytes: int) -> None:
    if size_bytes <= 0:
        raise DocumentValidationError("File is empty.")
    if size_bytes > max_bytes:
        max_mb = max_bytes / (1024 * 1024)
        raise DocumentValidationError(
            f"File exceeds maximum upload size of {max_mb:.0f} MB."
        )


def validate_mime_type(filename: str, content_type: str | None) -> str:
    ext = get_extension(filename)
    expected = EXTENSION_MIME_MAP.get(ext)
    if content_type:
        base_type = content_type.split(";")[0].strip().lower()
        guessed = mimetypes.guess_type(filename)[0]
        if expected and base_type not in (expected, guessed, "application/octet-stream"):
            if not (ext in (".xls", ".csv") and "spreadsheet" in base_type):
                raise DocumentValidationError(
                    f"MIME type '{content_type}' does not match extension '{ext}'."
                )
        return base_type
    return expected or mimetypes.guess_type(filename)[0] or "application/octet-stream"


def validate_metadata(
    document_type: str,
    status: str,
    client_name: str,
) -> None:
    if not client_name or not client_name.strip():
        raise DocumentValidationError("Client name is required.")
    if document_type not in DOCUMENT_TYPES:
        raise DocumentValidationError(
            f"Invalid document type '{document_type}'. "
            f"Allowed: {', '.join(sorted(DOCUMENT_TYPES))}"
        )
    if status not in DOCUMENT_STATUSES:
        raise DocumentValidationError(
            f"Invalid status '{status}'. "
            f"Allowed: {', '.join(sorted(DOCUMENT_STATUSES))}"
        )
