"""
AI Process Analyst

Module:
orchestration.orchestration_engine

Purpose:
Provide the top-level orchestration engine that integrates:

    Planner
        |
        v
    Agent Registry
        |
        v
    Governance / GovernedExecution
        |
        v
    Execution Manager
        |
        v
    Agent

Phase:
Milestone 3 - Enterprise AI Orchestration Layer
Phase 3.10 - Integrate Planner, Agent Registry, Governance,
and Execution Manager

Milestone 4:
Phase 4.10 - Integrate Governance Platform with Orchestration

Responsibilities:
- Accept an orchestration request
- Validate the request
- Generate an execution plan through Planner
- Determine the action represented by the plan
- Route execution through GovernedExecution when available
- Preserve the actual governance decision returned by GovernedExecution
- Fall back to ExecutionManager governance when GovernedExecution is not supplied
- Return a deterministic orchestration result

Authoritative Milestone 4 execution path:

    Request
       |
       v
    OrchestrationEngine
       |
       v
    Planner
       |
       v
    GovernedExecution
       |
       v
    GovernanceDecisionBoundary
       |
       +----> Security
       |
       +----> Compliance
       |
       +----> Authorization
       |
       +----> Audit
       |
       v
    ExecutionManager
       |
       v
    Agent

Important:
When GovernedExecution is supplied, the orchestration engine MUST NOT
perform a separate legacy governance check before execution.

The GovernanceDecisionBoundary invoked by GovernedExecution is the
authoritative governance decision point for the orchestration execution.
"""

# =============================================================================
# Standard Library Imports
# =============================================================================

from typing import Any


# =============================================================================
# Local Imports
# =============================================================================

from src.orchestration.agent_registry import AgentRegistry
from src.orchestration.contracts import OrchestrationResult
from src.orchestration.execution_manager import (
    ExecutionManager,
    ExecutionManagerError,
)
from src.orchestration.governed_execution import (
    GovernedExecution,
    GovernedExecutionError,
)
from src.orchestration.governance import Governance
from src.orchestration.planner import Planner


# =============================================================================
# Exceptions
# =============================================================================


class OrchestrationEngineError(ValueError):
    """
    Base exception raised for orchestration engine failures.
    """

    pass


# =============================================================================
# Orchestration Engine
# =============================================================================


class OrchestrationEngine:
    """
    Top-level coordinator for the enterprise orchestration layer.

    The engine integrates:

        Planner
        AgentRegistry
        Governance
        ExecutionManager
        GovernedExecution

    During Milestone 4, GovernedExecution is the authoritative execution
    boundary whenever it is supplied to the engine.
    """

    def __init__(
        self,
        planner: Planner,
        agent_registry: AgentRegistry,
        governance: Governance,
        execution_manager: ExecutionManager,
        governed_execution: GovernedExecution | None = None,
    ) -> None:
        """
        Initialise the orchestration engine.

        Parameters
        ----------
        planner : Planner
            Component responsible for creating execution plans.

        agent_registry : AgentRegistry
            Registry containing executable agents.

        governance : Governance
            Legacy/direct governance component retained for compatibility
            and non-execution helper methods.

        execution_manager : ExecutionManager
            Component responsible for agent execution.

        governed_execution : GovernedExecution | None
            Milestone 4 governance boundary.

            When supplied, orchestration execution uses this component as
            the authoritative governance path.

        Raises
        ------
        OrchestrationEngineError
            If any required dependency is None.
        """

        if planner is None:
            raise OrchestrationEngineError(
                "planner must not be None."
            )

        if agent_registry is None:
            raise OrchestrationEngineError(
                "agent_registry must not be None."
            )

        if governance is None:
            raise OrchestrationEngineError(
                "governance must not be None."
            )

        if execution_manager is None:
            raise OrchestrationEngineError(
                "execution_manager must not be None."
            )

        self._planner = planner
        self._agent_registry = agent_registry
        self._governance = governance
        self._execution_manager = execution_manager
        self._governed_execution = governed_execution

    # =========================================================================
    # Public API
    # =========================================================================

    def orchestrate(
        self,
        request: str,
    ) -> OrchestrationResult:
        """
        Plan and execute an orchestration request.

        Parameters
        ----------
        request : str
            Process-analysis request.

        Returns
        -------
        OrchestrationResult
            Structured orchestration result containing:

                request
                plan
                action
                governance
                result

        Raises
        ------
        OrchestrationEngineError
            If the request is invalid, a dependent orchestration component
            fails, governance denies execution, or execution fails.

        Governance behaviour
        --------------------
        If GovernedExecution is supplied:

            Planner
                ->
            GovernedExecution.execute_with_decision()
                ->
            GovernanceDecisionBoundary
                ->
            ExecutionManager

        The actual governance decision returned by the governance boundary
        is preserved in the orchestration result.

        No separate legacy governance check is performed in this path.

        If GovernedExecution is not supplied, the engine falls back to the
        existing ExecutionManager governance integration.
        """

        self._validate_request(request)

        normalized_request = request.strip()

        try:
            # -----------------------------------------------------------------
            # Phase 1: Planning
            # -----------------------------------------------------------------

            plan = self._planner.plan(
                normalized_request
            )

            if not isinstance(plan, dict):
                raise OrchestrationEngineError(
                    "Planner must return a dictionary."
                )

            action = plan.get("plan_type")

            if not isinstance(action, str):
                raise OrchestrationEngineError(
                    "Execution plan must contain a string plan_type."
                )

            normalized_action = action.strip()

            if not normalized_action:
                raise OrchestrationEngineError(
                    "Execution plan plan_type must not be empty."
                )

            # -----------------------------------------------------------------
            # Phase 2: Authoritative Governance + Execution
            # -----------------------------------------------------------------
            #
            # Milestone 4:
            #
            # GovernedExecution is the authoritative governance boundary.
            #
            # It performs:
            #
            #     GovernanceDecisionBoundary
            #             |
            #       +-----+-----+-----+
            #       |           |     |
            #    Security   Compliance Authorization
            #       |
            #      Audit
            #
            # and executes only when the resulting decision is allowed.
            #
            # execute_with_decision() is deliberately used here instead of
            # execute(), because orchestration must preserve the ACTUAL
            # governance decision in its returned result.
            # -----------------------------------------------------------------

            if self._governed_execution is not None:

                governance_decision, result = (
                    self._governed_execution.execute_with_decision(
                        action=normalized_action,
                        request=normalized_request,
                        subject="orchestration",
                        resource=normalized_action,
                    )
                )

            # -----------------------------------------------------------------
            # Legacy compatibility path
            # -----------------------------------------------------------------
            #
            # This path is retained only for callers that construct an
            # OrchestrationEngine without the Milestone 4 GovernedExecution
            # dependency.
            #
            # When GovernedExecution exists, this branch is never reached.
            # -----------------------------------------------------------------

            else:

                governance_decision, result = (
                    self._execution_manager.execute_with_governance(
                        normalized_action,
                        normalized_request,
                    )
                )

            # -----------------------------------------------------------------
            # Phase 3: Structured Result
            # -----------------------------------------------------------------

            return OrchestrationResult(
                request=normalized_request,
                plan=plan,
                action=normalized_action,
                governance=governance_decision,
                result=result,
            )

        # ---------------------------------------------------------------------
        # Stable orchestration error boundary
        # ---------------------------------------------------------------------

        except OrchestrationEngineError:
            raise

        except GovernedExecutionError as exc:
            raise OrchestrationEngineError(
                str(exc)
            ) from exc

        except ExecutionManagerError as exc:
            raise OrchestrationEngineError(
                str(exc)
            ) from exc

        except Exception as exc:
            raise OrchestrationEngineError(
                "Orchestration execution failed."
            ) from exc

    # =========================================================================
    # Planning Only
    # =========================================================================

    def create_plan(
        self,
        request: str,
    ) -> dict[str, Any]:
        """
        Create an execution plan without executing it.

        This method is useful for inspection, debugging, testing, and future
        approval workflows.

        Parameters
        ----------
        request : str
            Process-analysis request.

        Returns
        -------
        dict[str, Any]
            Planner-generated execution plan.
        """

        self._validate_request(request)

        return self._planner.plan(
            request.strip()
        )

    # =========================================================================
    # Governance Check
    # =========================================================================

    def is_allowed(
        self,
        action: str,
    ) -> bool:
        """
        Determine whether an action is permitted.

        This is a compatibility/helper method.

        IMPORTANT:
        This method is NOT used by orchestrate() when GovernedExecution
        is supplied.

        The Milestone 4 authoritative execution path is:

            orchestrate()
                ->
            GovernedExecution.execute_with_decision()
                ->
            GovernanceDecisionBoundary

        This helper remains available for callers that explicitly want
        to query the legacy Governance component.
        """

        if not isinstance(action, str):
            raise ValueError(
                "action must be a string."
            )

        normalized_action = action.strip()

        if not normalized_action:
            raise ValueError(
                "action must not be empty."
            )

        return self._governance.is_allowed(
            normalized_action
        )

    # =========================================================================
    # Agent Check
    # =========================================================================

    def has_agent(
        self,
        action: str,
    ) -> bool:
        """
        Determine whether an executable agent is registered for an action.

        This method does not execute the agent.
        """

        if not isinstance(action, str):
            raise ValueError(
                "action must be a string."
            )

        normalized_action = action.strip()

        if not normalized_action:
            raise ValueError(
                "action must not be empty."
            )

        return self._agent_registry.contains(
            normalized_action
        )

    # =========================================================================
    # Validation
    # =========================================================================

    @staticmethod
    def _validate_request(
        request: str,
    ) -> None:
        """
        Validate an orchestration request.
        """

        if not isinstance(request, str):
            raise OrchestrationEngineError(
                "request must be a string."
            )

        if not request.strip():
            raise OrchestrationEngineError(
                "request must not be empty."
            )


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":

    class ExampleAgent:
        """
        Simple example process-analysis agent.
        """

        def execute(
            self,
            request: str,
        ) -> dict[str, Any]:
            """
            Return a deterministic example result.
            """

            return {
                "agent": "process_analysis",
                "request": request,
                "status": "executed",
            }

    # -------------------------------------------------------------------------
    # Build orchestration dependencies
    # -------------------------------------------------------------------------

    planner = Planner()

    registry = AgentRegistry()

    governance = Governance()

    registry.register(
        "process_analysis",
        ExampleAgent(),
    )

    execution_manager = ExecutionManager(
        agent_registry=registry,
        governance=governance,
    )

    # -------------------------------------------------------------------------
    # Build top-level engine
    # -------------------------------------------------------------------------

    engine = OrchestrationEngine(
        planner=planner,
        agent_registry=registry,
        governance=governance,
        execution_manager=execution_manager,
    )

    # -------------------------------------------------------------------------
    # Execute example request
    # -------------------------------------------------------------------------

    result = engine.orchestrate(
        "Analyse the customer onboarding process."
    )

    print("=" * 80)
    print("ORCHESTRATION ENGINE PREVIEW")
    print("=" * 80)

    print(result)