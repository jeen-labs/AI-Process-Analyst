"""
===============================================================================
AI Process Analyst
===============================================================================

Module:
    process_repository.py

Purpose:
    Store and retrieve validated business process information.

Responsibilities:
    - Store process records
    - Retrieve process records
    - List stored processes
    - Prepare for future database integrations

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

from typing import Any, Dict, List, Optional

# =============================================================================
# Third-Party Imports
# =============================================================================

# (None)

# =============================================================================
# Project Imports
# =============================================================================

# (None)

# =============================================================================
# Module Constants
# =============================================================================

# (None)

# =============================================================================
# Classes
# =============================================================================


class ProcessRepository:
    """
    Repository for storing business process information.

    Sprint 1 uses an in-memory dictionary.
    Future versions may use SQLite, PostgreSQL, Neo4j,
    or another enterprise repository.
    """

    def __init__(self) -> None:
        """Initialise the repository."""

        self._repository: Dict[str, Dict[str, Any]] = {}

    def save(self, process: Dict[str, Any]) -> None:
        """
        Save a business process.

        Parameters
        ----------
        process : Dict[str, Any]
            Validated business process.
        """

        process_name = process.get("process_name")

        if not process_name:
            raise ValueError(
                "Process must contain 'process_name'."
            )

        self._repository[process_name] = process

    def get(self, process_name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a process.

        Parameters
        ----------
        process_name : str

        Returns
        -------
        Optional[Dict[str, Any]]
        """

        return self._repository.get(process_name)

    def exists(self, process_name: str) -> bool:
        """
        Check whether a process exists.

        Parameters
        ----------
        process_name : str

        Returns
        -------
        bool
        """

        return process_name in self._repository

    def delete(self, process_name: str) -> bool:
        """
        Delete a process.

        Parameters
        ----------
        process_name : str

        Returns
        -------
        bool
            True if deleted.
        """

        if process_name in self._repository:
            del self._repository[process_name]
            return True

        return False

    def list_processes(self) -> List[str]:
        """
        Return all process names.

        Returns
        -------
        List[str]
        """

        return sorted(self._repository.keys())

    def count(self) -> int:
        """
        Return the number of stored processes.

        Returns
        -------
        int
        """

        return len(self._repository)

    def clear(self) -> None:
        """
        Remove all stored processes.
        """

        self._repository.clear()


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":

    repository = ProcessRepository()

    sample_process = {
        "process_name": "Customer Onboarding",
        "description": "Open a new customer account.",
        "activities": [
            "Receive Application",
            "Verify Identity",
            "Approve Account"
        ]
    }

    repository.save(sample_process)

    print("=" * 70)
    print("PROCESS REPOSITORY TEST")
    print("=" * 70)

    print(f"Process Count : {repository.count()}")

    print()

    print("Stored Processes:")

    for process in repository.list_processes():
        print(f" - {process}")