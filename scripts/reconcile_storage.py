#!/usr/bin/env python3
"""Reconcile S3 objects with database records."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select

from src.aws import get_s3_client
from src.config import get_settings
from src.database import SessionLocal
from src.models import Document


def main() -> int:
    settings = get_settings()
    print("Reconciliation Report")
    print("=" * 50)

    db = SessionLocal()
    try:
        documents = db.execute(select(Document)).scalars().all()
        db_keys = {(d.s3_bucket, d.s3_key): d for d in documents}

        print(f"\nDatabase documents: {len(documents)}")

        failed_extractions = [d for d in documents if d.extraction_status == "failed"]
        print(f"Failed extractions: {len(failed_extractions)}")
        for d in failed_extractions[:10]:
            print(f"  - {d.id} | {d.original_filename} | {d.extraction_error}")

        partial = [d for d in documents if d.extraction_status == "partial"]
        print(f"Partial extractions: {len(partial)}")

        from collections import Counter
        hashes = Counter(d.content_hash_sha256 for d in documents)
        duplicates = {h: c for h, c in hashes.items() if c > 1}
        print(f"\nDuplicate checksums: {len(duplicates)}")
        for h, count in list(duplicates.items())[:5]:
            print(f"  - {h[:16]}... ({count} documents)")

        try:
            client = get_s3_client(settings)
            prefix = "client="
            paginator = client.get_paginator("list_objects_v2")
            s3_keys = set()
            for page in paginator.paginate(Bucket=settings.s3_bucket, Prefix=prefix):
                for obj in page.get("Contents", []):
                    s3_keys.add(obj["Key"])

            db_s3_keys = {d.s3_key for d in documents}
            orphan_s3 = s3_keys - db_s3_keys
            missing_s3 = db_s3_keys - s3_keys

            print(f"\nS3 objects (ddq prefix): {len(s3_keys)}")
            print(f"S3 objects without DB record: {len(orphan_s3)}")
            for key in list(orphan_s3)[:5]:
                print(f"  - {key}")
            print(f"DB records with missing S3 object: {len(missing_s3)}")
            for key in list(missing_s3)[:5]:
                print(f"  - {key}")
        except Exception as exc:
            print(f"\nS3 listing skipped: {exc}")

        print("\nReconciliation complete.")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
