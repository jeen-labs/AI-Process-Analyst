"""
AI Process Analyst

Module:
governance.governance_compliance

Purpose:
Provide a deterministic compliance boundary for the Governance Platform.

Phase:
Milestone 4 - Governance Platform
Phase 4.7 - Implement Governance Compliance

This module validates the structural compliance of governance requests.

It does not implement:

- policy evaluation
- permission management
- authorization
- security controls
- auditing
- authentication
- identity management
- persistent compliance storage
- regulatory framework-specific controls
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


class GovernanceComplianceError(ValueError):
    """
    Base exception raised for governance compliance validation failures.
    """

    pass


# =============================================================================
# Governance Compliance
# =============================================================================


class GovernanceCompliance:
    """
    Deterministic compliance boundary for governance requests.

    The compliance boundary validates that governance requests contain the
    required structural information needed for governance compliance.

    It does not evaluate policy, permissions, authorization, security,
    or audit requirements.
    """

    # =========================================================================
    # Public API
    # =========================================================================

    def validate(
        self,
        request: GovernanceRequest,
    ) -> bool:
        """
        Validate the structural compliance of a governance request.

        Parameters
        ----------
        request : GovernanceRequest
            Governance request to validate.

        Returns
        -------
        bool
            True when the request satisfies the compliance boundary.

        Raises
        ------
        GovernanceComplianceError
            If the request does not satisfy the required structure.
        """

        if not isinstance(request, dict):
            raise GovernanceComplianceError(
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

            raise GovernanceComplianceError(
                f"request is missing required field(s): {missing}."
            )

        # ---------------------------------------------------------------------
        # Action
        # ---------------------------------------------------------------------

        action = request["action"]

        if not isinstance(action, str):
            raise GovernanceComplianceError(
                "action must be a string."
            )

        if not action.strip():
            raise GovernanceComplianceError(
                "action must not be empty."
            )

        # ---------------------------------------------------------------------
        # Subject
        # ---------------------------------------------------------------------

        subject = request["subject"]

        if not isinstance(subject, str):
            raise GovernanceComplianceError(
                "subject must be a string."
            )

        if not subject.strip():
            raise GovernanceComplianceError(
                "subject must not be empty."
            )

        # ---------------------------------------------------------------------
        # Resource
        # ---------------------------------------------------------------------

        resource = request["resource"]

        if not isinstance(resource, str):
            raise GovernanceComplianceError(
                "resource must be a string."
            )

        if not resource.strip():
            raise GovernanceComplianceError(
                "resource must not be empty."
            )

        # ---------------------------------------------------------------------
        # Context
        # ---------------------------------------------------------------------

        context = request["context"]

        if not isinstance(context, dict):
            raise GovernanceComplianceError(
                "context must be a dictionary."
            )

        return True

    # =========================================================================
    # Compliance Evaluation
    # =========================================================================

    def evaluate(
        self,
        request: GovernanceRequest,
    ) -> GovernanceDecision:
        """
        Evaluate the compliance status of a governance request.

        Parameters
        ----------
        request : GovernanceRequest
            Governance request to evaluate.

        Returns
        -------
        GovernanceDecision
            Deterministic compliance decision.

        Raises
        ------
        GovernanceComplianceError
            If the request does not satisfy the compliance boundary.

        Notes
        -----
        A structurally compliant request receives an allowed compliance
        decision.

        This does not mean that the action is authorized.

        Policy evaluation, permissions, authorization, security, and
        auditing remain separate Governance Platform responsibilities.
        """

        self.validate(request)

        action = request["action"]

        return GovernanceDecision(
            action=action.strip(),
            allowed=True,
            reason="Request passed the governance compliance boundary.",
        )

    # =========================================================================
    # Boolean Compliance Check
    # =========================================================================

    def is_compliant(
        self,
        request: GovernanceRequest,
    ) -> bool:
        """
        Return whether a governance request passes the compliance boundary.

        Parameters
        ----------
        request : GovernanceRequest
            Governance request to validate.

        Returns
        -------
        bool
            True if the request is compliant, otherwise False.

        Notes
        -----
        Unlike validate() and evaluate(), this method does not raise a
        GovernanceComplianceError for invalid requests.
        """

        try:
            self.validate(request)
        except GovernanceComplianceError:
            return False

        return True


# =============================================================================
# Main
# =============================================================================


if __name__ == "__main__":

    compliance = GovernanceCompliance()

    example_request: GovernanceRequest = {
        "action": "process_analysis",
        "subject": "analyst",
        "resource": "customer_onboarding",
        "context": {},
    }

    print("=" * 80)
    print("GOVERNANCE COMPLIANCE PREVIEW")
    print("=" * 80)

    print(
        "Valid request:",
        compliance.validate(example_request),
    )

    print(
        "Compliance decision:",
        compliance.evaluate(example_request),
    )

    print(
        "Is compliant:",
        compliance.is_compliant(example_request),
    )