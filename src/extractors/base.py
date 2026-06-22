"""Document upload extractor base types."""

from dataclasses import dataclass, field


@dataclass
class QAPairDraft:
    question: str
    answer: str
    source_sheet: str | None = None
    source_row_number: int | None = None
    source_page_number: int | None = None
    section_heading: str | None = None
    topic_slug: str | None = None


@dataclass
class ChunkDraft:
    chunk_index: int
    content: str
    page_number: int | None = None
    sheet_name: str | None = None
    section_heading: str | None = None
    content_type: str = "text"
    token_count: int | None = None


@dataclass
class ExtractionResult:
    full_text: str = ""
    qa_pairs: list[QAPairDraft] = field(default_factory=list)
    chunks: list[ChunkDraft] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    method: str = "unknown"
    status: str = "completed"  # completed, partial, unsupported, failed
