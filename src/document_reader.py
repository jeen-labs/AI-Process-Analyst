"""
===============================================================================
AI Process Analyst
===============================================================================

Module:
    document_reader.py

Purpose:
    Read business process documents and extract their textual content
    for downstream AI processing.

Responsibilities:
    - Read supported document types
    - Extract raw text
    - Provide a unified interface for document reading
    - Raise meaningful exceptions when reading fails

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
#
# Future libraries:
# - python-docx
# - PyMuPDF
# - pdfplumber

# =============================================================================
# Project Imports
# =============================================================================

# (None)

# =============================================================================
# Module Constants
# =============================================================================

TEXT_EXTENSIONS = (
    ".txt",
    ".md",
)

# =============================================================================
# Classes
# =============================================================================


class DocumentReader:
    """
    Read business process documents.

    This class is responsible only for reading document contents.
    It does not validate, analyse, or interpret documents.
    """

    def __init__(self) -> None:
        """Initialise the document reader."""

        self.supported_extensions = TEXT_EXTENSIONS

    def read(self, document_path: Path) -> str:
        """
        Read a business process document.

        Parameters
        ----------
        document_path : Path
            Path to the document.

        Returns
        -------
        str
            Raw document text.

        Raises
        ------
        ValueError
            If the document type is unsupported.

        RuntimeError
            If the document cannot be read.
        """

        extension = document_path.suffix.lower()

        if extension == ".txt":
            return self._read_text(document_path)

        if extension == ".md":
            return self._read_markdown(document_path)

        raise ValueError(
            f"Reading '{extension}' documents is not yet implemented."
        )

    # =========================================================================
    # Private Methods
    # =========================================================================

    def _read_text(self, document_path: Path) -> str:
        """
        Read a plain text document.
        """

        try:

            return document_path.read_text(
                encoding="utf-8"
            )

        except Exception as error:

            raise RuntimeError(
                f"Unable to read text document: {error}"
            ) from error

    def _read_markdown(self, document_path: Path) -> str:
        """
        Read a Markdown document.
        """

        try:

            return document_path.read_text(
                encoding="utf-8"
            )

        except Exception as error:

            raise RuntimeError(
                f"Unable to read markdown document: {error}"
            ) from error


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":

    print("DocumentReader module loaded successfully.")