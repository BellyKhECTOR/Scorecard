"""Plain text extractor."""

from src.extractors.base import ChunkDraft, ExtractionResult


class TextExtractor:
    method = "text"

    def extract(self, file_data: bytes, extension: str = ".txt") -> ExtractionResult:
        text = file_data.decode("utf-8", errors="replace").strip()
        result = ExtractionResult(method="text", full_text=text, status="completed")
        if text:
            result.chunks.append(ChunkDraft(chunk_index=0, content=text, content_type="text"))
        return result
