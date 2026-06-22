# Operations Guide

## Launching the Application

1. Ensure PostgreSQL is running
2. Ensure `.env` is configured
3. Double-click **Run DDQ Knowledge Hub.bat** (Windows)
4. The browser opens automatically at http://127.0.0.1:8000

## Uploading a Document

1. Go to **Upload & Library**
2. Fill in: Client name, Document type, Strategy, Date, Status
3. Select the file
4. Click **Upload Document**
5. Wait for the success message showing extraction status

## Searching

1. Go to **Search & Draft**
2. Enter your search query
3. Optionally filter by client, document type, topic, year or status
4. Review **Exact Q&A Matches** and **Full Document Matches**
5. Click **Open Source** to view the original document

## Opening Source Documents

Source links are temporary (15 minutes by default). If a link expires, search again to generate a new link.

## Extraction Statuses

| Status | Meaning |
|--------|---------|
| pending | Awaiting extraction |
| uploaded | Stored in S3, extraction queued |
| processing | Extraction in progress |
| completed | Text and/or Q&A extracted successfully |
| partial | Some text extracted (e.g. scanned PDF) |
| unsupported | Format stored but not extractable |
| failed | Extraction error; source file is safe in S3 |

## When Extraction Fails

1. The original file remains in S3 — nothing is lost
2. Click **Reprocess** in the document library — the app downloads from S3 and re-runs extraction automatically
3. Or re-upload the same file
4. Contact IT if the problem persists

## Health status

The footer shows live status for App, Database, S3 and AI.

API endpoints (for IT):
- `GET /health`
- `GET /health/database`
- `GET /health/s3`

## Sample documents

Generate the acceptance test corpus:

```powershell
uv run python scripts/generate_sample_documents.py
uv run python scripts/ingest_samples.py
```

## Backlog ingestion

```powershell
uv run python scripts/ingest_backlog.py --recursive --dry-run
uv run python scripts/ingest_backlog.py --recursive
```

## Verify build

```powershell
uv run python scripts/verify_build.py
```

## Stopping the Application

Close the console window or press `Ctrl+C` in the terminal running uvicorn.
