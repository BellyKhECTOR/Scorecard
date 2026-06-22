"""Custom application exceptions."""


class MaziDDQError(Exception):
    """Base exception for the DDQ platform."""


class S3UploadError(MaziDDQError):
    """Raised when S3 upload or verification fails."""


class DocumentValidationError(MaziDDQError):
    """Raised when uploaded file fails validation."""


class ExtractionError(MaziDDQError):
    """Raised when document text extraction fails."""


class DatabasePersistenceError(MaziDDQError):
    """Raised when database persistence fails."""


class SearchError(MaziDDQError):
    """Raised when search operations fail."""
