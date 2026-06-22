# Security

## Upload Safety

- Filename sanitisation and path traversal prevention
- MIME type and extension validation
- File size limits (default 100 MB)
- Server-generated S3 keys (never user-supplied)
- SHA-256 checksums for integrity

## Access Control

- S3 bucket is private; presigned URLs expire after 15 minutes
- No public bucket ACLs or policies
- Credentials via standard AWS credential chain only

## Data Handling

- Parameterised SQL via SQLAlchemy
- HTML escaping in templates
- No credentials or full document content in logs
- Upload request IDs for audit tracing

## AI Safety

- Retrieved document content treated as evidence only
- Prompt injection protection in system prompts
- No outside knowledge used to represent Mazi
- Generated answers always include source references

## What We Never Do

- Delete historical DDQ documents
- Execute macros, scripts or shell commands from uploads
- Auto-extract ZIP archives without safety controls
- Store credentials in source control
