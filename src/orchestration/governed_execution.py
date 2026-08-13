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
- Delegate authorization to GovernanceAuthorization.
- Record the authorization decision through GovernanceAudit.
- Execute the action only when authorization succeeds.
- Preserve the existing ExecutionManager as the execution mechanism.

This component does not:
- Implement governance policy.
- Store permissions.
- Implement authorization rules.
- Implement audit storage.
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

from src.governance.governance_audit import GovernanceAudit
from src.governance.governance_authorization import GovernanceAuthorization
from src.governance.governance_contracts import GovernanceRequest
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
    Governed execution boundary for orchestration actions.

    The component coordinates:

        GovernanceAuthorization
                |
                v
        GovernanceDecision
                |
                v
        GovernanceAudit
                |
                v
        ExecutionManager
                |
                v
              Agent

    Authorization is performed before execution.

    A denied authorization decision is audited and execution does not occur.

    An allowed authorization decision is audited before execution begins.
    """

    def __init__(
        self,
        authorization: GovernanceAuthorization,
        audit: GovernanceAudit,
        execution_manager: ExecutionManager,
    ) -> None:
        """
        Initialise the governed execution boundary.

        Parameters
        ----------
        authorization : GovernanceAuthorization
            Governance Platform authorization component.

        audit : GovernanceAudit
            Governance decision audit component.

        execution_manager : ExecutionManager
            Existing orchestration execution manager.

        Raises
        ------
        GovernedExecutionError
            If any required dependency is None.
        """

        if authorization is None:
            raise GovernedExecutionError(
                "authorization must not be None."
            )

        if audit is None:
            raise GovernedExecutionError(
                "audit must not be None."
            )

        if execution_manager is None:
            raise GovernedExecutionError(
                "execution_manager must not be None."
            )

        self._authorization = authorization
        self._audit = audit
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

        Parameters
        ----------
        action : str
            Action being requested.

        request : Any
            Request passed to the existing ExecutionManager.

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
            If the request is invalid or authorization is denied.

        Notes
        -----
        Authorization always occurs before execution.

        Every authorization decision is recorded in GovernanceAudit,
        including denied decisions.
        """

        governance_request = self._build_governance_request(
            action=action,
            subject=subject,
            resource=resource,
            context=context,
        )

        try:
            decision = self._authorization.authorize(
                governance_request
            )
        except Exception as exc:
            raise GovernedExecutionError(
                "Governance authorization failed."
            ) from exc

        if not isinstance(decision, dict):
            raise GovernedExecutionError(
                "Governance authorization must return a decision dictionary."
            )

        required_fields = {
            "action",
            "allowed",
            "reason",
        }

        if not required_fields.issubset(decision):
            raise GovernedExecutionError(
                "Governance authorization returned an invalid decision."
            )

        try:
            self._audit.record(decision)
        except Exception as exc:
            raise GovernedExecutionError(
                "Governance audit recording failed."
            ) from exc

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

        The authorization decision is recorded in the audit trail.

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
            True if authorized, otherwise False.

        Raises
        ------
        GovernedExecutionError
            If authorization or audit recording fails.
        """

        governance_request = self._build_governance_request(
            action=action,
            subject=subject,
            resource=resource,
            context=context,
        )

        try:
            decision = self._authorization.authorize(
                governance_request
            )
        except Exception as exc:
            raise GovernedExecutionError(
                "Governance authorization failed."
            ) from exc

        if not isinstance(decision, dict):
            raise GovernedExecutionError(
                "Governance authorization must return a decision dictionary."
            )

        required_fields = {
            "action",
            "allowed",
            "reason",
        }

        if not required_fields.issubset(decision):
            raise GovernedExecutionError(
                "Governance authorization returned an invalid decision."
            )

        try:
            self._audit.record(decision)
        except Exception as exc:
            raise GovernedExecutionError(
                "Governance audit recording failed."
            ) from exc

        return bool(decision["allowed"])

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
    from src.governance.governance_permissions import (
        GovernancePermission,
        GovernancePermissions,
    )
    from src.governance.governance_policy_engine import (
        GovernancePolicyEngine,
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

    # -------------------------------------------------------------------------
    # Build governed execution boundary
    # -------------------------------------------------------------------------

    governed_execution = GovernedExecution(
        authorization=authorization,
        audit=audit,
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