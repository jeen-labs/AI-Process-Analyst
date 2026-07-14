"""
===============================================================================
AI Process Analyst
===============================================================================

Module:
    schema_validator.py

Purpose:
    Validate parsed AI process data.

Responsibilities:
    - Validate required fields
    - Validate activity structure
    - Prepare for JSON Schema validation

Author:
    Jeen Labs

Version:
    0.2.0

Status:
    Development
===============================================================================
"""

# =============================================================================
# Standard Library Imports
# =============================================================================

from typing import Any

# =============================================================================
# Module Constants
# =============================================================================

REQUIRED_FIELDS = (
    "process_name",
    "process_description",
    "activities",
)

# =============================================================================
# Classes
# =============================================================================


class SchemaValidator:
    """
    Validate parsed AI process data.

    Input is expected to be a Python dictionary.
    """

    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Validate extracted process information.

        Parameters
        ----------
        data : dict

        Returns
        -------
        dict
        """

        errors: list[str] = []

        #
        # Required fields
        #

        for field in REQUIRED_FIELDS:

            if field not in data:

                errors.append(
                    f"Missing required field: {field}"
                )

        #
        # Activities
        #

        if "activities" in data:

            if not isinstance(data["activities"], list):

                errors.append(
                    "'activities' must be a list."
                )

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "process": data
        }


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":

    validator = SchemaValidator()

    sample = {
        "process_name": "Customer Onboarding",
        "process_description": "Sample",
        "activities": []
    }

    print(validator.validate(sample))