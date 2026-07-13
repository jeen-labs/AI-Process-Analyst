"""
===============================================================================
AI Process Analyst
===============================================================================

Module:
    document_loader.py

Purpose:
    Locate and validate business process documents before they enter
    the AI processing pipeline.

Responsibilities:
    - Verify document existence
    - Validate supported document types
    - Resolve document paths
    - Prepare documents for reading

Author:
    Jeen Labs

Version:
    0.1.0

Status:
    Development
===============================================================================
"""

# =============================================================================
# Standard Library Imports
# =============================================================================

from pathlib import Path

# =============================================================================
# Third-Party Imports
# =============================================================================

# (None)

# =============================================================================
# Project Imports
# =============================================================================

# (None)

# =============================================================================
# Module Constants
# =============================================================================

SUPPORTED_EXTENSIONS = (
    ".docx",
    ".pdf",
    ".txt",
    ".md",
)

# =============================================================================
# Classes
# =============================================================================


class DocumentLoader:
    """
    Locate and validate business process documents.

    This class performs only file discovery and validation.
    It does not open or read document contents.
    """

    def __init__(self) -> None:
        """Initialise the document loader."""

        self.supported_extensions = SUPPORTED_EXTENSIONS

    def document_exists(self, file_path: str) -> bool:
        """
        Check whether a document exists.

        Parameters
        ----------
        file_path : str
            Path to the document.

        Returns
        -------
        bool
            True if the document exists.
        """

        return Path(file_path).exists()

    def is_supported(self, file_path: str) -> bool:
        """
        Check whether the document type is supported.

        Parameters
        ----------
        file_path : str
            Path to the document.

        Returns
        -------
        bool
            True if the extension is supported.
        """

        extension = Path(file_path).suffix.lower()

        return extension in self.supported_extensions

    def validate_document(self, file_path: str) -> bool:
        """
        Validate a document before processing.

        Parameters
        ----------
        file_path : str
            Path to the document.

        Returns
        -------
        bool
            True if the document is valid.
        """

        if not self.document_exists(file_path):
            return False

        if not self.is_supported(file_path):
            return False

        return True

    def resolve_document(self, file_path: str) -> Path:
        """
        Resolve a document path.

        Parameters
        ----------
        file_path : str
            Path supplied by the user.

        Returns
        -------
        Path
            Resolved Path object.

        Raises
        ------
        FileNotFoundError
            If the document does not exist.

        ValueError
            If the document type is unsupported.
        """

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Document not found: {file_path}"
            )

        if path.suffix.lower() not in self.supported_extensions:
            raise ValueError(
                f"Unsupported document type: {path.suffix}"
            )

        return path.resolve()


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":

    loader = DocumentLoader()

    print("Supported Extensions")

    for extension in loader.supported_extensions:
        print(f" - {extension}")