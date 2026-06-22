"""OCR adapter interface (optional)."""

from src.config import get_settings


class OcrAdapter:
    """Optional OCR implementation behind configuration."""

    def is_available(self) -> bool:
        return get_settings().ocr_enabled

    def extract_text(self, file_data: bytes, content_type: str) -> str:
        raise NotImplementedError("OCR is not configured.")
