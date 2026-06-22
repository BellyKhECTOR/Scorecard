"""AWS S3 integration for document storage."""

import logging
from dataclasses import dataclass

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from src.config import Settings, get_settings
from src.exceptions import S3UploadError

logger = logging.getLogger(__name__)

APPLICATION_TAG = "mazi-bd-ddq-platform"


@dataclass
class S3UploadResult:
    bucket: str
    key: str
    version_id: str | None
    etag: str
    size_bytes: int


@dataclass
class HeadObjectResult:
    bucket: str
    key: str
    version_id: str | None
    etag: str
    size_bytes: int
    content_type: str | None


def get_s3_client(settings: Settings | None = None):
    settings = settings or get_settings()
    config = Config(
        region_name=settings.aws_region,
        retries={"max_attempts": 3, "mode": "standard"},
        connect_timeout=10,
        read_timeout=60,
    )
    session_kwargs = {}
    if settings.aws_profile:
        session_kwargs["profile_name"] = settings.aws_profile
    session = boto3.Session(**session_kwargs)
    return session.client("s3", config=config)


def upload_document(
    file_data: bytes,
    bucket: str,
    key: str,
    content_type: str,
    metadata: dict[str, str],
    settings: Settings | None = None,
) -> S3UploadResult:
    """Upload document to S3 with server-side encryption."""
    client = get_s3_client(settings)
    try:
        response = client.put_object(
            Bucket=bucket,
            Key=key,
            Body=file_data,
            ContentType=content_type,
            ServerSideEncryption="AES256",
            Metadata=metadata,
        )
        version_id = response.get("VersionId")
        etag = response.get("ETag", "").strip('"')
        logger.info(
            "S3 upload successful: bucket=%s key=%s size=%d etag=%s",
            bucket, key, len(file_data), etag,
        )
        return S3UploadResult(
            bucket=bucket,
            key=key,
            version_id=version_id,
            etag=etag,
            size_bytes=len(file_data),
        )
    except ClientError as exc:
        raise S3UploadError(f"S3 upload failed for key '{key}': {exc}") from exc


def verify_object_exists(
    bucket: str,
    key: str,
    expected_size: int | None = None,
    version_id: str | None = None,
    settings: Settings | None = None,
) -> HeadObjectResult:
    """Verify uploaded object exists and matches expected size."""
    client = get_s3_client(settings)
    try:
        kwargs: dict = {"Bucket": bucket, "Key": key}
        if version_id:
            kwargs["VersionId"] = version_id
        response = client.head_object(**kwargs)
        size = response.get("ContentLength", 0)
        if expected_size is not None and size != expected_size:
            raise S3UploadError(
                f"S3 object size mismatch: expected {expected_size}, got {size}"
            )
        return HeadObjectResult(
            bucket=bucket,
            key=key,
            version_id=response.get("VersionId"),
            etag=response.get("ETag", "").strip('"'),
            size_bytes=size,
            content_type=response.get("ContentType"),
        )
    except ClientError as exc:
        raise S3UploadError(f"S3 verification failed for key '{key}': {exc}") from exc


def generate_presigned_url(
    bucket: str,
    key: str,
    expiry_seconds: int | None = None,
    version_id: str | None = None,
    settings: Settings | None = None,
) -> str:
    """Generate a short-lived presigned download URL."""
    settings = settings or get_settings()
    client = get_s3_client(settings)
    expiry = expiry_seconds or settings.presigned_url_expiry_seconds
    params: dict = {"Bucket": bucket, "Key": key}
    if version_id:
        params["VersionId"] = version_id
    try:
        return client.generate_presigned_url(
            "get_object",
            Params=params,
            ExpiresIn=expiry,
        )
    except ClientError as exc:
        raise S3UploadError(f"Failed to generate presigned URL: {exc}") from exc


def download_object(
    bucket: str,
    key: str,
    version_id: str | None = None,
    settings: Settings | None = None,
) -> bytes:
    """Download document bytes from S3."""
    client = get_s3_client(settings)
    try:
        kwargs: dict = {"Bucket": bucket, "Key": key}
        if version_id:
            kwargs["VersionId"] = version_id
        response = client.get_object(**kwargs)
        return response["Body"].read()
    except ClientError as exc:
        raise S3UploadError(f"S3 download failed for key '{key}': {exc}") from exc


def check_s3_health(settings: Settings | None = None) -> bool:
    """Check S3 bucket accessibility."""
    settings = settings or get_settings()
    try:
        client = get_s3_client(settings)
        client.head_bucket(Bucket=settings.s3_bucket)
        return True
    except Exception as exc:
        logger.warning("S3 health check failed: %s", exc)
        return False


def build_upload_metadata(
    original_filename: str,
    sha256: str,
    client_slug: str,
    document_type: str,
    strategy: str,
    status: str,
) -> dict[str, str]:
    return {
        "original-filename": original_filename[:200],
        "sha256": sha256,
        "application": APPLICATION_TAG,
        "client-slug": client_slug,
        "document-type": document_type,
        "strategy": strategy,
        "status": status,
    }
