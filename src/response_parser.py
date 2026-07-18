"""
===============================================================================
AI Process Analyst
===============================================================================

Module:
    response_parser.py

Purpose:
    Parse responses returned by Large Language Models (LLMs).

Responsibilities:
    - Parse JSON responses
    - Remove Markdown code fences
    - Validate JSON syntax
    - Convert responses into Python dictionaries
    - Provide formatted output for debugging

Author:
    Jeen Labs

Version:
    0.3.0

Status:
    Development
===============================================================================
"""

# =============================================================================
# Standard Library Imports
# =============================================================================

import json
from typing import Any


# =============================================================================
# Classes
# =============================================================================

class ResponseParser:
    """
    Parse responses returned by an LLM.
    """

    # -------------------------------------------------------------------------

    def parse(
        self,
        response: str
    ) -> dict[str, Any]:
        """
        Parse an LLM response into a Python dictionary.
        """

        if not response or not response.strip():

            raise ValueError(
                "LLM returned an empty response."
            )

        response = response.strip()

        #
        # Remove Markdown code fences if present.
        #

        if response.startswith("```json"):

            response = response[7:]

        elif response.startswith("```"):

            response = response[3:]

        if response.endswith("```"):

            response = response[:-3]

        response = response.strip()

        try:

            parsed = json.loads(response)

        except json.JSONDecodeError as error:

            raise ValueError(
                f"Invalid JSON returned by the LLM:\n{error}"
            ) from error

        if not isinstance(parsed, dict):

            raise ValueError(
                "LLM response must be a JSON object."
            )

        return parsed

    # -------------------------------------------------------------------------

    def pretty_print(
        self,
        parsed_response: dict[str, Any]
    ) -> str:
        """
        Return formatted JSON.
        """

        return json.dumps(
            parsed_response,
            indent=4,
            ensure_ascii=False
        )

    # -------------------------------------------------------------------------

    def contains_required_field(
        self,
        parsed_response: dict[str, Any],
        field_name: str
    ) -> bool:
        """
        Determine whether a field exists.
        """

        return field_name in parsed_response

    # -------------------------------------------------------------------------

    def response_summary(
        self,
        parsed_response: dict[str, Any]
    ) -> str:
        """
        Return a short response summary.
        """

        return (
            f"Top-level fields: "
            f"{len(parsed_response)}"
        )


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":

    sample = """
    ```json
    {
        "process_name": "Customer Onboarding",
        "activities": [
            "Receive Application",
            "Verify Identity"
        ]
    }
    ```
    """

    parser = ResponseParser()

    parsed = parser.parse(sample)

    print("=" * 70)
    print("RESPONSE PARSER TEST")
    print("=" * 70)

    print()

    print(parser.pretty_print(parsed))

    print()

    print(parser.response_summary(parsed))