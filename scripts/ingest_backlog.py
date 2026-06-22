#!/usr/bin/env python3
"""Batch ingest documents from a directory with dry-run and confirmation."""

import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select

from src.config import get_settings
from src.database import SessionLocal
from src.models import Document
from src.naming import build_canonical_filename, build_s3_key, slugify
from src.services.upload_service import UploadService
from src.validation import ALLOWED_EXTENSIONS, compute_sha256, get_extension


def scan_directory(root: Path, recursive: bool) -> list[Path]:
    if recursive:
        return [f for f in root.rglob("*") if f.is_file() and not f.name.startswith(".")]
    return [f for f in root.iterdir() if f.is_file() and not f.name.startswith(".")]


def infer_client(filepath: Path) -> str:
    parts = filepath.parts
    for part in parts:
        if part.lower().startswith("client="):
            return part.split("=", 1)[1]
    name = filepath.stem.lower()
    if "eppf" in name:
        return "EPPF"
    if "him" in name:
        return "HIM"
    return "Unknown"


def main() -> int:
    settings = get_settings()
    parser = argparse.ArgumentParser(description="Batch ingest DDQ documents")
    parser.add_argument(
        "directory",
        type=Path,
        nargs="?",
        default=settings.backlog_dir,
        help=f"Directory to scan (default: {settings.backlog_dir})",
    )
    parser.add_argument("--recursive", "-r", action="store_true", help="Scan recursively")
    parser.add_argument("--dry-run", action="store_true", help="Preview without uploading")
    parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation prompt")
    parser.add_argument("--client", default=None, help="Default client name")
    parser.add_argument("--document-type", default="other", help="Default document type")
    parser.add_argument("--strategy", default="firmwide", help="Default strategy")
    parser.add_argument("--status", default="supporting", help="Default status")
    parser.add_argument("--document-date", default=None, help="Default date YYYY-MM-DD")
    parser.add_argument(
        "--report",
        default=str(settings.reports_dir / "ingest_failures.json"),
        help="Failure report path",
    )
    args = parser.parse_args()

    print(f"Project root: {settings.root}")
    print(f"Scanning:     {args.directory}")

    if not args.directory.exists():
        print(f"FAILURE: Directory not found: {args.directory}")
        return 1

    files = scan_directory(args.directory, args.recursive)
    default_date = (
        datetime.strptime(args.document_date, "%Y-%m-%d").date()
        if args.document_date else date.today()
    )

    ext_counts: Counter = Counter()
    client_counts: Counter = Counter()
    valid_files: list[Path] = []
    unsupported_files: list[Path] = []
    invalid_files: list[Path] = []
    intended_keys: list[str] = []
    checksum_dupes: list[str] = []

    db = SessionLocal()
    existing_hashes = {
        r[0] for r in db.execute(select(Document.content_hash_sha256)).all()
    }

    for f in files:
        ext = get_extension(f.name)
        ext_counts[ext or "(none)"] += 1
        client = args.client or infer_client(f)
        client_counts[client] += 1

        if ext not in ALLOWED_EXTENSIONS:
            unsupported_files.append(f)
            continue

        try:
            data = f.read_bytes()
            sha = compute_sha256(data)
            if sha in existing_hashes:
                checksum_dupes.append(f.name)
            client_slug = slugify(client)
            stored = build_canonical_filename(
                client_slug, args.document_type, args.strategy,
                default_date, args.status, ext,
            )
            key = build_s3_key(client_slug, args.document_type, default_date.year, stored)
            intended_keys.append(key)
            valid_files.append(f)
        except Exception:
            invalid_files.append(f)

    print("=" * 60)
    print("BACKLOG INGESTION PRE-FLIGHT REPORT")
    print("=" * 60)
    print(f"Directory: {args.directory}")
    print(f"Total files: {len(files)}")
    print(f"\nFiles by extension:")
    for ext, count in ext_counts.most_common():
        print(f"  {ext}: {count}")
    print(f"\nFiles by client (inferred):")
    for client, count in client_counts.most_common():
        print(f"  {client}: {count}")
    print(f"\nValid files: {len(valid_files)}")
    print(f"Unsupported files: {len(unsupported_files)}")
    print(f"Invalid files: {len(invalid_files)}")
    print(f"Checksum duplicates (skip): {len(checksum_dupes)}")
    print(f"\nIntended S3 keys (first 10):")
    for key in intended_keys[:10]:
        print(f"  {key}")
    if len(intended_keys) > 10:
        print(f"  ... and {len(intended_keys) - 10} more")

    if args.dry_run:
        print("\nDRY RUN — no uploads performed.")
        db.close()
        return 0

    if not args.yes:
        answer = input("\nProceed? [y/N]: ").strip()
        if answer != "y":
            print("Aborted.")
            db.close()
            return 0

    service = UploadService(db)
    successes = 0
    failures: list[dict] = []

    for f in valid_files:
        if f.name in checksum_dupes:
            print(f"  SKIP (duplicate): {f.name}")
            continue
        try:
            data = f.read_bytes()
            sha = compute_sha256(data)
            if sha in existing_hashes:
                print(f"  SKIP (duplicate): {f.name}")
                continue
            client = args.client or infer_client(f)
            doc = service.upload(
                file_data=data,
                original_filename=f.name,
                client_name=client,
                document_type=args.document_type,
                strategy=args.strategy,
                document_date=default_date,
                status=args.status,
            )
            existing_hashes.add(sha)
            print(f"  SUCCESS: {f.name} -> {doc.s3_key}")
            successes += 1
        except Exception as exc:
            print(f"  FAILURE: {f.name} -> {exc}")
            failures.append({"file": str(f), "error": str(exc)})

    db.close()

    print(f"\nSUMMARY: {successes} uploaded, {len(failures)} failed, {len(checksum_dupes)} skipped (duplicate)")

    if failures:
        report_path = Path(args.report)
        report_path.write_text(json.dumps(failures, indent=2))
        csv_path = report_path.with_suffix(".csv")
        with csv_path.open("w", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=["file", "error"])
            writer.writeheader()
            writer.writerows(failures)
        print(f"Failure report: {report_path}")

    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
