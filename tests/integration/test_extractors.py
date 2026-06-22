"""Integration tests for extractors with synthetic fixtures."""

from pathlib import Path

import pytest

from src.extractors.docx import DocxExtractor
from src.extractors.excel import ExcelExtractor
from src.extractors.pdf import PdfExtractor
from src.extractors.registry import get_extractor

FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"


@pytest.fixture(scope="module", autouse=True)
def create_fixtures():
    from tests.fixtures.create_fixtures import main
    main()


class TestExcelExtraction:
    def test_esg_questionnaire(self):
        path = FIXTURES_DIR / "esg_questionnaire.xlsx"
        data = path.read_bytes()
        result = ExcelExtractor().extract(data, ".xlsx")
        assert len(result.qa_pairs) >= 3
        assert any("ESG policy" in q.question for q in result.qa_pairs)

    def test_him_ri_response_column(self):
        path = FIXTURES_DIR / "him_ri_questionnaire.xlsx"
        data = path.read_bytes()
        result = ExcelExtractor().extract(data, ".xlsx")
        assert len(result.qa_pairs) >= 3
        for qa in result.qa_pairs:
            assert qa.answer not in ("Y", "N", "Y/N")

    def test_two_column_fallback(self):
        path = FIXTURES_DIR / "two_column_ddq.xlsx"
        data = path.read_bytes()
        result = ExcelExtractor().extract(data, ".xlsx")
        assert len(result.qa_pairs) >= 3


class TestOtherExtractors:
    def test_docx(self):
        path = FIXTURES_DIR / "sample.docx"
        result = DocxExtractor().extract(path.read_bytes())
        assert result.status == "completed"
        assert len(result.chunks) >= 1

    def test_pdf_partial(self):
        path = FIXTURES_DIR / "sample.pdf"
        result = PdfExtractor().extract(path.read_bytes())
        assert result.status == "partial"

    def test_unknown_extension(self):
        assert get_extractor(".exe") is None
