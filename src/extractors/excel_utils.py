"""Excel Q&A extraction utilities."""

import re
from datetime import date, datetime
from typing import Any

QUESTION_HEADERS = {
    "question", "questions", "query", "ddq question",
    "information required", "info required", "item",
}
ANSWER_HEADERS = {
    "answer", "response", "manager response", "manager answer",
    "comment", "comments", "completed response", "firm response",
    "manager comments", "mazi response",
}


def normalise_header(value: str) -> str:
    if not value:
        return ""
    text = str(value).lower().strip()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def find_question_column(headers: dict[int, str]) -> int | None:
    for col_idx, header in headers.items():
        norm = normalise_header(header)
        if norm in QUESTION_HEADERS or any(q in norm for q in QUESTION_HEADERS):
            return col_idx
    return None


def find_answer_column(headers: dict[int, str], question_col: int | None) -> int | None:
    for col_idx, header in headers.items():
        norm = normalise_header(header)
        if norm in ANSWER_HEADERS or any(a in norm for a in ANSWER_HEADERS):
            return col_idx
    return None


def detect_header_row(rows: list[tuple], max_scan: int = 20) -> tuple[int | None, dict[int, str]]:
    for row_idx, row in enumerate(rows[:max_scan]):
        headers: dict[int, str] = {}
        for col_idx, cell in enumerate(row):
            if cell is not None and str(cell).strip():
                headers[col_idx] = str(cell).strip()
        if not headers:
            continue
        q_col = find_question_column(headers)
        a_col = find_answer_column(headers, q_col)
        if q_col is not None and a_col is not None:
            return row_idx, headers
    return None, {}


def normalise_cell_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if isinstance(value, (datetime, date)):
        return value.isoformat()[:10] if isinstance(value, date) else value.date().isoformat()
    if isinstance(value, float):
        if value == int(value):
            return str(int(value))
        return str(value)
    text = str(value).strip()
    text = re.sub(r"\s+", " ", text)
    return text


def is_section_heading(question: str, answer: str) -> bool:
    if question and not answer:
        q = question.strip()
        if len(q) < 200 and (q.isupper() or q.endswith(":")):
            return True
        if len(q.split()) <= 8 and not q.endswith("?"):
            return True
    return False


def is_likely_table_not_qa(rows: list[tuple], q_col: int, a_col: int) -> bool:
    """Detect biographies or data tables that should not become Q&A."""
    if len(rows) < 5:
        return False
    short_questions = sum(
        1 for row in rows[:20]
        if row and len(normalise_cell_value(row[q_col] if q_col < len(row) else "")) < 15
    )
    return short_questions > len(rows[:20]) * 0.6
