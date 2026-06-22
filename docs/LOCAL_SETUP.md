# Local Setup (Windows)

This application runs **only on your local PC**. The entire BD DDQ Universe project lives in one folder on your OneDrive.

## Official project folder

```text
C:\Users\KhotsoMokoatle\OneDrive - Mazi\Desktop\Projects\Universe\BD - DDQ
```

Clone or copy the project into this exact path. All application code, DDQ working files, backlog documents and reports live here.

## Folder layout

```text
BD - DDQ\
├── Run DDQ Knowledge Hub.bat    ← double-click to start
├── .env                         ← your local config (create from .env.example)
├── app\                         ← web UI
├── src\                         ← core logic
├── scripts\                     ← ingest, reconcile, launch
├── sample_documents\            ← acceptance test corpus
├── data\
│   ├── backlog\                 ← historical DDQs to batch-ingest
│   ├── inbox\                   ← drop new files for review
│   └── reports\                 ← ingestion failure reports
├── tests\
└── docs\
```

## What runs where

| Component | Location |
|-----------|----------|
| Web app | Your PC — http://127.0.0.1:8000 |
| PostgreSQL | Your PC — localhost:5432 |
| Working files | This project folder (`data/`) |
| Original documents (permanent) | S3 `khotso-bd-storage-basin` via your AWS CLI profile |

## One-time setup

### 1. Install prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) — `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"`
- PostgreSQL for Windows
- AWS CLI with your Mazi profile

### 2. Open the project folder

```powershell
cd "C:\Users\KhotsoMokoatle\OneDrive - Mazi\Desktop\Projects\Universe\BD - DDQ"
```

### 3. Configure `.env`

```powershell
copy .env.example .env
```

```env
PROJECT_ROOT=C:\Users\KhotsoMokoatle\OneDrive - Mazi\Desktop\Projects\Universe\BD - DDQ
LOCAL_ONLY=true
APP_HOST=127.0.0.1
APP_PORT=8000

DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/mazi_ddq

AWS_REGION=eu-north-1
S3_BUCKET=khotso-bd-storage-basin
AWS_PROFILE=your-aws-profile-name
```

### 4. Initialise

```powershell
uv sync
uv run alembic upgrade head
uv run python scripts/initialise_topics.py
uv run python scripts/check_s3.py
```

## Daily use

Double-click **`Run DDQ Knowledge Hub.bat`**

## Working with DDQ files

1. **New documents** — upload via the web UI, or drop in `data/inbox/` for review
2. **Historical backlog** — place files in `data/backlog/`, then run:
   ```powershell
   uv run python scripts/ingest_backlog.py --recursive --dry-run
   uv run python scripts/ingest_backlog.py --recursive
   ```
3. **Sample corpus** — place the six acceptance files in `sample_documents/`

## This is not a cloud deployment

- The app is not hosted on Cursor Cloud, Azure, or any remote server
- It binds to `127.0.0.1` only — not reachable from other machines
- S3 is the only remote service (your existing document vault)
