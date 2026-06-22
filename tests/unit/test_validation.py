"""Unit tests for file validation."""

import pytest

from src.exceptions import DocumentValidationError
from src.validation import (
    compute_sha256,
    validate_extension,
    validate_file_size,
    validate_filename,
    validate_metadata,
)


class TestValidation:
    def test_sha256(self):
        data = b"hello"
        assert len(compute_sha256(data)) == 64

    def test_valid_extension(self):
        assert validate_extension("test.xlsx") == ".xlsx"

    def test_invalid_extension(self):
        with pytest.raises(DocumentValidationError):
            validate_extension("test.exe")

    def test_file_size(self):
        with pytest.raises(DocumentValidationError):
            validate_file_size(0, 1000)

    def test_file_too_large(self):
        with pytest.raises(DocumentValidationError):
            validate_file_size(2000, 1000)

    def test_path_traversal_filename(self):
        with pytest.raises(DocumentValidationError):
            validate_filename("../etc/passwd")

    def test_invalid_document_type(self):
        with pytest.raises(DocumentValidationError):
            validate_metadata("invalid_type", "final", "EPPF")

    def test_missing_client(self):
        with pytest.raises(DocumentValidationError):
            validate_metadata("ddq", "final", "")
