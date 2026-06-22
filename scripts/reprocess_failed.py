"""Reprocess failed document extractions."""

import argparse
import sys
from pathlib import Path
from uuid import UUID

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select

from src.database import SessionLocal
from src.models import Document
from src.services.upload_service import UploadService


def main() -> int:
    parser = argparse.ArgumentParser(description="Reprocess failed document extractions from S3")
    parser.add_argument("--document-id", help="Specific document UUID to reprocess")
    parser.add_argument("--all-failed", action="store_true", help="Reprocess all failed/partial docs")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        service = UploadService(db)

        if args.document_id:
            doc = db.get(Document, UUID(args.document_id))
            if not doc:
                print(f"Document not found: {args.document_id}")
                return 1
            docs = [doc]
        elif args.all_failed:
            docs = db.execute(
                select(Document).where(
                    Document.extraction_status.in_(["failed", "partial", "unsupported"])
                )
            ).scalars().all()
        else:
            docs = db.execute(
                select(Document).where(Document.extraction_status == "failed")
            ).scalars().all()

        if not docs:
            print("No documents to reprocess.")
            return 0

        print(f"Reprocessing {len(docs)} document(s)...")
        success = 0
        failed = 0
        for doc in docs:
            try:
                service.reprocess(doc.id)
                db.refresh(doc)
                print(f"  SUCCESS: {doc.original_filename} -> {doc.extraction_status}")
                success += 1
            except Exception as exc:
                print(f"  FAILURE: {doc.original_filename} -> {exc}")
                failed += 1

        print(f"\nSummary: {success} succeeded, {failed} failed")
        return 0 if failed == 0 else 1
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
