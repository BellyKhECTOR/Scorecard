"""HTML document extractor."""

import re

from bs4 import BeautifulSoup

from src.extractors.base import ChunkDraft, ExtractionResult


class HtmlExtractor:
    method = "html"

    def extract(self, file_data: bytes, extension: str = ".html") -> ExtractionResult:
        html = file_data.decode("utf-8", errors="replace")
        soup = BeautifulSoup(html, "html.parser")

        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        text_parts: list[str] = []
        for element in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "td", "th"]):
            text = element.get_text(separator=" ", strip=True)
            if text:
                text_parts.append(text)

        full_text = "\n".join(text_parts)
        full_text = re.sub(r"\n{3,}", "\n\n", full_text)

        result = ExtractionResult(method="html", full_text=full_text, status="completed")
        if full_text:
            result.chunks.append(ChunkDraft(chunk_index=0, content=full_text, content_type="text"))
        return result
