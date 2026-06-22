"""Integration tests for upload service with mocked S3."""

import uuid
from datetime import date
from unittest.mock import patch

import boto3
import pytest
from moto import mock_aws

from src.config import get_settings
from src.database import SessionLocal
from src.naming import build_canonical_filename, build_s3_key, slugify
from src.services.upload_service import UploadService
from src.validation import compute_sha256


@mock_aws
def test_upload_builds_correct_s3_key():
    """Test S3 key and filename generation for upload."""
    client_name = "EPPF"
    client_slug = slugify(client_name)
    doc_date = date(2025, 6, 30)
    stored = build_canonical_filename(client_slug, "ddq", "domestic-equity", doc_date, "final", ".pdf")
    key = build_s3_key(client_slug, "ddq", 2025, stored)
    assert key == "client=eppf/document_type=ddq/year=2025/eppf_ddq_domestic-equity_20250630_final.pdf"


@mock_aws
def test_s3_upload_and_verify():
    """Test S3 upload with moto mock."""
    from src.aws import upload_document, verify_object_exists, build_upload_metadata

    conn = boto3.client("s3", region_name="eu-north-1")
    conn.create_bucket(
        Bucket="test-bucket",
        CreateBucketConfiguration={"LocationConstraint": "eu-north-1"},
    )

    data = b"test content"
    sha = compute_sha256(data)
    metadata = build_upload_metadata("test.pdf", sha, "eppf", "ddq", "firmwide", "final")

    settings = get_settings()
    with patch.object(settings, "s3_bucket", "test-bucket"):
        result = upload_document(
            file_data=data,
            bucket="test-bucket",
            key="client=eppf/document_type=ddq/year=2025/test.pdf",
            content_type="application/pdf",
            metadata=metadata,
        )
        head = verify_object_exists("test-bucket", "client=eppf/document_type=ddq/year=2025/test.pdf", expected_size=len(data))
        assert head.size_bytes == len(data)
        assert result.etag
