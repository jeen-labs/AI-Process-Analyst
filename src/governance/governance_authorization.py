"""
AI Process Analyst

Module:
governance.governance_authorization

Purpose:
Provide deterministic authorization decisions for the Governance Platform.

Phase:
Milestone 4 - Governance Platform
Phase 4.4 - Implement Governance Authorization

This module combines governance policy evaluation with explicit subject
permissions to determine whether a governance request is authorized.

It does not implement:

- policy definition
- permission storage
- auditing
- security controls
- compliance controls
"""

from __future__ import annotations

from src.governance.governance_contracts import (
    GovernanceDecision,
    GovernanceRequest,
)
from src.governance.governance_permissions import GovernancePermissions
from src.governance.governance_policy_engine import GovernancePolicyEngine


class GovernanceAuthorization:
    """
    Deterministic authorization engine for the Governance Platform.

    A request is authorized only when:

    1. The requested action is allowed by governance policy.
    2. The requesting subject has explicit permission for the action
       on the requested resource.
    """

    def __init__(
        self,
        policy_engine: GovernancePolicyEngine,
        permissions: GovernancePermissions,
    ) -> None:
        self._policy_engine = policy_engine
        self._permissions = permissions

    def authorize(
        self,
        request: GovernanceRequest,
    ) -> GovernanceDecision:
        """
        Evaluate whether a governance request is authorized.
        """

        action = request["action"]
        subject = request["subject"]
        resource = request["resource"]

        policy_decision = self._policy_engine.evaluate(request)

        if not policy_decision["allowed"]:
            return GovernanceDecision(
                action=action,
                allowed=False,
                reason="Action is denied by governance policy.",
            )

        if not self._permissions.has_permission(
            subject=subject,
            action=action,
            resource=resource,
        ):
            return GovernanceDecision(
                action=action,
                allowed=False,
                reason="Subject does not have the required permission.",
            )

        return GovernanceDecision(
            action=action,
            allowed=True,
            reason="Action is authorized by governance policy and permissions.",
        )

    def is_authorized(
        self,
        request: GovernanceRequest,
    ) -> bool:
        """
        Return whether the governance request is authorized.
        """

        return self.authorize(request)["allowed"]