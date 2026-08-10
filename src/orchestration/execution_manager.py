"""
AI Process Analyst

Module: src.orchestration.execution_manager

Purpose:
    Execute governed actions through registered agents.

Phase:
    Milestone 3 - Enterprise AI Orchestration Layer

Phase 3.9 - Execution Manager
"""

from typing import Any

from src.orchestration.agent_registry import AgentRegistry
from src.orchestration.governance import Governance


class ExecutionManagerError(ValueError):
    """Base exception for execution manager errors."""


class ExecutionManager:
    """
    Execute actions through registered agents after governance approval.

    The execution manager is responsible for:

    1. Validating the requested action.
    2. Checking whether governance permits the action.
    3. Retrieving the corresponding agent from the registry.
    4. Executing the agent.
    5. Returning the agent's result.

    It does not perform planning or agent registration itself.
    """

    def __init__(
        self,
        agent_registry: AgentRegistry,
        governance: Governance,
    ) -> None:
        """
        Initialise the execution manager.

        Parameters
        ----------
        agent_registry : AgentRegistry
            Registry containing executable agents.

        governance : Governance
            Governance policy used to approve or deny actions.

        Raises
        ------
        ExecutionManagerError
            If either dependency is None.
        """

        if agent_registry is None:
            raise ExecutionManagerError(
                "agent_registry must not be None."
            )

        if governance is None:
            raise ExecutionManagerError(
                "governance must not be None."
            )

        self._agent_registry = agent_registry
        self._governance = governance

    def execute(
        self,
        action: str,
        request: Any,
    ) -> Any:
        """
        Execute a governed action.

        Parameters
        ----------
        action : str
            Name of the action to execute.

        request : Any
            Request passed to the registered agent.

        Returns
        -------
        Any
            Result returned by the registered agent.

        Raises
        ------
        ValueError
            If the action is invalid.

        ExecutionManagerError
            If governance denies the action or the action has no
            registered agent.
        """

        normalized_action = self._validate_action(action)

        decision = self._governance.evaluate(normalized_action)

        if not decision["allowed"]:
            raise ExecutionManagerError(
                decision["reason"]
            )

        if not self._agent_registry.contains(normalized_action):
            raise ExecutionManagerError(
                f"No agent registered for action: {normalized_action}"
            )

        agent = self._agent_registry.get(normalized_action)

        if not hasattr(agent, "execute"):
            raise ExecutionManagerError(
                f"Registered agent cannot execute action: "
                f"{normalized_action}"
            )

        return agent.execute(request)

    def is_allowed(self, action: str) -> bool:
        """
        Determine whether an action is permitted by governance.

        This method does not execute the action.
        """

        normalized_action = self._validate_action(action)

        return self._governance.is_allowed(normalized_action)

    @staticmethod
    def _validate_action(action: str) -> str:
        """
        Validate and normalise an action name.
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

        return normalized_action


if __name__ == "__main__":
    from src.orchestration.agent_registry import AgentRegistry

    class ExampleAgent:
        """Simple demonstration agent."""

        def execute(self, request: Any) -> dict[str, Any]:
            return {
                "agent": "example",
                "request": request,
            }

    registry = AgentRegistry()
    governance = Governance()

    registry.register(
        "process_analysis",
        ExampleAgent(),
    )

    manager = ExecutionManager(
        agent_registry=registry,
        governance=governance,
    )

    print("EXECUTION MANAGER PREVIEW")
    print(
        manager.execute(
            "process_analysis",
            "Analyse customer onboarding.",
        )
    )