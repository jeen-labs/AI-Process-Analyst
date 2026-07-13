"""
===============================================================================
AI Process Analyst
===============================================================================

Module:
    document_parser.py

Purpose:
    Prepare document text for AI processing by cleaning and structuring
    the extracted content.

Responsibilities:
    - Normalise whitespace
    - Split text into logical sections
    - Remove empty lines
    - Prepare AI-ready text

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

# (None)

# =============================================================================
# Classes
# =============================================================================


class DocumentParser:
    """
    Prepare raw document text for downstream AI processing.

    This class performs deterministic preprocessing only.
    It does not interpret business meaning or use AI models.
    """

    def __init__(self) -> None:
        """Initialise the document parser."""

        pass

    def clean_text(self, text: str) -> str:
        """
        Clean document text.

        Parameters
        ----------
        text : str
            Raw document text.

        Returns
        -------
        str
            Cleaned document text.
        """

        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        return "\n".join(lines)

    def split_sections(self, text: str) -> List[str]:
        """
        Split document into logical sections.

        Parameters
        ----------
        text : str
            Cleaned document text.

        Returns
        -------
        List[str]
            List of document sections.
        """

        sections = text.split("\n\n")

        return [
            section.strip()
            for section in sections
            if section.strip()
        ]

    def parse(self, text: str) -> List[str]:
        """
        Execute the document parsing workflow.

        Parameters
        ----------
        text : str
            Raw document text.

        Returns
        -------
        List[str]
            Parsed document sections.
        """

        cleaned_text = self.clean_text(text)

        sections = self.split_sections(cleaned_text)

        return sections


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":

    parser = DocumentParser()

    sample_text = """

    Customer submits application.

    Operations verifies application.

    Manager approves application.

    """

    parsed_sections = parser.parse(sample_text)

    print("Parsed Sections")

    for index, section in enumerate(parsed_sections, start=1):
        print(f"{index}. {section}")