#!/usr/bin/env python3
"""Ingest sample documents from sample_documents/ directory."""

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import get_settings
from src.database import SessionLocal
from src.services.upload_service import UploadService

SAMPLE_METADATA = {
    "EPPF Asset Manager Questionnaire Domestic Equity_2025.pdf": {
        "client_name": "EPPF", "document_type": "ddq", "strategy": "domestic-equity",
        "document_date": date(2025, 6, 30), "status": "blank",
    },
    "EPPF Asset Manager Questionnaire Domestic Equity_2025.docx": {
        "client_name": "EPPF", "document_type": "ddq", "strategy": "domestic-equity",
        "document_date": date(2025, 6, 30), "status": "blank",
    },
    "EPPF Asset Manager Questionnaire Domestic Equity_2025 Final.pdf": {
        "client_name": "EPPF", "document_type": "ddq", "strategy": "domestic-equity",
        "document_date": date(2025, 6, 30), "status": "final",
    },
    "Investment Manager DD Questionnaire - 19052026.xlsx": {
        "client_name": "Unknown", "document_type": "ddq", "strategy": "firmwide",
        "document_date": date(2026, 5, 19), "status": "completed",
    },
    "ESG Questionnaire.xlsx": {
        "client_name": "Unknown", "document_type": "esg_questionnaire", "strategy": "firmwide",
        "document_date": date(2025, 1, 1), "status": "completed",
    },
    "Completed_HIM_RI_Questionnaire.xlsx": {
        "client_name": "HIM", "document_type": "ri_questionnaire", "strategy": "firmwide",
        "document_date": date(2025, 1, 1), "status": "completed",
    },
}


def main() -> int:
    settings = get_settings()
    sample_dir = settings.sample_documents_dir
    print(f"Project root: {settings.root}")
    print(f"Sample documents: {sample_dir}")
    if not sample_dir.exists():
        print(f"Sample directory not found: {sample_dir}")
        return 1

    files = [f for f in sample_dir.iterdir() if f.is_file() and not f.name.startswith(".")]
    if not files:
        print("No sample files found. Place acceptance corpus files in sample_documents/.")
        return 1

    print(f"Ingesting {len(files)} sample file(s)...")
    db = SessionLocal()
    success = 0
    failed = 0
    try:
        service = UploadService(db)
        for filepath in files:
            meta = SAMPLE_METADATA.get(filepath.name, {
                "client_name": "Unknown",
                "document_type": "other",
                "strategy": "firmwide",
                "document_date": date.today(),
                "status": "supporting",
            })
            try:
                file_data = filepath.read_bytes()
                doc = service.upload(
                    file_data=file_data,
                    original_filename=filepath.name,
                    **meta,
                )
                print(f"  SUCCESS: {filepath.name} -> {doc.extraction_status}")
                success += 1
            except Exception as exc:
                print(f"  FAILURE: {filepath.name} -> {exc}")
                failed += 1
        print(f"\nSummary: {success} succeeded, {failed} failed")
        return 0 if failed == 0 else 1
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
