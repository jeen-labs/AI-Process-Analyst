"""
AI Process Analyst

Module:
governance.governance_security

Purpose:
Provide a deterministic structural security boundary for the
Governance Platform.

Phase:
Milestone 4 - Governance Platform
Phase 4.7 - Governance Security Boundary

This module provides structural security validation for governance
requests.

It does not implement:

- authentication
- identity management
- encryption
- secrets management
- policy evaluation
- permission management
- authorization
- auditing
- compliance
- persistent security storage

Those responsibilities remain delegated to their appropriate
Governance Platform components.
"""

# =============================================================================
# Standard Library Imports
# =============================================================================

from typing import Any


# =============================================================================
# Local Imports
# =============================================================================

from src.governance.governance_contracts import GovernanceDecision
from src.governance.governance_contracts import GovernanceRequest


# =============================================================================
# Exceptions
# =============================================================================


class GovernanceSecurityError(ValueError):
    """
    Base exception raised for governance security validation failures.
    """

    pass


# =============================================================================
# Governance Security
# =============================================================================


class GovernanceSecurity:
    """
    Deterministic structural security boundary for governance requests.

    The security boundary validates that governance requests have the
    expected structure and basic value types.

    It does not decide whether an action is permitted by policy and does
    not determine whether a subject has permission to perform an action.
    """

    # =========================================================================
    # Public API
    # =========================================================================

    def validate(
        self,
        request: GovernanceRequest,
    ) -> bool:
        """
        Validate the structural integrity of a governance request.

        Parameters
        ----------
        request : GovernanceRequest
            Governance request to validate.

        Returns
        -------
        bool
            True when the request is structurally valid.

        Raises
        ------
        GovernanceSecurityError
            If the request is not structurally valid.

        Notes
        -----
        This method performs structural validation only.

        It does not evaluate governance policy or permissions.
        """

        if not isinstance(request, dict):
            raise GovernanceSecurityError(
                "request must be a dictionary."
            )

        # ---------------------------------------------------------------------
        # Required fields
        # ---------------------------------------------------------------------

        required_fields = {
            "action",
            "subject",
            "resource",
            "context",
        }

        missing_fields = required_fields.difference(request.keys())

        if missing_fields:
            missing = ", ".join(
                sorted(missing_fields)
            )

            raise GovernanceSecurityError(
                f"request is missing required field(s): {missing}."
            )

        # ---------------------------------------------------------------------
        # Action
        # ---------------------------------------------------------------------

        action = request["action"]

        if not isinstance(action, str):
            raise GovernanceSecurityError(
                "action must be a string."
            )

        if not action.strip():
            raise GovernanceSecurityError(
                "action must not be empty."
            )

        # ---------------------------------------------------------------------
        # Subject
        # ---------------------------------------------------------------------

        subject = request["subject"]

        if not isinstance(subject, str):
            raise GovernanceSecurityError(
                "subject must be a string."
            )

        if not subject.strip():
            raise GovernanceSecurityError(
                "subject must not be empty."
            )

        # ---------------------------------------------------------------------
        # Resource
        # ---------------------------------------------------------------------

        resource = request["resource"]

        if not isinstance(resource, str):
            raise GovernanceSecurityError(
                "resource must be a string."
            )

        if not resource.strip():
            raise GovernanceSecurityError(
                "resource must not be empty."
            )

        # ---------------------------------------------------------------------
        # Context
        # ---------------------------------------------------------------------

        context = request["context"]

        if not isinstance(context, dict):
            raise GovernanceSecurityError(
                "context must be a dictionary."
            )

        return True

    # =========================================================================
    # Security Evaluation
    # =========================================================================

    def evaluate(
        self,
        request: GovernanceRequest,
    ) -> GovernanceDecision:
        """
        Evaluate the structural security of a governance request.

        Parameters
        ----------
        request : GovernanceRequest
            Governance request to evaluate.

        Returns
        -------
        GovernanceDecision
            Deterministic security decision.

        Raises
        ------
        GovernanceSecurityError
            If the request is structurally invalid.

        Notes
        -----
        A structurally valid request receives an allowed security decision.

        This does NOT mean that the action is authorized.

        Policy evaluation, permissions, and authorization remain separate
        Governance Platform responsibilities.
        """

        self.validate(request)

        action = request["action"]

        return GovernanceDecision(
            action=action.strip(),
            allowed=True,
            reason="Request passed the governance security boundary.",
        )

    # =========================================================================
    # Boolean Security Check
    # =========================================================================

    def is_secure(
        self,
        request: GovernanceRequest,
    ) -> bool:
        """
        Return whether a governance request passes security validation.

        Parameters
        ----------
        request : GovernanceRequest
            Governance request to validate.

        Returns
        -------
        bool
            True if the request is structurally secure, otherwise False.

        Notes
        -----
        Unlike validate() and evaluate(), this method does not raise a
        GovernanceSecurityError for invalid requests.
        """

        try:
            self.validate(request)
        except GovernanceSecurityError:
            return False

        return True


# =============================================================================
# Main
# =============================================================================


if __name__ == "__main__":

    security = GovernanceSecurity()

    example_request: GovernanceRequest = {
        "action": "process_analysis",
        "subject": "analyst",
        "resource": "customer_onboarding",
        "context": {},
    }

    print("=" * 80)
    print("GOVERNANCE SECURITY PREVIEW")
    print("=" * 80)

    print(
        "Valid request:",
        security.validate(example_request),
    )

    print(
        "Security decision:",
        security.evaluate(example_request),
    )

    print(
        "Is secure:",
        security.is_secure(example_request),
    )