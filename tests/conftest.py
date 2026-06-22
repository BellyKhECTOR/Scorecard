"""Pytest configuration."""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest


@pytest.fixture(scope="session")
def fixtures_dir():
    from tests.fixtures.create_fixtures import main
    fixtures_path = Path(__file__).parent / "fixtures"
    main()
    return fixtures_path
