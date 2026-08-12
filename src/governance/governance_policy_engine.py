"""
AI Process Analyst

Module:
governance.governance_policy_engine

Purpose:
Provide deterministic policy evaluation for the Governance Platform.

Phase:
Milestone 4 - Governance Platform
Phase 4.2 - Implement Governance Policy Engine
"""

from __future__ import annotations

from src.governance.governance_contracts import (
    GovernanceDecision,
    GovernanceRequest,
)


class GovernancePolicyEngine:
    """
    Deterministic governance policy evaluation engine.
    """

    def __init__(self, allowed_actions: set[str] | None = None) -> None:
        self._allowed_actions = allowed_actions or set()

    def evaluate(
        self,
        request: GovernanceRequest,
    ) -> GovernanceDecision:
        """
        Evaluate a governance request against the configured policy.
        """

        action = request["action"]

        if action in self._allowed_actions:
            return GovernanceDecision(
                action=action,
                allowed=True,
                reason="Action is explicitly allowed by governance policy.",
            )

        return GovernanceDecision(
            action=action,
            allowed=False,
            reason="Action is not allowed by governance policy.",
        )

    def is_allowed(
        self,
        request: GovernanceRequest,
    ) -> bool:
        """
        Return whether the requested action is allowed.
        """

        return self.evaluate(request)["allowed"]