"""Extractor registry."""

from src.extractors.csv import CsvExtractor
from src.extractors.docx import DocxExtractor
from src.extractors.email import EmailExtractor
from src.extractors.excel import ExcelExtractor
from src.extractors.html import HtmlExtractor
from src.extractors.pdf import PdfExtractor
from src.extractors.pptx import PowerPointExtractor
from src.extractors.text import TextExtractor

EXTRACTORS = {
    ".xlsx": ExcelExtractor(),
    ".xls": ExcelExtractor(),
    ".csv": CsvExtractor(),
    ".docx": DocxExtractor(),
    ".pdf": PdfExtractor(),
    ".txt": TextExtractor(),
    ".html": HtmlExtractor(),
    ".htm": HtmlExtractor(),
    ".pptx": PowerPointExtractor(),
    ".eml": EmailExtractor(),
}


def get_extractor(extension: str):
    return EXTRACTORS.get(extension.lower())
