# Mazi BD DDQ Knowledge Hub

Internal application for Mazi Asset Management Business Development, Compliance and Operations teams to store, search, retrieve and reuse information from completed due diligence questionnaires (DDQs) and supporting documents.

## Project home (your PC)

**All BD DDQ Universe data lives in this folder:**

```text
C:\Users\KhotsoMokoatle\OneDrive - Mazi\Desktop\Projects\Universe\BD - DDQ
```

This is the only project location. The application, scripts, working files, sample documents and backlog all live here on your local machine. See [`PROJECT_HOME.md`](PROJECT_HOME.md) for the full folder layout.

| What | Where |
|------|-------|
| Application code | This folder (`app/`, `src/`, `scripts/`) |
| Historical files to ingest | `data/backlog/` |
| New files for review | `data/inbox/` |
| Sample / test corpus | `sample_documents/` |
| Ingestion reports | `data/reports/` |
| Searchable knowledge | PostgreSQL on `localhost` |
| Original documents (permanent) | S3 `khotso-bd-storage-basin` |

## What It Does

- **Upload** original DDQ documents and supporting files to a secure S3 vault
- **Extract** structured Q&A from Excel questionnaires and full text from PDFs/DOCX
- **Search** the knowledge base using PostgreSQL full-text search
- **Draft** evidence-backed answers using optional AI (disabled by default)
- **Track** source lineage — every answer links back to its original document

## Quick start (Windows)

```powershell
cd "C:\Users\KhotsoMokoatle\OneDrive - Mazi\Desktop\Projects\Universe\BD - DDQ"
copy .env.example .env
uv sync
uv run alembic upgrade head
uv run python scripts/initialise_topics.py
```

Then double-click **`Run DDQ Knowledge Hub.bat`**

Full setup: [`docs/LOCAL_SETUP.md`](docs/LOCAL_SETUP.md)

## Architecture

```
Browser (Upload & Library | Search & Draft)
    ↓
FastAPI + Jinja2 templates  (runs on your PC at 127.0.0.1)
    ↓
Services (upload, extraction, search, retrieval, answer, feedback)
    ↓
PostgreSQL (localhost) + S3 (khotso-bd-storage-basin via AWS CLI profile)
```

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- PostgreSQL 14+ (installed locally on your PC)
- AWS CLI profile with access to `khotso-bd-storage-basin` (eu-north-1)

## Environment Setup

Copy `.env.example` to `.env` and set:

```env
PROJECT_ROOT=C:\Users\KhotsoMokoatle\OneDrive - Mazi\Desktop\Projects\Universe\BD - DDQ
LOCAL_ONLY=true
DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/mazi_ddq
AWS_PROFILE=your-profile-name
```

## Backlog Ingestion

Place historical DDQ files in `data/backlog/`, then:

```powershell
uv run python scripts/ingest_backlog.py --recursive --dry-run
uv run python scripts/ingest_backlog.py --recursive
```

## Testing

```bash
uv run pytest tests/ -v
```

## Documentation

- [`PROJECT_HOME.md`](PROJECT_HOME.md) — folder layout and data locations
- [`docs/LOCAL_SETUP.md`](docs/LOCAL_SETUP.md) — Windows setup guide
- [`docs/OPERATIONS.md`](docs/OPERATIONS.md) — day-to-day use for staff
- [`BUILD_PLAN.md`](BUILD_PLAN.md) — implementation milestones

## Legacy Scorecard

The original ESG Due Diligence Scorecard React app is preserved in `legacy-scorecard/` and is unrelated to this application.
