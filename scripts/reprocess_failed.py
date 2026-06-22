#!/usr/bin/env python3
"""Reprocess failed document extractions."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select

from src.database import SessionLocal
from src.models import Document


def main() -> int:
    parser = argparse.ArgumentParser(description="List and flag failed extractions for reprocessing")
    parser.add_argument("--document-id", help="Specific document UUID to reprocess")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        if args.document_id:
            doc = db.get(Document, args.document_id)
            if not doc:
                print(f"Document not found: {args.document_id}")
                return 1
            docs = [doc]
        else:
            docs = db.execute(
                select(Document).where(
                    Document.extraction_status.in_(["failed", "partial"])
                )
            ).scalars().all()

        if not docs:
            print("No failed or partial extractions found.")
            return 0

        print(f"Found {len(docs)} document(s) for reprocessing:")
        for doc in docs:
            print(f"  {doc.id} | {doc.original_filename} | {doc.extraction_status}")
            doc.extraction_status = "pending"
            doc.extraction_error = "Queued for reprocessing"

        db.commit()
        print("\nDocuments flagged for reprocessing. Re-upload source files to complete extraction.")
        return 0
    except Exception as exc:
        db.rollback()
        print(f"FAILURE: {exc}")
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
