# Mazi BD DDQ Knowledge Hub

Internal application for Mazi Asset Management Business Development, Compliance and Operations teams to store, search, retrieve and reuse information from completed due diligence questionnaires (DDQs) and supporting documents.

## What It Does

- **Upload** original DDQ documents and supporting files to a secure S3 vault
- **Extract** structured Q&A from Excel questionnaires and full text from PDFs/DOCX
- **Search** the knowledge base using PostgreSQL full-text search
- **Draft** evidence-backed answers using optional AI (disabled by default)
- **Track** source lineage — every answer links back to its original document

## Architecture

```
Browser (Upload & Library | Search & Draft)
    ↓
FastAPI + Jinja2 templates
    ↓
Services (upload, extraction, search, retrieval, answer, feedback)
    ↓
PostgreSQL (searchable knowledge) + S3 (permanent document vault)
```

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- PostgreSQL 14+
- AWS credentials with access to `khotso-bd-storage-basin` (eu-north-1)

## PostgreSQL Setup

Using Docker:

```bash
docker compose up -d postgres
```

Or install PostgreSQL locally and create a database:

```sql
CREATE DATABASE mazi_ddq;
```

## AWS Configuration

Configure credentials using one of:

- AWS CLI profile (set `AWS_PROFILE` in `.env`)
- Environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`)
- IAM role (when deployed)

Verify connectivity:

```bash
uv run python scripts/check_s3.py
```

## Environment Setup

```bash
cp .env.example .env
```

Edit `.env` with your database URL and AWS settings. Never commit `.env` to source control.

## Installation

```bash
uv sync
```

## Database Migration

```bash
uv run alembic upgrade head
uv run python scripts/initialise_topics.py
```

## Application Launch

### Windows (one-click)

Double-click `Run DDQ Knowledge Hub.bat`

### Manual

```bash
uv run uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000

## Backlog Ingestion

Scan and upload a directory of historical documents:

```bash
# Preview without uploading
uv run python scripts/ingest_backlog.py /path/to/documents --dry-run

# Upload with confirmation
uv run python scripts/ingest_backlog.py /path/to/documents

# Automated (no prompt)
uv run python scripts/ingest_backlog.py /path/to/documents --yes --client EPPF --document-type ddq
```

## Sample Documents

Place acceptance corpus files in `sample_documents/` and run:

```bash
uv run python scripts/ingest_samples.py
```

## Testing

```bash
uv run pytest tests/ -v
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Database connection failed | Check `DATABASE_URL` in `.env`; ensure PostgreSQL is running |
| S3 upload failed | Run `scripts/check_s3.py`; verify AWS credentials and bucket access |
| Extraction failed | Source file is still in S3; click Reprocess or re-upload |
| AI drafting disabled | Set `AI_ENABLED=true` and configure `LLM_PROVIDER`, `LLM_API_KEY`, `LLM_MODEL` |

## AI Enablement

```env
AI_ENABLED=true
LLM_PROVIDER=openai
LLM_API_KEY=your-key-here
LLM_MODEL=gpt-4o-mini
```

The application works fully without AI. Search and storage are unaffected.

## Security Notes

- S3 bucket is never public; downloads use presigned URLs
- No credentials in source control or logs
- Uploaded documents are treated as untrusted data
- AI layer is protected against prompt injection from document content

## Recovery Steps

```bash
# Check S3 ↔ database consistency
uv run python scripts/reconcile_storage.py

# Flag failed extractions for reprocessing
uv run python scripts/reprocess_failed.py
```

## Project Structure

See `BUILD_PLAN.md` for implementation details and `docs/` for architecture, operations, security and AI governance documentation.

## Legacy Scorecard

The original ESG Due Diligence Scorecard React app is preserved in `legacy-scorecard/` and is unrelated to this application.
