"""Email (EML) extractor."""

import email
from email import policy

from src.extractors.base import ChunkDraft, ExtractionResult


class EmailExtractor:
    method = "eml"

    def extract(self, file_data: bytes, extension: str = ".eml") -> ExtractionResult:
        result = ExtractionResult(method="eml")
        msg = email.message_from_bytes(file_data, policy=policy.default)

        subject = msg.get("Subject", "")
        sender = msg.get("From", "")
        date_hdr = msg.get("Date", "")
        attachment_names: list[str] = []

        body_parts: list[str] = []
        if subject:
            body_parts.append(f"Subject: {subject}")
        if sender:
            body_parts.append(f"From: {sender}")
        if date_hdr:
            body_parts.append(f"Date: {date_hdr}")

        if msg.is_multipart():
            for part in msg.walk():
                content_disposition = str(part.get("Content-Disposition", ""))
                if "attachment" in content_disposition:
                    filename = part.get_filename()
                    if filename:
                        attachment_names.append(filename)
                    continue
                if part.get_content_type() == "text/plain":
                    payload = part.get_content()
                    if payload:
                        body_parts.append(str(payload))
        else:
            payload = msg.get_content()
            if payload:
                body_parts.append(str(payload))

        if attachment_names:
            body_parts.append(f"Attachments: {', '.join(attachment_names)}")

        result.full_text = "\n\n".join(body_parts)
        result.status = "completed"
        result.metadata = {
            "subject": subject,
            "sender": sender,
            "attachment_names": attachment_names,
        }
        if result.full_text:
            result.chunks.append(ChunkDraft(chunk_index=0, content=result.full_text, content_type="text"))
        return result
