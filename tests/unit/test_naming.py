"""Unit tests for naming utilities."""

from datetime import date

import pytest

from src.naming import build_canonical_filename, build_s3_key, slugify


class TestSlugify:
    def test_basic(self):
        assert slugify("EPPF") == "eppf"

    def test_spaces_and_punctuation(self):
        assert slugify("Domestic Equity") == "domestic-equity"

    def test_duplicate_hyphens(self):
        assert slugify("A  --  B") == "a-b"

    def test_empty(self):
        assert slugify("") == "unknown"


class TestCanonicalFilename:
    def test_format(self):
        result = build_canonical_filename(
            "eppf", "ddq", "domestic-equity", date(2025, 6, 30), "final", ".pdf"
        )
        assert result == "eppf_ddq_domestic-equity_20250630_final.pdf"


class TestS3Key:
    def test_format(self):
        key = build_s3_key("eppf", "ddq", 2025, "eppf_ddq_domestic-equity_20250630_final.pdf")
        assert key == "client=eppf/document_type=ddq/year=2025/eppf_ddq_domestic-equity_20250630_final.pdf"

    def test_path_traversal_rejected(self):
        with pytest.raises(ValueError):
            build_s3_key("eppf", "ddq", 2025, "../evil.pdf")
