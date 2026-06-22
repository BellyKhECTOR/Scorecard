"""Canonical project paths for the BD DDQ Universe folder."""

import os
from functools import lru_cache
from pathlib import Path

# Official home for all Mazi BD DDQ work — local Windows workstation only.
CANONICAL_PROJECT_ROOT = Path(
    r"C:\Users\KhotsoMokoatle\OneDrive - Mazi\Desktop\Projects\Universe\BD - DDQ"
)

MARKER_FILES = ("pyproject.toml", "Run DDQ Knowledge Hub.bat")


def _find_root_from_start(start: Path) -> Path | None:
    current = start.resolve()
    for _ in range(12):
        if any((current / marker).exists() for marker in MARKER_FILES):
            return current
        if current.parent == current:
            break
        current = current.parent
    return None


@lru_cache
def get_project_root() -> Path:
    """
    Resolve the BD DDQ project root directory.

    Priority:
    1. PROJECT_ROOT environment variable
    2. Walk up from this file looking for project markers
    3. Canonical Windows Universe path (if it exists)
    4. Current working directory
    """
    env_root = os.environ.get("PROJECT_ROOT")
    if env_root:
        return Path(env_root).resolve()

    from_file = _find_root_from_start(Path(__file__).parent.parent)
    if from_file:
        return from_file

    if CANONICAL_PROJECT_ROOT.exists():
        return CANONICAL_PROJECT_ROOT

    from_cwd = _find_root_from_start(Path.cwd())
    if from_cwd:
        return from_cwd

    return Path.cwd().resolve()


def get_sample_documents_dir() -> Path:
    return get_project_root() / "sample_documents"


def get_backlog_dir() -> Path:
    return get_project_root() / "data" / "backlog"


def get_inbox_dir() -> Path:
    return get_project_root() / "data" / "inbox"


def get_reports_dir() -> Path:
    return get_project_root() / "data" / "reports"


def ensure_data_directories() -> None:
    """Create standard Universe data folders if they do not exist."""
    for directory in (
        get_sample_documents_dir(),
        get_backlog_dir(),
        get_inbox_dir(),
        get_reports_dir(),
    ):
        directory.mkdir(parents=True, exist_ok=True)
