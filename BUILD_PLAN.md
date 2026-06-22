# Mazi BD DDQ Knowledge Hub — Build Plan

## Milestone Status

| # | Milestone | Status |
|---|-----------|--------|
| 1 | Foundation — config, DB, migrations, topics, naming, FastAPI skeleton | **Complete** |
| 2 | Storage — S3 upload, verification, document library UI | **Complete** |
| 3 | Extraction — Excel, PDF, DOCX, registry, reprocessing | **Complete** |
| 4 | Search — PostgreSQL FTS, trigram, filters, search UI | **Complete** |
| 5 | Backlog ingestion — dry-run, confirmation, reconciliation scripts | **Complete** |
| 6 | AI assistant — optional RAG, confidence, feedback | **Complete** |
| 7 | Hardening — security, health checks, tests, launcher, docs | **Complete** |

## Implementation Sequence

### Milestone 1: Foundation
- [x] Move legacy scorecard to `legacy-scorecard/`
- [x] `pyproject.toml` with uv dependencies
- [x] `src/config.py` — Pydantic settings
- [x] `src/aws.py` — S3 client with retries, SSE, presigned URLs
- [x] `src/models.py` — 6 core tables
- [x] Alembic initial migration with extensions and search triggers
- [x] `src/naming.py`, `src/validation.py`
- [x] `scripts/initialise_topics.py`
- [x] `app/main.py` — FastAPI entry with health endpoints

### Milestone 2: Storage
- [x] `src/services/upload_service.py` — validate → SHA-256 → S3 → verify → DB
- [x] Upload and document library routes
- [x] Screen 1 UI (upload form + library table)
- [x] Presigned source links

### Milestone 3: Extraction
- [x] Extractor registry and base types
- [x] Excel extractor with header detection, two-column fallback, section headings
- [x] PDF, DOCX, CSV, TXT, HTML, PPTX, EML extractors
- [x] Unsupported format handling
- [x] `scripts/reprocess_failed.py`

### Milestone 4: Search
- [x] `src/services/search_service.py` — FTS + trigram
- [x] Screen 2 UI with filters and grouped results

### Milestone 5: Backlog Ingestion
- [x] `scripts/ingest_backlog.py` — dry-run, confirmation, failure report
- [x] `scripts/ingest_samples.py`
- [x] `scripts/check_s3.py`
- [x] `scripts/reconcile_storage.py`

### Milestone 6: AI Assistant
- [x] LLM provider abstraction with disabled fallback
- [x] Retrieval service with freshness warnings
- [x] Answer service with confidence scoring
- [x] Feedback capture

### Milestone 7: Hardening
- [x] Health check endpoints
- [x] Unit and integration tests
- [x] `Run DDQ Knowledge Hub.bat`
- [x] README and docs/

## Commands

```bash
# Install dependencies
uv sync

# Start PostgreSQL (Docker)
docker compose up -d postgres

# Configure environment
cp .env.example .env

# Run migrations
uv run alembic upgrade head

# Seed topics
uv run python scripts/initialise_topics.py

# Start application
uv run uvicorn app.main:app --reload

# Run tests
uv run pytest tests/ -v
```

## Remaining Limitations

- Scanned PDF OCR requires optional `OCR_ENABLED=true` and provider configuration
- Semantic search requires optional `pgvector` extension
- ZIP files are stored but not auto-extracted in v1
- Replace synthetic sample PDFs with real EPPF corpus files for final acceptance if available
