# Backlog documents

Place historical DDQ files here for batch ingestion into the knowledge hub.

## Ingest

```powershell
cd "C:\Users\KhotsoMokoatle\OneDrive - Mazi\Desktop\Projects\Universe\BD - DDQ"
uv run python scripts/ingest_backlog.py data/backlog --recursive
```

Use `--dry-run` first to preview what will be uploaded.

Subfolders are supported — organise by client if helpful:

```text
data/backlog/
  EPPF/
  HIM/
  Prescient/
```
