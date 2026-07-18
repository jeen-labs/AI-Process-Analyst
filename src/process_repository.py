"""
===============================================================================
AI Process Analyst
===============================================================================

Module:
    process_repository.py

Purpose:
    Store validated ProcessModel objects.

Responsibilities:
    - Store ProcessModel instances
    - Retrieve ProcessModel instances
    - Maintain an in-memory repository
    - Prepare for future database implementations

Author:
    Jeen Labs

Version:
    0.4.0

Status:
    Development
===============================================================================
"""

# =============================================================================
# Project Imports
# =============================================================================

from models.process_model import ProcessModel


# =============================================================================
# Classes
# =============================================================================

class ProcessRepository:
    """
    Repository for validated enterprise process models.

    Current implementation
    ----------------------
    In-memory dictionary

    Future implementations
    ----------------------
    - SQLite
    - PostgreSQL
    - Neo4j
    - Azure Cosmos DB
    """

    def __init__(self) -> None:

        self._repository: dict[str, ProcessModel] = {}

    # -------------------------------------------------------------------------

    def save(
        self,
        process: ProcessModel
    ) -> None:
        """
        Save a ProcessModel.
        """

        process.validate()

        self._repository[
            process.process_name
        ] = process

    # -------------------------------------------------------------------------

    def get(
        self,
        process_name: str
    ) -> ProcessModel | None:
        """
        Retrieve a ProcessModel.
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

        return sorted(
            self._repository.keys()
        )

    # -------------------------------------------------------------------------

    def get_all(self) -> list[ProcessModel]:
        """
        Return every stored ProcessModel.
        """

        return list(
            self._repository.values()
        )

    # -------------------------------------------------------------------------

    def count(self) -> int:
        """
        Return repository size.
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

    sample = ProcessModel(

        metadata={
            "process_id": "PROC-001",
            "process_name": "Customer Onboarding",
            "process_level": 1,
            "version": "1.0",
            "status": "Draft",
            "schema_version": "1.0.0"
        },

        overview={
            "description": "Open a customer account.",
            "objective": "Create a customer."
        }
    )

    repository.save(sample)

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