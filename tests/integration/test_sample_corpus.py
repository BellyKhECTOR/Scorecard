"""Tests for the six-file acceptance corpus."""

from pathlib import Path

import pytest

from src.config import get_settings
from src.extractors.docx import DocxExtractor
from src.extractors.excel import ExcelExtractor
from src.extractors.pdf import PdfExtractor

SAMPLE_FILES = {
    "EPPF Asset Manager Questionnaire Domestic Equity_2025.pdf": {"ext": ".pdf", "min_chunks": 0},
    "EPPF Asset Manager Questionnaire Domestic Equity_2025.docx": {"ext": ".docx", "min_chunks": 1},
    "EPPF Asset Manager Questionnaire Domestic Equity_2025 Final.pdf": {"ext": ".pdf", "min_text": 50},
    "Investment Manager DD Questionnaire - 19052026.xlsx": {"ext": ".xlsx", "min_qa": 5},
    "ESG Questionnaire.xlsx": {"ext": ".xlsx", "min_qa": 3},
    "Completed_HIM_RI_Questionnaire.xlsx": {"ext": ".xlsx", "min_qa": 3},
}


@pytest.fixture(scope="module", autouse=True)
def ensure_samples():
    from scripts.generate_sample_documents import main
    main()


@pytest.fixture
def sample_dir():
    return get_settings().sample_documents_dir


class TestSampleCorpus:
    @pytest.mark.parametrize("filename,expect", SAMPLE_FILES.items())
    def test_file_exists(self, sample_dir, filename, expect):
        path = sample_dir / filename
        assert path.exists(), f"Missing sample: {filename}"

    def test_esg_questionnaire_extraction(self, sample_dir):
        data = (sample_dir / "ESG Questionnaire.xlsx").read_bytes()
        result = ExcelExtractor().extract(data, ".xlsx")
        assert len(result.qa_pairs) >= 3
        assert any("ESG policy" in q.question for q in result.qa_pairs)

    def test_him_ri_response_column(self, sample_dir):
        data = (sample_dir / "Completed_HIM_RI_Questionnaire.xlsx").read_bytes()
        result = ExcelExtractor().extract(data, ".xlsx")
        assert len(result.qa_pairs) >= 3
        for qa in result.qa_pairs:
            assert qa.answer not in ("Y", "N", "Y/N")

    def test_investment_dd_multi_sheet(self, sample_dir):
        data = (sample_dir / "Investment Manager DD Questionnaire - 19052026.xlsx").read_bytes()
        result = ExcelExtractor().extract(data, ".xlsx")
        assert len(result.qa_pairs) >= 5

    def test_eppf_docx_chunks(self, sample_dir):
        data = (sample_dir / "EPPF Asset Manager Questionnaire Domestic Equity_2025.docx").read_bytes()
        result = DocxExtractor().extract(data)
        assert len(result.chunks) >= 1

    def test_eppf_final_pdf_text(self, sample_dir):
        data = (sample_dir / "EPPF Asset Manager Questionnaire Domestic Equity_2025 Final.pdf").read_bytes()
        result = PdfExtractor().extract(data)
        assert len(result.full_text) >= 50
        assert "Mazi" in result.full_text
