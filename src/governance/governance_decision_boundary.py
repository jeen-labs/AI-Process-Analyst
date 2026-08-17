"""
src.governance.governance_decision_boundary

Phase:
Milestone 4 - Governance Platform
Phase 4.8 - Unified Governance Decision Boundary

Coordinates the existing governance boundaries without owning
their individual responsibilities.
"""

from __future__ import annotations

from typing import Any

from src.governance.governance_audit import GovernanceAudit
from src.governance.governance_authorization import GovernanceAuthorization
from src.governance.governance_compliance import GovernanceCompliance
from src.governance.governance_contracts import (
    GovernanceDecision,
    GovernanceRequest,
)
from src.governance.governance_security import GovernanceSecurity


class GovernanceDecisionBoundaryError(ValueError):
    """Base exception for unified governance boundary failures."""


class GovernanceDecisionBoundary:
    """
    Unified fail-closed governance decision boundary.

    Sequence:

        Security
            |
            v
        Compliance
            |
            v
        Authorization
            |
            v
        Audit

    This component does not implement policy, permissions, security,
    compliance, authorization rules, or audit storage.
    """

    def __init__(
        self,
        security: GovernanceSecurity,
        compliance: GovernanceCompliance,
        authorization: GovernanceAuthorization,
        audit: GovernanceAudit,
    ) -> None:
        if security is None:
            raise GovernanceDecisionBoundaryError(
                "security must not be None."
            )

        if compliance is None:
            raise GovernanceDecisionBoundaryError(
                "compliance must not be None."
            )

        if authorization is None:
            raise GovernanceDecisionBoundaryError(
                "authorization must not be None."
            )

        if audit is None:
            raise GovernanceDecisionBoundaryError(
                "audit must not be None."
            )

        self._security = security
        self._compliance = compliance
        self._authorization = authorization
        self._audit = audit

    def evaluate(
        self,
        request: GovernanceRequest,
    ) -> GovernanceDecision:
        """
        Evaluate a governance request through the complete
        governance boundary.

        The boundary fails closed: if a governance stage cannot
        produce a valid decision, execution must not proceed.
        """

        security_decision = self._security.evaluate(request)

        if not security_decision["allowed"]:
            self._audit.record(security_decision)
            return security_decision

        compliance_decision = self._compliance.evaluate(request)

        if not compliance_decision["allowed"]:
            self._audit.record(compliance_decision)
            return compliance_decision

        authorization_decision = self._authorization.authorize(
            request
        )

        if not isinstance(authorization_decision, dict):
            raise GovernanceDecisionBoundaryError(
                "Governance authorization must return a decision dictionary."
            )

        required_fields = {
            "action",
            "allowed",
            "reason",
        }

        if not required_fields.issubset(authorization_decision):
            raise GovernanceDecisionBoundaryError(
                "Governance authorization returned an invalid decision."
            )

        self._audit.record(authorization_decision)

        return authorization_decision