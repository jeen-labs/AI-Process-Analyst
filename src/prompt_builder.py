"""
===============================================================================
AI Process Analyst
===============================================================================

Module:
    prompt_builder.py

Purpose:
    Load prompt templates and construct prompts for Large Language Models (LLMs).

Responsibilities:
    - Load prompt templates from the prompts directory
    - Inject document content into prompt placeholders
    - Return a complete prompt ready for LLM processing
    - Keep prompt engineering separate from API communication

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
# Module Constants
# =============================================================================

PROMPTS_DIRECTORY = Path("prompts")

EXTRACTION_PROMPT_FILE = PROMPTS_DIRECTORY / "extraction_prompt.md"

DOCUMENT_PLACEHOLDER = "{{DOCUMENT_TEXT}}"


# =============================================================================
# Classes
# =============================================================================

class PromptBuilder:
    """
    Build prompts for AI processing.

    This class loads prompt templates from Markdown files and replaces
    placeholders with runtime content.
    """

    def __init__(self) -> None:
        """Initialise the Prompt Builder."""

        pass

    def load_template(self) -> str:
        """
        Load the extraction prompt template.

        Returns
        -------
        str
            Prompt template.
        """

        if not EXTRACTION_PROMPT_FILE.exists():
            raise FileNotFoundError(
                f"Prompt template not found: {EXTRACTION_PROMPT_FILE}"
            )

        return EXTRACTION_PROMPT_FILE.read_text(
            encoding="utf-8"
        )

    def build_prompt(self, document_text: str) -> str:
        """
        Construct a complete LLM prompt.

        Parameters
        ----------
        document_text : str

        Returns
        -------
        str
        """

        template = self.load_template()

        prompt = template.replace(
            DOCUMENT_PLACEHOLDER,
            document_text.strip()
        )

        return prompt

    def preview_prompt(
        self,
        document_text: str,
        max_length: int = 500
    ) -> str:
        """
        Return a shortened preview of the generated prompt.

        Parameters
        ----------
        document_text : str

        max_length : int

        Returns
        -------
        str
        """

        prompt = self.build_prompt(document_text)

        if len(prompt) <= max_length:
            return prompt

        return prompt[:max_length] + "\n\n... (truncated)"


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":

    sample_document = """
Customer Onboarding Process

1. Customer submits application.
2. Operations team verifies documents.
3. Manager approves application.
4. Customer account is created.
"""

    builder = PromptBuilder()

    prompt = builder.build_prompt(sample_document)

    print("=" * 80)
    print("PROMPT PREVIEW")
    print("=" * 80)
    print(builder.preview_prompt(sample_document))