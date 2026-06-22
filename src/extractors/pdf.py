"""PDF document extractor."""

import io
import logging

from pypdf import PdfReader

from src.extractors.base import ChunkDraft, ExtractionResult

logger = logging.getLogger(__name__)

MIN_TEXT_THRESHOLD = 50


class PdfExtractor:
    method = "pdf"

    def extract(self, file_data: bytes, extension: str = ".pdf") -> ExtractionResult:
        result = ExtractionResult(method="pdf")
        try:
            reader = PdfReader(io.BytesIO(file_data))
            text_parts: list[str] = []

            for page_num, page in enumerate(reader.pages, start=1):
                page_text = page.extract_text() or ""
                page_text = page_text.strip()
                if page_text:
                    text_parts.append(page_text)
                    result.chunks.append(ChunkDraft(
                        chunk_index=page_num - 1,
                        content=page_text,
                        page_number=page_num,
                        content_type="text",
                        token_count=len(page_text.split()),
                    ))

            result.full_text = "\n\n".join(text_parts)
            total_chars = len(result.full_text)

            if total_chars < MIN_TEXT_THRESHOLD:
                result.status = "partial"
                result.warnings.append(
                    "Extracted text is minimal; document may be scanned and require OCR."
                )
            else:
                result.status = "completed"

            result.metadata = {
                "page_count": len(reader.pages),
                "char_count": total_chars,
            }
        except Exception as exc:
            logger.exception("PDF extraction failed")
            result.status = "failed"
            result.warnings.append(f"PDF extraction error: {exc}")
        return result
