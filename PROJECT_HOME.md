# BD DDQ Universe — Project Home

This folder is the **official home** for all Mazi Business Development due diligence questionnaire (DDQ) work.

## Canonical location (your PC)

```text
C:\Users\KhotsoMokoatle\OneDrive - Mazi\Desktop\Projects\Universe\BD - DDQ
```

Everything for the DDQ Knowledge Hub lives here:

| Path | Purpose |
|------|---------|
| `app/` | Web application (FastAPI + UI) |
| `src/` | Core Python logic (upload, search, extraction, AI) |
| `scripts/` | Operational scripts (ingest, reconcile, launch) |
| `sample_documents/` | Acceptance test corpus and reference DDQs |
| `data/backlog/` | Historical DDQ files waiting to be ingested into S3 |
| `data/inbox/` | Drop folder for new documents to review before upload |
| `data/reports/` | Ingestion failure reports (JSON/CSV) |
| `tests/` | Automated tests |
| `docs/` | Architecture, operations and security documentation |
| `.env` | Local configuration (never commit) |
| `Run DDQ Knowledge Hub.bat` | One-click Windows launcher |

## Where data is stored

| Data | Location |
|------|----------|
| Original documents (permanent) | AWS S3 `khotso-bd-storage-basin` |
| Searchable knowledge (Q&A, text) | PostgreSQL on your PC (`localhost`) |
| Working files and backlog | This project folder under `data/` |

## Quick start

1. Open this folder in File Explorer
2. Copy `.env.example` to `.env` and configure
3. Double-click `Run DDQ Knowledge Hub.bat`

See `docs/LOCAL_SETUP.md` for full setup instructions.
