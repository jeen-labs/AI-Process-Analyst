"""
===============================================================================
AI Process Analyst
===============================================================================

Module:
    schema_validator.py

Purpose:
    Validate enterprise process data against the canonical enterprise schema
    and return a validated ProcessModel.

Author:
    Jeen Labs

Version:
    0.5.0

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
from referencing import Registry
from referencing import Resource

# =============================================================================
# Project Imports
# =============================================================================

from models.process_model import ProcessModel

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
    Validate enterprise process models against the canonical schema.
    """

    def __init__(self) -> None:

        self.schemas = self._load_schemas()

        self.registry = self._build_registry()

        self.validator = jsonschema.Draft202012Validator(
            self.schemas[PROCESS_SCHEMA],
            registry=self.registry
        )

    # -------------------------------------------------------------------------

    def _load_schemas(
        self
    ) -> dict[str, dict[str, Any]]:
        """
        Load every schema into memory.
        """

        schemas: dict[str, dict[str, Any]] = {}

        for filename in SCHEMA_FILES:

            path = SCHEMA_DIRECTORY / filename

            if not path.exists():

                raise FileNotFoundError(
                    f"Schema not found: {path}"
                )

            with path.open(
                "r",
                encoding="utf-8"
            ) as file:

                schemas[filename] = json.load(file)

        return schemas

    # -------------------------------------------------------------------------

    def _build_registry(
        self
    ) -> Registry:
        """
        Build the JSON Schema registry.
        """

        registry = Registry()

        for filename, schema in self.schemas.items():

            resource = Resource.from_contents(schema)

            registry = registry.with_resource(
                filename,
                resource
            )

            schema_id = schema.get("$id")

            if schema_id:

                registry = registry.with_resource(
                    schema_id,
                    resource
                )

        return registry

    # -------------------------------------------------------------------------

    def validate(
        self,
        process_data: dict[str, Any]
    ) -> ProcessModel:
        """
        Validate a normalized process dictionary and return a ProcessModel.
        """

        errors = sorted(

            self.validator.iter_errors(process_data),

            key=lambda error: list(error.path)
        )

        if errors:

            message = "\n".join(

                f"- {'/'.join(map(str, error.path))}: {error.message}"

                if error.path

                else f"- {error.message}"

                for error in errors
            )

            raise ValueError(

                "Schema validation failed:\n\n"

                f"{message}"
            )

        process = ProcessModel.from_dictionary(
            process_data
        )

        process.validate()

        return process

    # -------------------------------------------------------------------------

    def get_schema_names(
        self
    ) -> list[str]:
        """
        Return loaded schema names.
        """

        return sorted(
            self.schemas.keys()
        )


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":

    validator = SchemaValidator()

    print("=" * 70)
    print("ENTERPRISE SCHEMA VALIDATOR")
    print("=" * 70)

    print()

    for schema in validator.get_schema_names():

        print(schema)