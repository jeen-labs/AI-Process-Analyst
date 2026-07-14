"""
===============================================================================
AI Process Analyst
===============================================================================

Module:
    document_parser.py

Purpose:
    Prepare document text for AI processing.

Responsibilities:
    - Remove unnecessary whitespace
    - Normalize line endings
    - Prepare AI-ready text

Author:
    Jeen Labs

Version:
    0.2.0

Status:
    Development
===============================================================================
"""

# =============================================================================
# Classes
# =============================================================================


class DocumentParser:
    """
    Prepare raw document text for downstream AI processing.

    This class performs deterministic preprocessing only.
    """

    def __init__(self) -> None:
        """Initialise the document parser."""

    # -------------------------------------------------------------------------

    def clean_text(self, text: str) -> str:
        """
        Clean and normalize document text.

        Parameters
        ----------
        text : str

        Returns
        -------
        str
        """

        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        return "\n".join(lines)

    # -------------------------------------------------------------------------

    def parse(self, text: str) -> str:
        """
        Execute document preprocessing.

        Parameters
        ----------
        text : str

        Returns
        -------
        str
            Cleaned document ready for prompt generation.
        """

        return self.clean_text(text)


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":

    parser = DocumentParser()

    sample = """

        Customer submits application.

        Operations validates documents.

        Manager approves application.

    """

    print("=" * 70)
    print("DOCUMENT PARSER TEST")
    print("=" * 70)

    print(parser.parse(sample))