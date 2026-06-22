"""Filename, slug and S3 key generation."""

import re
from datetime import date, datetime

SLUG_PATTERN = re.compile(r"[^a-z0-9]+")

DOCUMENT_TYPES = {
    "ddq",
    "esg_questionnaire",
    "ri_questionnaire",
    "operational_dd",
    "supporting_document",
    "policy",
    "other",
}

DOCUMENT_STATUSES = {
    "blank",
    "draft",
    "completed",
    "submitted",
    "final",
    "supporting",
    "archived",
}


def slugify(value: str) -> str:
    """Convert text to a safe lowercase slug."""
    if not value:
        return "unknown"
    slug = SLUG_PATTERN.sub("-", value.lower().strip())
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug or "unknown"


def build_canonical_filename(
    client_slug: str,
    document_type: str,
    strategy: str,
    document_date: date,
    status: str,
    extension: str,
) -> str:
    """Build canonical stored filename."""
    ext = extension.lstrip(".").lower()
    date_str = document_date.strftime("%Y%m%d")
    return (
        f"{client_slug}_{document_type}_{slugify(strategy)}_"
        f"{date_str}_{status}.{ext}"
    )


def build_s3_key(
    client_slug: str,
    document_type: str,
    document_year: int,
    stored_filename: str,
) -> str:
    """Build S3 object key following required convention."""
    safe_filename = stored_filename.replace("/", "-").replace("\\", "-")
    if ".." in safe_filename:
        raise ValueError("Invalid filename: path traversal detected")
    return (
        f"client={client_slug}/document_type={document_type}/"
        f"year={document_year}/{safe_filename}"
    )


def parse_document_year(document_date: date | datetime) -> int:
    if isinstance(document_date, datetime):
        return document_date.year
    return document_date.year
