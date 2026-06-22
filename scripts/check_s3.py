#!/usr/bin/env python3
"""Check S3 bucket connectivity."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.aws import check_s3_health, get_s3_client
from src.config import get_settings


def main() -> int:
    settings = get_settings()
    print(f"Checking S3 bucket: {settings.s3_bucket}")
    print(f"Region: {settings.aws_region}")
    print(f"Profile: {settings.aws_profile or '(default credential chain)'}")

    try:
        client = get_s3_client(settings)
        client.head_bucket(Bucket=settings.s3_bucket)
        print("SUCCESS: Bucket is accessible.")
        return 0
    except Exception as exc:
        print(f"FAILURE: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
