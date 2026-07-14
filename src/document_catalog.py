"""
===============================================================================
AI Process Analyst
===============================================================================

Module:
    document_catalog.py

Purpose:
    Discover and catalogue business process documents available for
    processing.

Responsibilities:
    - Scan document sources
    - Identify supported document types
    - Return a list of available documents
    - Prepare for future enterprise repositories

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
from typing import List

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


class DocumentCatalog:
    """
    Discover documents available for processing.

    Sprint 1:
        Local folders.

    Future:
        - SharePoint
        - OneDrive
        - Google Drive
        - Confluence
        - Enterprise Content Management Systems
    """

    def __init__(self) -> None:
        """Initialise the document catalogue."""

        pass

    def discover_documents(self, source_folder: str) -> List[Path]:
        """
        Scan a folder for supported document types.

        Parameters
        ----------
        source_folder : str

        Returns
        -------
        List[Path]
        """

        folder = Path(source_folder)

        if not folder.exists():
            raise FileNotFoundError(
                f"Folder not found: {folder}"
            )

        documents: List[Path] = []

        for file in folder.iterdir():

            if (
                file.is_file()
                and file.suffix.lower() in SUPPORTED_EXTENSIONS
            ):
                documents.append(file)

        documents.sort()

        return documents

    def count_documents(self, source_folder: str) -> int:
        """
        Return the number of supported documents.

        Parameters
        ----------
        source_folder : str

        Returns
        -------
        int
        """

        return len(
            self.discover_documents(source_folder)
        )

    def supported_extensions(self) -> List[str]:
        """
        Return supported document extensions.

        Returns
        -------
        List[str]
        """

        return list(SUPPORTED_EXTENSIONS)


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":

    catalog = DocumentCatalog()

    print("=" * 70)
    print("DOCUMENT CATALOG")
    print("=" * 70)

    print("Supported Document Types:")

    for extension in catalog.supported_extensions():
        print(f" - {extension}")

    print()

    print("Example:")

    print("catalog.discover_documents('sample_documents')")