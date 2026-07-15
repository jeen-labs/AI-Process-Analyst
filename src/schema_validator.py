"""
===============================================================================
AI Process Analyst
===============================================================================

Module:
    schema_validator.py

Purpose:
    Validate enterprise process data against the canonical schema family.

Responsibilities:
    - Load all enterprise schemas
    - Build a schema registry
    - Resolve inter-schema references
    - Validate extracted process models

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
from pathlib import Path
from typing import Any

# =============================================================================
# Third-Party Imports
# =============================================================================

import jsonschema
from referencing import Registry, Resource

# =============================================================================
# Module Constants
# =============================================================================

SCHEMA_DIRECTORY = Path("schemas")

PROCESS_SCHEMA = "process.schema.json"

SCHEMA_FILES = [
    "process.schema.json",
    "activity.schema.json",
    "actor.schema.json",
    "decision.schema.json",
    "business_rule.schema.json",
]

# =============================================================================
# Classes
# =============================================================================


class SchemaValidator:
    """
    Validate enterprise process models against the canonical schema family.
    """

    def __init__(self) -> None:

        self.schemas = self._load_schemas()

        self.registry = self._build_registry()

        self.schema = self.schemas[PROCESS_SCHEMA]

        self.validator = jsonschema.Draft202012Validator(
            self.schema,
            registry=self.registry,
        )

    # ---------------------------------------------------------------------

    def _load_schemas(self) -> dict[str, dict[str, Any]]:
        """
        Load every schema in the schemas folder.
        """

        schemas: dict[str, dict[str, Any]] = {}

        for filename in SCHEMA_FILES:

            path = SCHEMA_DIRECTORY / filename

            if not path.exists():

                raise FileNotFoundError(
                    f"Schema not found: {path}"
                )

            with open(path, encoding="utf-8") as file:

                schemas[filename] = json.load(file)

        return schemas

    # ---------------------------------------------------------------------

    def _build_registry(self) -> Registry:
        """
        Build a schema registry for resolving $ref references.
        """

        registry = Registry()

        for filename, schema in self.schemas.items():

            #
            # Register by filename because our schemas use:
            #
            #     "$ref": "actor.schema.json"
            #
            registry = registry.with_resource(
                filename,
                Resource.from_contents(schema)
            )

            #
            # Register by schema ID as well.
            #
            schema_id = schema.get("$id")

            if schema_id:

                registry = registry.with_resource(
                    schema_id,
                    Resource.from_contents(schema)
                )

        return registry

    # ---------------------------------------------------------------------

    def validate(
        self,
        process_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Validate extracted process information.
        """

        errors = sorted(
            self.validator.iter_errors(process_data),
            key=lambda error: error.path
        )

        if not errors:

            return {
                "valid": True,
                "errors": []
            }

        return {
            "valid": False,
            "errors": [
                error.message
                for error in errors
            ]
        }

    # ---------------------------------------------------------------------

    def get_schema_names(self) -> list[str]:
        """
        Return loaded schema names.
        """

        return list(self.schemas.keys())


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":

    validator = SchemaValidator()

    print("=" * 70)
    print("ENTERPRISE SCHEMA VALIDATOR")
    print("=" * 70)

    print()

    print("Loaded Schemas")

    print("-----------------------------")

    for schema in validator.get_schema_names():

        print(schema)

    print()

    print("Schema registry created successfully.")