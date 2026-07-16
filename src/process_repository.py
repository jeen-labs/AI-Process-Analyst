"""
===============================================================================
AI Process Analyst
===============================================================================

Module:
    process_repository.py

Purpose:
    Store validated enterprise process models.

Responsibilities:
    - Store enterprise process models
    - Retrieve enterprise process models
    - Maintain an in-memory repository
    - Prepare for future database implementations

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
# Classes
# =============================================================================


class ProcessRepository:
    """
    Repository for validated enterprise process models.

    Current implementation:
        - In-memory dictionary

    Future implementations:
        - SQLite
        - PostgreSQL
        - Neo4j
        - Azure Cosmos DB
        - Knowledge Graph
    """

    def __init__(self) -> None:

        self._repository: dict[str, dict[str, Any]] = {}

    # -------------------------------------------------------------------------

    def save(
        self,
        process: dict[str, Any]
    ) -> None:
        """
        Save a validated enterprise process.
        """

        metadata = process.get("metadata", {})

        process_name = metadata.get("process_name")

        if not process_name:

            raise ValueError(
                "Process metadata must contain 'process_name'."
            )

        self._repository[process_name] = process

    

    def save(
        self,
        process: dict[str, Any]
    ) -> None:
        """
        Save a validated enterprise process.

        Supports both the legacy schema and the newer
        process_metadata schema.
        """

        process_name = None

        #
        # Preferred schema
        #
        if "process_metadata" in process:

            metadata = process["process_metadata"]

            process_name = metadata.get("process_name")

        #
        # Legacy schema
        #
        elif "metadata" in process:

            metadata = process["metadata"]

            process_name = metadata.get("process_name")

        #
        # Flat schema (backward compatibility)
        #
        if not process_name:

            process_name = process.get("process_name")

        if not process_name:

            raise ValueError(
                "Process must contain 'process_name'."
            )

        self._repository[process_name] = process

    # -------------------------------------------------------------------------

    def get(
        self,
        process_name: str
    ) -> dict[str, Any] | None:
        """
        Retrieve a process.
        """

        return self._repository.get(process_name)

    # -------------------------------------------------------------------------

    def exists(
        self,
        process_name: str
    ) -> bool:
        """
        Determine whether a process exists.
        """

        return process_name in self._repository

    # -------------------------------------------------------------------------

    def delete(
        self,
        process_name: str
    ) -> bool:
        """
        Delete a process.
        """

        if process_name not in self._repository:

            return False

        del self._repository[process_name]

        return True

    # -------------------------------------------------------------------------

    def list_processes(self) -> list[str]:
        """
        Return all stored process names.
        """

        return sorted(self._repository.keys())

    # -------------------------------------------------------------------------

    def count(self) -> int:
        """
        Number of stored processes.
        """

        return len(self._repository)

    # -------------------------------------------------------------------------

    def clear(self) -> None:
        """
        Remove every stored process.
        """

        self._repository.clear()


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":

    repository = ProcessRepository()

    sample_process = {

        "metadata": {

            "process_name": "Customer Onboarding"

        },

        "activities": []

    }

    repository.save(sample_process)

    print("=" * 70)
    print("PROCESS REPOSITORY TEST")
    print("=" * 70)

    print()

    print("Stored Processes")

    print("------------------------")

    for process in repository.list_processes():

        print(process)

    print()

    print("Repository Count")

    print("------------------------")

    print(repository.count())