"""Unit tests for Excel header detection."""

from src.extractors.excel_utils import (
    detect_header_row,
    find_answer_column,
    find_question_column,
    is_section_heading,
    normalise_header,
)


class TestHeaderDetection:
    def test_normalise_header(self):
        assert normalise_header("  Question  ") == "question"
        assert normalise_header("Manager Response") == "manager response"

    def test_question_response_headers(self):
        headers = {0: "Question", 1: "Indicator", 2: "Confirmation", 3: "Response"}
        q_col = find_question_column(headers)
        a_col = find_answer_column(headers, q_col)
        assert q_col == 0
        assert a_col == 3

    def test_detect_header_row(self):
        rows = [
            ("", "", ""),
            ("Question", "Indicator", "Response"),
            ("What is your AUM?", "", "R10bn"),
        ]
        idx, headers = detect_header_row(rows)
        assert idx == 1
        assert find_question_column(headers) == 0
        assert find_answer_column(headers, 0) == 2

    def test_section_heading(self):
        assert is_section_heading("GOVERNANCE", "") is True
        assert is_section_heading("What is your AUM?", "R10bn") is False

    def test_two_column_esg(self):
        rows = [
            ("Question", "Response"),
            ("ESG policy?", "Yes we have one"),
            ("Climate risk?", "Integrated into process"),
            ("Board oversight?", "Quarterly review"),
        ]
        idx, headers = detect_header_row(rows)
        assert idx == 0
        assert find_question_column(headers) == 0
        assert find_answer_column(headers, 0) == 1
