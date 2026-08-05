"""
===============================================================================
Enterprise Schema Validator
===============================================================================

Validates Enterprise Canonical Process Models.

Current responsibilities
------------------------
✓ Required root objects
✓ Basic structural validation

Future responsibilities
-----------------------
✓ JSON Schema validation
✓ Entity ID uniqueness
✓ Relationship validation
✓ Referential integrity
✓ Cross-object consistency
✓ Governance validation
✓ Analytics validation
✓ Automation validation

Author:
Jeen Labs
===============================================================================
"""

from __future__ import annotations

from typing import Any, Dict

from .validation_errors import ValidationError


class SchemaValidator:
    """
    Enterprise Canonical Process Validator.
    """

    REQUIRED_ROOT_FIELDS = (
        "schemaVersion",
        "modelVersion",
        "metadata",
        "process",
    )

    def validate(
        self,
        model: Dict[str, Any],
    ) -> bool:
        """
        Validate a canonical process model.

        Returns
        -------
        bool
            True if valid.

        Raises
        ------
        ValidationError
            When validation fails.
        """

        if not isinstance(model, dict):
            raise ValidationError(
                "Canonical model must be a dictionary."
            )

        for field in self.REQUIRED_ROOT_FIELDS:

            if field not in model:

                raise ValidationError(
                    f"Missing required root field '{field}'."
                )

        return True