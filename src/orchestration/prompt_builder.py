"""
===============================================================================
AI Process Analyst
===============================================================================

Module:
    orchestration.prompt_builder

Purpose:
    Build deterministic prompts for enterprise AI process analysis.

Responsibilities:
    - Load prompt templates from the prompts directory
    - Validate the presence of the required document placeholder
    - Inject document content into the prompt template
    - Return a complete prompt ready for LLM processing
    - Provide a safe preview of generated prompts
    - Keep prompt construction separate from LLM/API communication

Architecture:
    Enterprise AI Orchestration Layer

This component does NOT:
    - Call an LLM
    - Manage API credentials
    - Execute business rules
    - Parse LLM responses
    - Normalize LLM responses
    - Perform ontology classification
    - Build the enterprise knowledge graph

Author:
    Jeen Labs

Version:
    0.6.0

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

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROMPTS_DIRECTORY = PROJECT_ROOT / "prompts"

EXTRACTION_PROMPT_FILE = PROMPTS_DIRECTORY / "extraction_prompt.md"

DOCUMENT_PLACEHOLDER = "{{DOCUMENT_TEXT}}"


# =============================================================================
# Exceptions
# =============================================================================

class PromptTemplateError(Exception):
    """
    Raised when the prompt template is invalid.
    """

    pass


# =============================================================================
# Prompt Builder
# =============================================================================

class PromptBuilder:
    """
    Build prompts for enterprise AI process analysis.

    The PromptBuilder is responsible only for prompt construction.

    It loads a Markdown prompt template and injects runtime document
    content into the configured document placeholder.

    LLM communication is intentionally outside the responsibility
    of this class.
    """

    def __init__(
        self,
        template_path: Path | None = None,
    ) -> None:
        """
        Initialise the PromptBuilder.

        Parameters
        ----------
        template_path : Path | None
            Optional custom prompt template path.

            If omitted, the enterprise extraction prompt located at:

                prompts/extraction_prompt.md

            is used.
        """

        self.template_path = (
            template_path
            if template_path is not None
            else EXTRACTION_PROMPT_FILE
        )

    # =========================================================================
    # Template Loading
    # =========================================================================

    def load_template(self) -> str:
        """
        Load the configured prompt template.

        Returns
        -------
        str
            Prompt template contents.

        Raises
        ------
        FileNotFoundError
            If the configured template does not exist.

        PromptTemplateError
            If the template does not contain the required
            document placeholder.
        """

        if not self.template_path.exists():
            raise FileNotFoundError(
                f"Prompt template not found: {self.template_path}"
            )

        template = self.template_path.read_text(
            encoding="utf-8"
        )

        if DOCUMENT_PLACEHOLDER not in template:
            raise PromptTemplateError(
                "Prompt template does not contain the required "
                f"placeholder: {DOCUMENT_PLACEHOLDER}"
            )

        return template

    # =========================================================================
    # Prompt Construction
    # =========================================================================

    def build_prompt(
        self,
        document_text: str,
    ) -> str:
        """
        Construct a complete prompt from document content.

        Parameters
        ----------
        document_text : str
            Source process document to be analysed.

        Returns
        -------
        str
            Complete prompt ready for an LLM provider.

        Notes
        -----
        This method does not call an LLM. It only constructs the
        prompt text.
        """

        if not isinstance(document_text, str):
            raise TypeError(
                "document_text must be a string"
            )

        template = self.load_template()

        return template.replace(
            DOCUMENT_PLACEHOLDER,
            document_text.strip(),
        )

    # =========================================================================
    # Prompt Preview
    # =========================================================================

    def preview_prompt(
        self,
        document_text: str,
        max_length: int = 500,
    ) -> str:
        """
        Return a shortened preview of the generated prompt.

        Parameters
        ----------
        document_text : str
            Source process document.

        max_length : int
            Maximum number of characters in the preview before the
            truncation marker is added.

        Returns
        -------
        str
            Complete prompt if within the limit, otherwise a
            truncated preview.

        Raises
        ------
        ValueError
            If max_length is less than or equal to zero.
        """

        if max_length <= 0:
            raise ValueError(
                "max_length must be greater than zero"
            )

        prompt = self.build_prompt(document_text)

        if len(prompt) <= max_length:
            return prompt

        return prompt[:max_length] + "\n\n... (truncated)"