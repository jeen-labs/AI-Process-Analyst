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
    0.2.0

Status:
    Development
===============================================================================
"""

# =============================================================================
# Standard Library Imports
# =============================================================================

from pathlib import Path

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
    """

    def __init__(self) -> None:

        self.supported_extensions = SUPPORTED_EXTENSIONS

    # -------------------------------------------------------------------------

    def load(self, document: Path) -> Path:
        """
        Validate and return a document ready for processing.

        Parameters
        ----------
        document : Path

        Returns
        -------
        Path
        """

        return self.resolve_document(document)

    # -------------------------------------------------------------------------

    def document_exists(self, file_path: Path) -> bool:

        return file_path.exists()

    # -------------------------------------------------------------------------

    def is_supported(self, file_path: Path) -> bool:

        return file_path.suffix.lower() in self.supported_extensions

    # -------------------------------------------------------------------------

    def validate_document(self, file_path: Path) -> bool:

        return (
            self.document_exists(file_path)
            and
            self.is_supported(file_path)
        )

    # -------------------------------------------------------------------------

    def resolve_document(self, file_path: Path) -> Path:
        """
        Resolve and validate a document.

        Parameters
        ----------
        file_path : Path

        Returns
        -------
        Path
        """

        if not file_path.exists():

            raise FileNotFoundError(
                f"Document not found: {file_path}"
            )

        if not self.is_supported(file_path):

            raise ValueError(
                f"Unsupported document type: {file_path.suffix}"
            )

        return file_path.resolve()


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":

    loader = DocumentLoader()

    print("=" * 70)
    print("DOCUMENT LOADER TEST")
    print("=" * 70)

    print("Supported Extensions:")

    for extension in loader.supported_extensions:

        print(f"  {extension}")