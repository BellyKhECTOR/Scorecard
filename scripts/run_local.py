#!/usr/bin/env python3
"""Start the application on localhost only (local workstation mode)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import uvicorn

from src.config import get_settings
from src.paths import CANONICAL_PROJECT_ROOT


def main() -> int:
    settings = get_settings()
    host = settings.bind_host
    port = settings.app_port

    print("=" * 60)
    print(" Mazi BD DDQ Knowledge Hub")
    print("=" * 60)
    print(f" Project:  {settings.root}")
    print(f" Expected: {CANONICAL_PROJECT_ROOT}")
    print(f" URL:      http://{host}:{port}")
    print(f" Database: localhost (PostgreSQL)")
    print(f" S3:       {settings.s3_bucket} (via local AWS credentials)")
    print(f" Backlog:  {settings.backlog_dir}")
    print(f" Inbox:    {settings.inbox_dir}")
    if settings.local_only:
        print(" Network:  localhost only — not exposed to internet or LAN")
    if settings.root != CANONICAL_PROJECT_ROOT.resolve():
        print()
        print(" NOTE: Running from a different folder than the canonical Universe path.")
        print("       Set PROJECT_ROOT in .env to match your BD - DDQ folder.")
    print("=" * 60)
    print()

    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=settings.app_env == "development",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
