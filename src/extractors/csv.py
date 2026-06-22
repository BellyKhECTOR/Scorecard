"""CSV extractor - delegates to Excel extractor."""

from src.extractors.excel import ExcelExtractor


class CsvExtractor(ExcelExtractor):
    method = "csv"

    def extract(self, file_data: bytes, extension: str = ".csv"):
        return super().extract(file_data, ".csv")
