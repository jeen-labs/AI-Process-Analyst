"""
AI Process Analyst

Module:
src.orchestration.governed_execution

Purpose:
Provide a governed execution boundary between the orchestration layer
and the Milestone 4 Governance Platform.

Phase:
Milestone 4 - Governance Platform
Phase 4.6A - Governed Execution Boundary

Responsibilities:
- Accept an explicit governed execution request.
- Submit the request to GovernanceDecisionBoundary.
- Prevent execution when governance denies the request.
- Delegate successful execution to ExecutionManager.
- Preserve the existing public execute() and authorize() APIs.
- Preserve existing execution result and error behavior as closely as
  possible while using GovernanceDecisionBoundary as the single
  governance gate.

This component does not:
- Implement governance policy.
- Store permissions.
- Implement authorization rules.
- Implement audit storage.
- Implement security rules.
- Implement compliance rules.
- Register agents.
- Execute agents directly.

Those responsibilities remain delegated to the appropriate components.
"""

# =============================================================================
# Standard Library Imports
# =============================================================================

from __future__ import annotations

from typing import Any


# =============================================================================
# Local Imports
# =============================================================================

from src.governance.governance_contracts import GovernanceRequest
from src.governance.governance_decision_boundary import (
    GovernanceDecisionBoundary,
)
from src.orchestration.execution_manager import ExecutionManager


# =============================================================================
# Exceptions
# =============================================================================


class GovernedExecutionError(ValueError):
    """
    Base exception raised for governed execution failures.
    """

    pass


# =============================================================================
# Governed Execution
# =============================================================================


class GovernedExecution:
    """
    Thin governed execution boundary for orchestration actions.

    GovernanceDecisionBoundary is the single governance gate.

    The governance decision boundary is responsible for the complete
    governance decision process, including:

    - security,
    - compliance,
    - authorization,
    - audit.

    GovernedExecution is responsible only for:

    - constructing the GovernanceRequest,
    - submitting the request to GovernanceDecisionBoundary,
    - validating the returned governance decision,
    - preventing execution when the decision is denied,
    - delegating successful execution to ExecutionManager.

    The existing public execute() and authorize() APIs are preserved.
    """

    def __init__(
        self,
        decision_boundary: GovernanceDecisionBoundary,
        execution_manager: ExecutionManager,
    ) -> None:
        """
        Initialise the governed execution boundary.

        Parameters
        ----------
        decision_boundary : GovernanceDecisionBoundary
            The single governance decision boundary used as the
            governance gate.

        execution_manager : ExecutionManager
            Existing orchestration execution manager.

        Raises
        ------
        GovernedExecutionError
            If any required dependency is None.
        """

        if decision_boundary is None:
            raise GovernedExecutionError(
                "decision_boundary must not be None."
            )

        if execution_manager is None:
            raise GovernedExecutionError(
                "execution_manager must not be None."
            )

        self._decision_boundary = decision_boundary
        self._execution_manager = execution_manager

    # =========================================================================
    # Public API
    # =========================================================================

    def execute(
        self,
        action: str,
        request: Any,
        subject: str,
        resource: str,
        context: dict[str, Any] | None = None,
    ) -> Any:
        """
        Authorize, audit, and execute an action.

        GovernanceDecisionBoundary is the only governance gate.

        Parameters
        ----------
        action : str
            Action being requested.

        request : Any
            Request passed unchanged to the existing ExecutionManager.

        subject : str
            Identity requesting the action.

        resource : str
            Resource against which the action is being requested.

        context : dict[str, Any] | None
            Additional governance context.

        Returns
        -------
        Any
            Result returned by ExecutionManager.

        Raises
        ------
        GovernedExecutionError
            If the request is invalid, the governance decision fails,
            the governance decision is invalid, the action is denied,
            or execution fails.

        Notes
        -----
        Governance evaluation always occurs before execution.

        Audit responsibilities remain inside GovernanceDecisionBoundary.
        """

        governance_request = self._build_governance_request(
            action=action,
            subject=subject,
            resource=resource,
            context=context,
        )

        decision = self._evaluate_governance(governance_request)

        if not decision["allowed"]:
            raise GovernedExecutionError(
                decision["reason"]
            )

        try:
            return self._execution_manager.execute(
                action,
                request,
            )
        except Exception as exc:
            raise GovernedExecutionError(
                "Governed execution failed."
            ) from exc

    # =========================================================================
    # Authorization Only
    # =========================================================================

    def authorize(
        self,
        action: str,
        subject: str,
        resource: str,
        context: dict[str, Any] | None = None,
    ) -> bool:
        """
        Determine whether an action is authorized without executing it.

        GovernanceDecisionBoundary is the only governance gate.

        Audit responsibilities remain inside GovernanceDecisionBoundary.

        Parameters
        ----------
        action : str
            Action being evaluated.

        subject : str
            Identity requesting the action.

        resource : str
            Resource against which the action is being evaluated.

        context : dict[str, Any] | None
            Additional governance context.

        Returns
        -------
        bool
            True if the governance boundary allows the action,
            otherwise False.

        Raises
        ------
        GovernedExecutionError
            If the governance decision boundary fails or returns
            an invalid decision.
        """

        governance_request = self._build_governance_request(
            action=action,
            subject=subject,
            resource=resource,
            context=context,
        )

        decision = self._evaluate_governance(governance_request)

        return bool(decision["allowed"])

    # =========================================================================
    # Governance Evaluation
    # =========================================================================

    def _evaluate_governance(
        self,
        governance_request: GovernanceRequest,
    ) -> dict[str, Any]:
        """
        Evaluate a governance request through the single governance gate.

        This method deliberately contains no policy, permission,
        security, compliance, or audit logic.

        All of those responsibilities belong to
        GovernanceDecisionBoundary.
        """

        try:
            decision = self._decision_boundary.evaluate(
                governance_request
            )
        except Exception as exc:
            raise GovernedExecutionError(
                "Governance decision boundary failed."
            ) from exc

        if not isinstance(decision, dict):
            raise GovernedExecutionError(
                "Governance decision boundary must return a decision dictionary."
            )

        required_fields = {
            "action",
            "allowed",
            "reason",
        }

        if not required_fields.issubset(decision):
            raise GovernedExecutionError(
                "Governance decision boundary returned an invalid decision."
            )

        return decision

    # =========================================================================
    # Governance Request Construction
    # =========================================================================

    @staticmethod
    def _build_governance_request(
        action: str,
        subject: str,
        resource: str,
        context: dict[str, Any] | None,
    ) -> GovernanceRequest:
        """
        Validate and construct a GovernanceRequest.

        Input normalization and validation remain here because they
        belong to the governed execution boundary rather than to the
        individual governance mechanisms.
        """

        if not isinstance(action, str):
            raise GovernedExecutionError(
                "action must be a string."
            )

        normalized_action = action.strip()

        if not normalized_action:
            raise GovernedExecutionError(
                "action must not be empty."
            )

        if not isinstance(subject, str):
            raise GovernedExecutionError(
                "subject must be a string."
            )

        normalized_subject = subject.strip()

        if not normalized_subject:
            raise GovernedExecutionError(
                "subject must not be empty."
            )

        if not isinstance(resource, str):
            raise GovernedExecutionError(
                "resource must be a string."
            )

        normalized_resource = resource.strip()

        if not normalized_resource:
            raise GovernedExecutionError(
                "resource must not be empty."
            )

        if context is None:
            normalized_context: dict[str, Any] = {}

        elif isinstance(context, dict):
            normalized_context = dict(context)

        else:
            raise GovernedExecutionError(
                "context must be a dictionary."
            )

        return GovernanceRequest(
            action=normalized_action,
            subject=normalized_subject,
            resource=normalized_resource,
            context=normalized_context,
        )


# =============================================================================
# Demonstration
# =============================================================================


if __name__ == "__main__":

    from src.governance.governance_audit import GovernanceAudit
    from src.governance.governance_authorization import (
        GovernanceAuthorization,
    )
    from src.governance.governance_compliance import (
        GovernanceCompliance,
    )
    from src.governance.governance_permissions import (
        GovernancePermission,
        GovernancePermissions,
    )
    from src.governance.governance_policy_engine import (
        GovernancePolicyEngine,
    )
    from src.governance.governance_security import (
        GovernanceSecurity,
    )
    from src.orchestration.agent_registry import AgentRegistry
    from src.orchestration.governance import Governance

    class ExampleAgent:
        """
        Simple deterministic example agent.
        """

        def execute(
            self,
            request: Any,
        ) -> dict[str, Any]:
            return {
                "agent": "process_analysis",
                "request": request,
                "status": "executed",
            }

    # -------------------------------------------------------------------------
    # Build Milestone 3 execution dependencies
    # -------------------------------------------------------------------------

    registry = AgentRegistry()

    registry.register(
        "process_analysis",
        ExampleAgent(),
    )

    legacy_governance = Governance()

    execution_manager = ExecutionManager(
        agent_registry=registry,
        governance=legacy_governance,
    )

    # -------------------------------------------------------------------------
    # Build Milestone 4 governance dependencies
    # -------------------------------------------------------------------------

    policy_engine = GovernancePolicyEngine(
        allowed_actions={
            "process_analysis",
        }
    )

    permissions = GovernancePermissions()

    permissions.grant(
        GovernancePermission(
            subject="analyst",
            action="process_analysis",
            resource="customer_onboarding",
        )
    )

    authorization = GovernanceAuthorization(
        policy_engine=policy_engine,
        permissions=permissions,
    )

    audit = GovernanceAudit()

    decision_boundary = GovernanceDecisionBoundary(
        security=GovernanceSecurity(),
        compliance=GovernanceCompliance(),
        authorization=authorization,
        audit=audit,
    )

    # -------------------------------------------------------------------------
    # Build governed execution boundary
    # -------------------------------------------------------------------------

    governed_execution = GovernedExecution(
        decision_boundary=decision_boundary,
        execution_manager=execution_manager,
    )

    # -------------------------------------------------------------------------
    # Execute governed request
    # -------------------------------------------------------------------------

    result = governed_execution.execute(
        action="process_analysis",
        request="Analyse customer onboarding.",
        subject="analyst",
        resource="customer_onboarding",
        context={
            "source": "demo",
        },
    )

    print("=" * 80)
    print("GOVERNED EXECUTION PREVIEW")
    print("=" * 80)
    print(result)

    print()
    print("AUDIT ENTRIES:")
    print(audit.entries())