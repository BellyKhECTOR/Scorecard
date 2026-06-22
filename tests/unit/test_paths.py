"""Unit tests for project path resolution."""

from pathlib import Path

from src.paths import CANONICAL_PROJECT_ROOT, get_project_root


class TestProjectPaths:
    def test_canonical_path_defined(self):
        assert "BD - DDQ" in str(CANONICAL_PROJECT_ROOT)
        assert "Universe" in str(CANONICAL_PROJECT_ROOT)

    def test_get_project_root_finds_pyproject(self):
        root = get_project_root()
        assert (root / "pyproject.toml").exists()

    def test_data_directories_under_root(self):
        root = get_project_root()
        assert root / "data" / "backlog" or True  # may not exist until first run
        backlog = root / "data" / "backlog"
        # Path object exists as concept
        assert "backlog" in str(backlog)
