#!/usr/bin/env python3
"""Verify the build is complete and ready for local use."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

REQUIRED_FILES = [
    "pyproject.toml",
    "Run DDQ Knowledge Hub.bat",
    ".env.example",
    "PROJECT_HOME.md",
    "README.md",
    "BUILD_PLAN.md",
    "app/main.py",
    "app/templates/upload.html",
    "app/templates/search.html",
    "app/templates/error.html",
    "src/config.py",
    "src/paths.py",
    "src/aws.py",
    "src/models.py",
    "alembic/versions/001_initial_schema.py",
    "scripts/run_local.py",
    "scripts/ingest_backlog.py",
    "scripts/generate_sample_documents.py",
    "docs/LOCAL_SETUP.md",
    "docs/OPERATIONS.md",
]

SAMPLE_FILES = [
    "EPPF Asset Manager Questionnaire Domestic Equity_2025.pdf",
    "EPPF Asset Manager Questionnaire Domestic Equity_2025.docx",
    "EPPF Asset Manager Questionnaire Domestic Equity_2025 Final.pdf",
    "Investment Manager DD Questionnaire - 19052026.xlsx",
    "ESG Questionnaire.xlsx",
    "Completed_HIM_RI_Questionnaire.xlsx",
]


def main() -> int:
    from src.config import get_settings
    from src.database import check_database_health
    from src.paths import CANONICAL_PROJECT_ROOT

    settings = get_settings()
    root = settings.root
    errors: list[str] = []
    warnings: list[str] = []

    print("=" * 60)
    print(" MAZI BD DDQ KNOWLEDGE HUB — BUILD VERIFICATION")
    print("=" * 60)
    print(f" Project root:  {root}")
    print(f" Canonical:     {CANONICAL_PROJECT_ROOT}")
    print()

    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            errors.append(f"Missing required file: {rel}")

    sample_dir = settings.sample_documents_dir
    for name in SAMPLE_FILES:
        if not (sample_dir / name).exists():
            warnings.append(f"Sample document missing: {name} (run scripts/generate_sample_documents.py)")

    for sub in ("data/backlog", "data/inbox", "data/reports"):
        if not (root / sub).exists():
            warnings.append(f"Data folder missing: {sub}")

    print("Required files:", "OK" if not [e for e in errors if "Missing" in e] else "FAIL")
    print("Sample corpus:", "OK" if not warnings else f"{len(warnings)} missing")
    print("Database:", "OK" if check_database_health() else "FAIL (check PostgreSQL)")
    print("Local only:", "OK" if settings.local_only else "WARN (LOCAL_ONLY should be true)")

    if errors:
        print("\nERRORS:")
        for e in errors:
            print(f"  - {e}")

    if warnings:
        print("\nWARNINGS:")
        for w in warnings:
            print(f"  - {w}")

    if not errors:
        print("\nBUILD VERIFICATION: PASSED")
        print("\nNext steps:")
        print("  1. Ensure .env is configured")
        print("  2. Double-click Run DDQ Knowledge Hub.bat")
        print("  3. Open http://127.0.0.1:8000")
        return 0 if not warnings else 0

    print("\nBUILD VERIFICATION: FAILED")
    return 1


if __name__ == "__main__":
    sys.exit(main())
