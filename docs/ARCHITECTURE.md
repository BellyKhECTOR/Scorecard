# Architecture

## Components

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Web UI | FastAPI + Jinja2 + CSS | Two-screen interface |
| API | FastAPI routes | Upload, search, feedback |
| Services | Python modules | Business logic orchestration |
| Extractors | Registry pattern | Format-specific text extraction |
| Storage | PostgreSQL + S3 | Search index + document vault |
| AI (optional) | Provider abstraction | Evidence-backed draft answers |

## Upload Flow

1. Validate file (size, MIME, extension, metadata)
2. Compute SHA-256 checksum
3. Generate canonical filename and S3 key
4. Upload to S3 with server-side encryption
5. Verify with head_object
6. Create database record
7. Run extractor
8. Persist Q&A pairs and document chunks
9. Update extraction status

## Search Flow

1. User query → websearch_to_tsquery
2. Search qa_pairs (weighted: question > answer)
3. Search document_chunks and full_text
4. Apply filters (client, type, topic, year, status)
5. Rank results (approved > historical > document text)
6. Attach presigned source URLs

## Key Design Decisions

- Original S3 documents are immutable historical records
- Failed extraction never deletes source files
- AI is optional and disabled by default
- Search works without AI or pgvector
