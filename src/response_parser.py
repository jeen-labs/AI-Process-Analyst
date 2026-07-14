"""
===============================================================================
AI Process Analyst
===============================================================================

Module:
    response_parser.py

Purpose:
    Parse and validate responses returned by Large Language Models (LLMs).

Responsibilities:
    - Parse JSON responses
    - Validate JSON syntax
    - Convert responses into Python dictionaries
    - Prepare structured data for ProcessModel creation

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

import json
from typing import Any, Dict

# =============================================================================
# Classes
# =============================================================================


class ResponseParser:
    """
    Parse responses returned by an LLM.
    """

    def __init__(self) -> None:
        """Initialise the Response Parser."""
        pass

    def parse(self, response: str) -> Dict[str, Any]:
        """
        Parse a JSON response.

        Parameters
        ----------
        response : str

        Returns
        -------
        Dict[str, Any]
        """

        if not response.strip():
            raise ValueError("LLM response is empty.")

        try:
            parsed_response = json.loads(response)

        except json.JSONDecodeError as error:
            raise ValueError(
                f"Invalid JSON returned by the LLM: {error}"
            ) from error

        return parsed_response

    def pretty_print(
        self,
        parsed_response: Dict[str, Any]
    ) -> str:
        """
        Return formatted JSON.

        Parameters
        ----------
        parsed_response : Dict[str, Any]

        Returns
        -------
        str
        """

        return json.dumps(
            parsed_response,
            indent=4,
            ensure_ascii=False
        )

    def contains_required_field(
        self,
        parsed_response: Dict[str, Any],
        field_name: str
    ) -> bool:
        """
        Check whether a field exists.

        Parameters
        ----------
        parsed_response : Dict[str, Any]

        field_name : str

        Returns
        -------
        bool
        """

        return field_name in parsed_response

    def response_summary(
        self,
        parsed_response: Dict[str, Any]
    ) -> str:
        """
        Return a short summary.

        Parameters
        ----------
        parsed_response : Dict[str, Any]

        Returns
        -------
        str
        """

        return (
            f"Top-level fields: "
            f"{len(parsed_response)}"
        )


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":

    sample_response = """
    {
        "process_name": "Customer Onboarding",
        "description": "Registers a new customer.",
        "activities": [
            "Receive Application",
            "Verify Documents",
            "Approve Customer"
        ]
    }
    """

    parser = ResponseParser()

    parsed = parser.parse(sample_response)

    print("=" * 70)
    print("PARSED RESPONSE")
    print("=" * 70)

    print(parser.pretty_print(parsed))

    print()

    print(parser.response_summary(parsed))