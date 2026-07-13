"""
===============================================================================
AI Process Analyst
===============================================================================

Module:
    process_model.py

Purpose:
    Define the core business process model exchanged between
    platform components.

Responsibilities:
    - Represent a business process
    - Provide a common data structure
    - Support future serialisation and persistence

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

from dataclasses import dataclass, field
from typing import Dict, List

# =============================================================================
# Third-Party Imports
# =============================================================================

# (None)

# =============================================================================
# Project Imports
# =============================================================================

# (None)

# =============================================================================
# Data Models
# =============================================================================


@dataclass
class ProcessModel:
    """
    Represents a business process.

    This model is the canonical representation of a process within
    AI Process Analyst.
    """

    process_name: str = ""
    description: str = ""

    activities: List[str] = field(default_factory=list)

    business_rules: List[str] = field(default_factory=list)

    actors: List[str] = field(default_factory=list)

    systems: List[str] = field(default_factory=list)

    inputs: List[str] = field(default_factory=list)

    outputs: List[str] = field(default_factory=list)

    metadata: Dict[str, str] = field(default_factory=dict)

    def to_dictionary(self) -> Dict:
        """
        Convert the model into a dictionary.

        Returns
        -------
        Dict
        """

        return {
            "process_name": self.process_name,
            "description": self.description,
            "activities": self.activities,
            "business_rules": self.business_rules,
            "actors": self.actors,
            "systems": self.systems,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dictionary(cls, data: Dict) -> "ProcessModel":
        """
        Create a ProcessModel from a dictionary.

        Parameters
        ----------
        data : Dict

        Returns
        -------
        ProcessModel
        """

        return cls(
            process_name=data.get("process_name", ""),
            description=data.get("description", ""),
            activities=data.get("activities", []),
            business_rules=data.get("business_rules", []),
            actors=data.get("actors", []),
            systems=data.get("systems", []),
            inputs=data.get("inputs", []),
            outputs=data.get("outputs", []),
            metadata=data.get("metadata", {}),
        )


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":

    process = ProcessModel(
        process_name="Customer Onboarding",
        description="Open a customer account.",
        activities=[
            "Receive Application",
            "Verify Identity",
            "Approve Account",
        ],
    )

    print("=" * 70)
    print("PROCESS MODEL TEST")
    print("=" * 70)

    print(process)

    print()

    print(process.to_dictionary())