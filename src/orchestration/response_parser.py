"""
===============================================================================
AI Process Analyst
===============================================================================

Module:
    orchestration.response_parser

Purpose:
    Parse raw Large Language Model (LLM) responses into structured Python
    objects for the enterprise orchestration layer.

Responsibilities:
    - Accept raw LLM responses
    - Validate response input
    - Remove optional Markdown code fences
    - Parse JSON responses
    - Return structured Python data
    - Keep response parsing separate from LLM/provider communication

Architecture:
    Enterprise AI Orchestration Layer

Phase:
    Milestone 3 - Enterprise AI Orchestration Layer
    Phase 3.3 - Refactor Response Parser

This component does NOT:
    - Call an LLM provider
    - Build prompts
    - Perform schema validation
    - Normalize enterprise process models
    - Enrich process data
    - Modify the legacy response parser

The component is intentionally small so that it can later become part of
the Enterprise AI Orchestration pipeline.
===============================================================================
"""

# =============================================================================
# Standard Library Imports
# =============================================================================

import json
from typing import Any


# =============================================================================
# Exceptions
# =============================================================================


class ResponseParserError(ValueError):
    """
    Base exception raised for response parsing failures.
    """


# =============================================================================
# Classes
# =============================================================================


class ResponseParser:
    """
    Parse raw LLM responses into structured Python objects.

    The parser is provider-independent. It receives the raw response produced
    by an LLM client and converts JSON content into Python objects.
    """

    def __init__(self) -> None:
        """
        Initialise the Response Parser.
        """

        pass

    def parse(self, response: str) -> Any:
        """
        Parse a raw LLM response.

        Parameters
        ----------
        response : str
            Raw response returned by an LLM client.

        Returns
        -------
        Any
            Parsed Python representation of the JSON response.

        Raises
        ------
        ResponseParserError
            If the response is not a string, is empty, or contains invalid
            JSON.
        """

        if not isinstance(response, str):
            raise ResponseParserError(
                "LLM response must be a string."
            )

        if not response.strip():
            raise ResponseParserError(
                "LLM response cannot be empty."
            )

        cleaned_response = self._clean_response(response)

        try:
            return json.loads(cleaned_response)

        except json.JSONDecodeError as exc:
            raise ResponseParserError(
                f"Unable to parse LLM response as JSON: {exc}"
            ) from exc

    def _clean_response(self, response: str) -> str:
        """
        Remove surrounding whitespace and optional Markdown code fences.

        Parameters
        ----------
        response : str
            Raw LLM response.

        Returns
        -------
        str
            Cleaned JSON text.
        """

        cleaned = response.strip()

        if cleaned.startswith("```") and cleaned.endswith("```"):
            lines = cleaned.splitlines()

            if len(lines) >= 2:
                first_line = lines[0].strip().lower()

                if first_line in {
                    "```",
                    "```json",
                    "```javascript",
                }:
                    cleaned = "\n".join(lines[1:-1]).strip()

        return cleaned

    def is_valid_json(self, response: str) -> bool:
        """
        Determine whether an LLM response contains valid JSON.

        Parameters
        ----------
        response : str
            Raw LLM response.

        Returns
        -------
        bool
            True when the response can be parsed as JSON; otherwise False.

        Notes
        -----
        This method does not raise ResponseParserError for invalid JSON.
        It is intended for lightweight validation before parsing.
        """

        if not isinstance(response, str):
            return False

        if not response.strip():
            return False

        try:
            self.parse(response)
            return True

        except ResponseParserError:
            return False


# =============================================================================
# Main
# =============================================================================


if __name__ == "__main__":

    sample_response = """
    ```json
    {
        "process_name": "Customer Onboarding",
        "activities": [
            {
                "name": "Submit Application"
            },
            {
                "name": "Verify Documents"
            },
            {
                "name": "Approve Application"
            }
        ]
    }
    ```
    """

    parser = ResponseParser()

    parsed_response = parser.parse(sample_response)

    print("=" * 80)
    print("PARSED LLM RESPONSE")
    print("=" * 80)
    print(json.dumps(parsed_response, indent=4))