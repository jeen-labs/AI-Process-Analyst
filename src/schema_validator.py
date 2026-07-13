"""
===============================================================================
AI Process Analyst
===============================================================================

Module:
    schema_validator.py

Purpose:
    Validate AI-generated process data against the enterprise schema.

Responsibilities:
    - Validate JSON format
    - Check required schema fields
    - Report validation results
    - Prepare for full JSON Schema validation

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
from typing import Any, Dict, List

# =============================================================================
# Third-Party Imports
# =============================================================================

# (None)
#
# Future:
#     jsonschema

# =============================================================================
# Project Imports
# =============================================================================

# (None)

# =============================================================================
# Module Constants
# =============================================================================

REQUIRED_FIELDS = (
    "process_name",
    "description",
    "activities",
)

# =============================================================================
# Classes
# =============================================================================


class SchemaValidator:
    """
    Validate AI-generated process information.

    This validator performs lightweight validation during Sprint 1.
    Future versions will validate against process.schema.json.
    """

    def __init__(self) -> None:
        """Initialise the schema validator."""

        pass

    def validate(self, json_text: str) -> Dict[str, Any]:
        """
        Validate a JSON document.

        Parameters
        ----------
        json_text : str
            JSON text returned by the AI.

        Returns
        -------
        Dict[str, Any]
            Validation result.
        """

        try:
            data = json.loads(json_text)

        except json.JSONDecodeError as error:

            return {
                "valid": False,
                "errors": [
                    f"Invalid JSON: {error}"
                ]
            }

        return self.validate_dictionary(data)

    def validate_dictionary(
        self,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate a parsed JSON dictionary.

        Parameters
        ----------
        data : Dict[str, Any]

        Returns
        -------
        Dict[str, Any]
            Validation result.
        """

        errors: List[str] = []

        for field in REQUIRED_FIELDS:

            if field not in data:
                errors.append(
                    f"Missing required field: {field}"
                )

        return {
            "valid": len(errors) == 0,
            "errors": errors
        }


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":

    validator = SchemaValidator()

    sample_json = """
    {
        "process_name": "Customer Onboarding",
        "description": "Open a new customer account.",
        "activities": [
            "Receive Application",
            "Verify Identity",
            "Approve Account"
        ]
    }
    """

    result = validator.validate(sample_json)

    print("=" * 70)
    print("SCHEMA VALIDATION RESULT")
    print("=" * 70)
    print(result)