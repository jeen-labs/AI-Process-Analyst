"""
===============================================================================
AI Process Analyst
===============================================================================

Module:
    orchestration.governed_execution

Purpose:
    Provide the governed execution boundary between the orchestration layer
    and the Milestone 4 Governance Platform.

Phase:
    Milestone 4 - Governance Platform
    Phase 4.10 - Integrate Governance Platform with Orchestration

Responsibilities:
    - Accept an explicit governed execution request.
    - Construct a GovernanceRequest.
    - Submit the request to GovernanceDecisionBoundary.
    - Preserve the actual governance decision.
    - Prevent execution when governance denies the request.
    - Delegate successful execution to ExecutionManager.
    - Preserve the existing execute() API.
    - Preserve the existing authorize() API.
    - Provide execute_with_decision() for callers that need both the
      governance decision and the execution result.

Important architecture:

    OrchestrationEngine
            |
            v
    GovernedExecution
            |
            v
    GovernanceDecisionBoundary
            |
            +--> Security
            |
            +--> Compliance
            |
            +--> Authorization
            |
            +--> Audit
            |
            v
    ExecutionManager
            |
            v
          Agent

GovernedExecution does NOT:
    - Implement governance policy.
    - Store permissions.
    - Implement authorization rules.
    - Implement security rules.
    - Implement compliance rules.
    - Store audit records.
    - Execute agents directly.

Those responsibilities remain delegated to the appropriate components.

Compatibility rule:

    execute()
        -> returns only the execution result

    execute_with_decision()
        -> returns (governance_decision, execution_result)

This allows existing callers of execute() to continue working while
the orchestration layer can obtain the real governance decision.
===============================================================================
"""

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
    Governed execution boundary for orchestration actions.

    GovernanceDecisionBoundary is the single authoritative governance gate.

    The GovernanceDecisionBoundary is responsible for:

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

    GovernedExecution is responsible only for:

        1. Constructing the GovernanceRequest.
        2. Calling GovernanceDecisionBoundary.
        3. Validating the returned decision.
        4. Blocking execution when denied.
        5. Delegating successful execution to ExecutionManager.
        6. Preserving the actual governance decision when requested.

    Existing public APIs:

        execute()
        authorize()

    Additional API:

        execute_with_decision()
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
            The single authoritative governance decision boundary.

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
    # Public API - Existing Execute
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

        This method preserves the existing result-only API.

        The actual governance decision is obtained internally through
        GovernanceDecisionBoundary.

        Parameters
        ----------
        action : str
            Action being requested.

        request : Any
            Request passed unchanged to ExecutionManager.

        subject : str
            Identity requesting the action.

        resource : str
            Resource against which the action is being evaluated.

        context : dict[str, Any] | None
            Additional governance context.

        Returns
        -------
        Any
            Result returned by ExecutionManager.

        Raises
        ------
        GovernedExecutionError
            If governance denies the request, governance fails, or execution
            fails.
        """

        _decision, result = self.execute_with_decision(
            action=action,
            request=request,
            subject=subject,
            resource=resource,
            context=context,
        )

        return result

    # =========================================================================
    # Public API - Decision-Preserving Execute
    # =========================================================================

    def execute_with_decision(
        self,
        action: str,
        request: Any,
        subject: str,
        resource: str,
        context: dict[str, Any] | None = None,
    ) -> tuple[dict[str, Any], Any]:
        """
        Evaluate governance and execute the action while preserving the
        actual governance decision.

        This is the authoritative execution path for callers that need both:

            governance decision
            +
            execution result

        The governance decision returned by GovernanceDecisionBoundary is
        returned unchanged.

        This method evaluates governance exactly once.

        Parameters
        ----------
        action : str
            Action being requested.

        request : Any
            Request passed unchanged to ExecutionManager.

        subject : str
            Identity requesting the action.

        resource : str
            Resource against which the action is being evaluated.

        context : dict[str, Any] | None
            Additional governance context.

        Returns
        -------
        tuple[dict[str, Any], Any]
            A tuple containing:

                (
                    governance_decision,
                    execution_result,
                )

        Raises
        ------
        GovernedExecutionError
            If the request is invalid, governance fails, the governance
            decision is invalid, governance denies the action, or execution
            fails.
        """

        governance_request = self._build_governance_request(
            action=action,
            subject=subject,
            resource=resource,
            context=context,
        )

        decision = self._evaluate_governance(
            governance_request
        )

        if not decision["allowed"]:
            raise GovernedExecutionError(
                decision["reason"]
            )

        try:
            result = self._execution_manager.execute(
                action,
                request,
            )
        except Exception as exc:
            raise GovernedExecutionError(
                "Governed execution failed."
            ) from exc

        return decision, result

    # =========================================================================
    # Public API - Authorization Only
    # =========================================================================

    def authorize(
        self,
        action: str,
        subject: str,
        resource: str,
        context: dict[str, Any] | None = None,
    ) -> bool:
        """
        Determine whether an action is allowed without executing it.

        GovernanceDecisionBoundary is the only governance gate.

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
            True if governance allows the action, otherwise False.

        Raises
        ------
        GovernedExecutionError
            If governance fails or returns an invalid decision.
        """

        governance_request = self._build_governance_request(
            action=action,
            subject=subject,
            resource=resource,
            context=context,
        )

        decision = self._evaluate_governance(
            governance_request
        )

        return bool(
            decision["allowed"]
        )

    # =========================================================================
    # Governance Evaluation
    # =========================================================================

    def _evaluate_governance(
        self,
        governance_request: GovernanceRequest,
    ) -> dict[str, Any]:
        """
        Evaluate a governance request through the single authoritative
        GovernanceDecisionBoundary.

        This method deliberately contains no policy, permission, security,
        compliance, or audit logic.

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

        if not isinstance(
            decision,
            dict,
        ):
            raise GovernedExecutionError(
                "Governance decision boundary must return "
                "a decision dictionary."
            )

        required_fields = {
            "action",
            "allowed",
            "reason",
        }

        if not required_fields.issubset(
            decision
        ):
            raise GovernedExecutionError(
                "Governance decision boundary returned "
                "an invalid decision."
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

        Normalisation and basic request validation remain here.

        Security, compliance, authorization, and audit decisions do not
        belong here.
        """

        # ---------------------------------------------------------------------
        # Action
        # ---------------------------------------------------------------------

        if not isinstance(
            action,
            str,
        ):
            raise GovernedExecutionError(
                "action must be a string."
            )

        normalized_action = action.strip()

        if not normalized_action:
            raise GovernedExecutionError(
                "action must not be empty."
            )

        # ---------------------------------------------------------------------
        # Subject
        # ---------------------------------------------------------------------

        if not isinstance(
            subject,
            str,
        ):
            raise GovernedExecutionError(
                "subject must be a string."
            )

        normalized_subject = subject.strip()

        if not normalized_subject:
            raise GovernedExecutionError(
                "subject must not be empty."
            )

        # ---------------------------------------------------------------------
        # Resource
        # ---------------------------------------------------------------------

        if not isinstance(
            resource,
            str,
        ):
            raise GovernedExecutionError(
                "resource must be a string."
            )

        normalized_resource = resource.strip()

        if not normalized_resource:
            raise GovernedExecutionError(
                "resource must not be empty."
            )

        # ---------------------------------------------------------------------
        # Context
        # ---------------------------------------------------------------------

        if context is None:
            normalized_context: dict[str, Any] = {}

        elif isinstance(
            context,
            dict,
        ):
            # Copy the dictionary so the caller's context is not mutated.
            normalized_context = dict(
                context
            )

        else:
            raise GovernedExecutionError(
                "context must be a dictionary."
            )

        # ---------------------------------------------------------------------
        # Governance Request
        # ---------------------------------------------------------------------

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
    # Build execution dependencies
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
    # Build governed execution
    # -------------------------------------------------------------------------

    governed_execution = GovernedExecution(
        decision_boundary=decision_boundary,
        execution_manager=execution_manager,
    )

    # -------------------------------------------------------------------------
    # Execute
    # -------------------------------------------------------------------------

    decision, result = (
        governed_execution.execute_with_decision(
            action="process_analysis",
            request="Analyse customer onboarding.",
            subject="analyst",
            resource="customer_onboarding",
            context={
                "source": "demo",
            },
        )
    )

    print("=" * 80)
    print("GOVERNED EXECUTION PREVIEW")
    print("=" * 80)

    print()
    print("GOVERNANCE DECISION:")
    print(decision)

    print()
    print("EXECUTION RESULT:")
    print(result)

    print()
    print("AUDIT ENTRIES:")
    print(audit.entries())