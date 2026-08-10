"""
AI Process Analyst

Module:
src.orchestration.governance

Purpose:
Provide a deterministic governance and policy boundary for
the enterprise orchestration layer.

Phase:
Milestone 3 - Enterprise AI Orchestration Layer
Phase 3.8 - Governance / Policy Boundary
"""

from __future__ import annotations

from typing import Any, Dict


class GovernanceError(Exception):
    """Base exception for governance-related errors."""


class Governance:
    """
    Deterministic policy boundary for orchestration decisions.

    The governance layer does not execute agents or call an LLM.
    It only evaluates whether a requested action is permitted.
    """

    def __init__(
        self,
        allowed_actions: list[str] | None = None,
    ) -> None:
        """
        Initialise the governance policy.

        Parameters
        ----------
        allowed_actions : list[str] | None
            Actions permitted by the current policy.

        Notes
        -----
        If no actions are supplied, the default policy permits
        process_analysis.
        """

        if allowed_actions is None:
            allowed_actions = ["process_analysis"]

        if not isinstance(allowed_actions, list):
            raise GovernanceError(
                "allowed_actions must be a list."
            )

        normalized_actions: list[str] = []

        for action in allowed_actions:
            if not isinstance(action, str):
                raise GovernanceError(
                    "Each allowed action must be a string."
                )

            normalized_action = action.strip()

            if not normalized_action:
                raise GovernanceError(
                    "Allowed action names must not be empty."
                )

            if normalized_action not in normalized_actions:
                normalized_actions.append(normalized_action)

        self._allowed_actions = sorted(normalized_actions)

    def is_allowed(self, action: str) -> bool:
        """
        Determine whether an action is permitted.

        Parameters
        ----------
        action : str
            Action to evaluate.

        Returns
        -------
        bool
            True if the action is permitted, otherwise False.
        """

        if not isinstance(action, str):
            return False

        normalized_action = action.strip()

        if not normalized_action:
            return False

        return normalized_action in self._allowed_actions

    def evaluate(self, action: str) -> Dict[str, Any]:
        """
        Evaluate an action and return a structured policy decision.

        Parameters
        ----------
        action : str
            Action to evaluate.

        Returns
        -------
        Dict[str, Any]
            Structured governance decision.

        Raises
        ------
        GovernanceError
            If the action is not a valid string.
        """

        if not isinstance(action, str):
            raise GovernanceError(
                "action must be a string."
            )

        normalized_action = action.strip()

        if not normalized_action:
            raise GovernanceError(
                "action must not be empty."
            )

        allowed = self.is_allowed(normalized_action)

        if allowed:
            return {
                "action": normalized_action,
                "allowed": True,
                "reason": "Action is permitted by the current policy.",
            }

        return {
            "action": normalized_action,
            "allowed": False,
            "reason": "Action is not permitted by the current policy.",
        }

    def list_allowed_actions(self) -> list[str]:
        """
        Return all currently allowed actions.

        Returns
        -------
        list[str]
            Sorted list of permitted actions.
        """

        return list(self._allowed_actions)


if __name__ == "__main__":
    governance = Governance()

    print("GOVERNANCE PREVIEW")
    print(
        "Allowed actions:",
        governance.list_allowed_actions(),
    )

    print(
        "process_analysis:",
        governance.evaluate("process_analysis"),
    )

    print(
        "unknown_action:",
        governance.evaluate("unknown_action"),
    )