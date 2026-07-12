"""
Document Loader

Responsible for locating and validating business process documents
before they are processed by AI agents.

Version: 0.1.0
Status: Development
"""

from pathlib import Path


class DocumentLoader:
    """
    Handles loading business process documents.
    """

    def __init__(self):

        self.supported_extensions = [
            ".docx",
            ".pdf",
            ".txt",
            ".md"
        ]

    def is_supported(self, file_path: str) -> bool:
        """
        Check whether the supplied document type is supported.
        """

        extension = Path(file_path).suffix.lower()

        return extension in self.supported_extensions

    def document_exists(self, file_path: str) -> bool:
        """
        Verify the document exists.
        """

        return Path(file_path).exists()

    def validate_document(self, file_path: str) -> bool:
        """
        Validate a document before processing.
        """

        if not self.document_exists(file_path):
            return False

        if not self.is_supported(file_path):
            return False

        return True