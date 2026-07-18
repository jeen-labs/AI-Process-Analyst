"""
===============================================================================
AI Process Analyst
===============================================================================

Module:
    process_model.py

Purpose:
    Define the canonical enterprise process model exchanged between all
    platform components.

Responsibilities:
    - Represent an enterprise business process
    - Provide a strongly-typed domain model
    - Support serialisation/deserialisation
    - Serve as the canonical object used throughout the application

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

from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from typing import Any


# =============================================================================
# Data Model
# =============================================================================


@dataclass
class ProcessModel:
    """
    Canonical enterprise process model.

    This class mirrors process.schema.json and is the single business object
    exchanged throughout the application.
    """

    metadata: dict[str, Any] = field(default_factory=dict)

    overview: dict[str, Any] = field(default_factory=dict)

    actors: list[dict[str, Any]] = field(default_factory=list)

    systems: list[str] = field(default_factory=list)

    documents: list[str] = field(default_factory=list)

    inputs: list[str] = field(default_factory=list)

    outputs: list[str] = field(default_factory=list)

    activities: list[dict[str, Any]] = field(default_factory=list)

    decisions: list[dict[str, Any]] = field(default_factory=list)

    business_rules: list[dict[str, Any]] = field(default_factory=list)

    risks: list[str] = field(default_factory=list)

    controls: list[str] = field(default_factory=list)

    kpis: list[str] = field(default_factory=list)

    relationships: dict[str, Any] = field(default_factory=dict)

    source: dict[str, Any] = field(default_factory=dict)

    # -------------------------------------------------------------------------

    def to_dictionary(self) -> dict[str, Any]:
        """
        Convert the ProcessModel into a dictionary.
        """

        return asdict(self)

    # -------------------------------------------------------------------------

    @classmethod
    def from_dictionary(
        cls,
        data: dict[str, Any]
    ) -> "ProcessModel":
        """
        Create a ProcessModel from a validated dictionary.
        """

        return cls(

            metadata=data.get("metadata", {}),

            overview=data.get("overview", {}),

            actors=data.get("actors", []),

            systems=data.get("systems", []),

            documents=data.get("documents", []),

            inputs=data.get("inputs", []),

            outputs=data.get("outputs", []),

            activities=data.get("activities", []),

            decisions=data.get("decisions", []),

            business_rules=data.get("business_rules", []),

            risks=data.get("risks", []),

            controls=data.get("controls", []),

            kpis=data.get("kpis", []),

            relationships=data.get("relationships", {}),

            source=data.get("source", {})
        )

    # -------------------------------------------------------------------------

    def validate(self) -> None:
        """
        Perform lightweight validation.
        """

        process_name = self.metadata.get(
            "process_name",
            ""
        )

        if not process_name.strip():

            raise ValueError(
                "metadata.process_name cannot be empty."
            )

    # -------------------------------------------------------------------------

    @property
    def process_name(self) -> str:
        """
        Convenience property.
        """

        return self.metadata.get(
            "process_name",
            ""
        )

    # -------------------------------------------------------------------------

    def summary(self) -> str:
        """
        Return a concise summary.
        """

        return (
            f"{self.process_name} | "
            f"{len(self.activities)} activities | "
            f"{len(self.actors)} actors | "
            f"{len(self.systems)} systems"
        )


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":

    process = ProcessModel(

        metadata={
            "process_id": "PROC-001",
            "process_name": "Customer Onboarding",
            "process_level": 1,
            "version": "1.0",
            "status": "Draft",
            "schema_version": "1.0.0"
        },

        overview={
            "description": "Register and activate a customer.",
            "objective": "Create a valid customer record."
        },

        activities=[
            {
                "activity_id": "ACT-001",
                "activity_name": "Receive Application",
                "sequence_number": 1
            }
        ],

        actors=[
            {
                "actor_id": "ACTOR-001",
                "actor_name": "Customer Service Officer",
                "actor_type": "Human"
            }
        ],

        systems=[
            "CRM"
        ]
    )

    print("=" * 70)
    print("PROCESS MODEL TEST")
    print("=" * 70)

    print()

    print(process.summary())

    print()

    print(process.to_dictionary())