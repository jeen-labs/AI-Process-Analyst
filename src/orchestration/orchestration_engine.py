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
    Governance
        |
        v
    Execution Manager

Phase:
Milestone 3 - Enterprise AI Orchestration Layer
Phase 3.10 - Integrate Planner, Agent Registry, Governance,
and Execution Manager

Responsibilities:
- Accept an orchestration request
- Validate the request
- Generate an execution plan through Planner
- Determine the action represented by the plan
- Verify that the action is governed
- Execute the action through ExecutionManager
- Return a deterministic orchestration result

This component does NOT:
- Implement planning logic
- Register agents
- Implement governance policies
- Execute agents directly
- Call an LLM directly
- Build prompts
- Parse LLM responses

Those responsibilities remain delegated to the appropriate components.

Architecture:

Request
   |
   v
OrchestrationEngine
   |
   +----> Planner
   |          |
   |          v
   |       Execution Plan
   |
   +----> Governance
   |          |
   |          v
   |       Policy Decision
   |
   +----> AgentRegistry
   |          |
   |          v
   |       Registered Agent
   |
   +----> ExecutionManager
              |
              v
           Result

The engine is intentionally thin. It coordinates existing orchestration
components rather than duplicating their responsibilities.
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
from src.orchestration.execution_manager import ExecutionManager
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

    The engine integrates the Planner, AgentRegistry, Governance, and
    ExecutionManager without duplicating their responsibilities.
    """

    def __init__(
        self,
        planner: Planner,
        agent_registry: AgentRegistry,
        governance: Governance,
        execution_manager: ExecutionManager,
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
            Policy boundary used to approve or deny actions.

        execution_manager : ExecutionManager
            Component responsible for governed agent execution.

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
        dict[str, Any]
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
            fails, or the planned action cannot be executed.

        Notes
        -----
        This method establishes the integration-level error boundary for
        the orchestration API. Component-specific exceptions are preserved
        through exception chaining while callers receive the stable
        OrchestrationEngineError type.
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
            # Phase 2: Governance
            # -----------------------------------------------------------------

            governance_decision = self._governance.evaluate(
                normalized_action
            )

            if not isinstance(governance_decision, dict):
                raise OrchestrationEngineError(
                    "Governance must return a dictionary decision."
                )

            if not governance_decision.get("allowed"):
                raise OrchestrationEngineError(
                    governance_decision.get(
                        "reason",
                        "Action is not permitted by the current policy.",
                    )
                )

            # -----------------------------------------------------------------
            # Phase 3: Agent Discovery
            # -----------------------------------------------------------------

            if not self._agent_registry.contains(
                normalized_action
            ):
                raise OrchestrationEngineError(
                    "No agent registered for action: "
                    f"{normalized_action}"
                )

            # -----------------------------------------------------------------
            # Phase 4: Execution
            # -----------------------------------------------------------------

            result = self._execution_manager.execute(
                normalized_action,
                normalized_request,
            )

            # -----------------------------------------------------------------
            # Phase 5: Structured Result
            # -----------------------------------------------------------------

            return OrchestrationResult(
                request=normalized_request,
                plan=plan,
                action=normalized_action,
                governance=governance_decision,
                result=result,
            )

        except OrchestrationEngineError:
            raise

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

        This method does not execute the action.
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