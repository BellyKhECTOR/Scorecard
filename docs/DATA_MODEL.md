# Data Model

## Tables

### topics
Seeded taxonomy for categorising Q&A (governance, ESG, risk, etc.)

### documents
One row per uploaded file. Links to S3 object with checksum, version ID and ETag.

### qa_pairs
Structured question-answer pairs extracted from Excel DDQs. Full-text indexed.

### document_chunks
Page/slide/section-level text chunks from PDFs, DOCX, etc. Optional embedding column for future semantic search.

### generated_answers
AI-drafted responses with confidence, sources and warnings.

### answer_feedback
Human reviewer actions for future learning-to-rank improvements.

## S3 Key Convention

```
client={client-slug}/document_type={type}/year={YYYY}/{canonical-filename}
```

## Canonical Filename

```
{client}_{document-type}_{strategy}_{YYYYMMDD}_{status}.{extension}
```
