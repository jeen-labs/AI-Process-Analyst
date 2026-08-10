"""
===============================================================================
AI Process Analyst
===============================================================================

Module:
    orchestration.agent_registry

Purpose:
    Provide a deterministic registry for agents available to the enterprise
    orchestration layer.

Responsibilities:
    - Register named agents
    - Retrieve registered agents
    - Determine whether an agent is registered
    - List registered agents
    - Prevent duplicate agent registrations
    - Validate agent registration inputs

Architecture:
    Enterprise AI Orchestration Layer

Phase:
    Milestone 3 - Enterprise AI Orchestration Layer
    Phase 3.7 - Add Agent Registry

This component does NOT:
    - Execute agents
    - Select agents for execution
    - Apply governance policies
    - Apply security policies
    - Build prompts
    - Call LLM providers
    - Manage execution state

The registry is intentionally lightweight. It establishes a stable
architectural boundary between orchestration planning and agent discovery.
===============================================================================
"""

# =============================================================================
# Standard Library Imports
# =============================================================================

from typing import Any


# =============================================================================
# Exceptions
# =============================================================================


class AgentRegistryError(ValueError):
    """
    Base exception raised for agent registry failures.
    """


class AgentAlreadyRegisteredError(AgentRegistryError):
    """
    Raised when an agent name is already registered.
    """


class AgentNotFoundError(AgentRegistryError):
    """
    Raised when a requested agent is not registered.
    """


# =============================================================================
# Agent Registry
# =============================================================================


class AgentRegistry:
    """
    Registry of agents available to the enterprise orchestration layer.

    The registry maps stable agent names to configured agent objects.

    Agent objects are intentionally treated as opaque values. The registry
    does not impose provider-specific requirements on the agent itself.
    """

    def __init__(self) -> None:
        """
        Initialise an empty agent registry.
        """

        self._agents: dict[str, Any] = {}

    # =========================================================================
    # Registration
    # =========================================================================

    def register(
        self,
        name: str,
        agent: Any,
    ) -> None:
        """
        Register an agent under a stable name.

        Parameters
        ----------
        name : str
            Unique name used to identify the agent.

        agent : Any
            Configured agent object.

        Raises
        ------
        AgentRegistryError
            If the name is invalid or the agent is None.

        AgentAlreadyRegisteredError
            If the supplied name is already registered.
        """

        self._validate_name(name)

        if agent is None:
            raise AgentRegistryError(
                "agent must not be None."
            )

        if name.strip() in self._agents:
            raise AgentAlreadyRegisteredError(
                f"Agent is already registered: {name.strip()}"
            )

        self._agents[name.strip()] = agent

    # =========================================================================
    # Retrieval
    # =========================================================================

    def get(
        self,
        name: str,
    ) -> Any:
        """
        Retrieve an agent by name.

        Parameters
        ----------
        name : str
            Registered agent name.

        Returns
        -------
        Any
            Registered agent object.

        Raises
        ------
        AgentRegistryError
            If the name is invalid.

        AgentNotFoundError
            If no agent is registered under the supplied name.
        """

        self._validate_name(name)

        normalized_name = name.strip()

        if normalized_name not in self._agents:
            raise AgentNotFoundError(
                f"Agent not found: {normalized_name}"
            )

        return self._agents[normalized_name]

    # =========================================================================
    # Existence Check
    # =========================================================================

    def contains(
        self,
        name: str,
    ) -> bool:
        """
        Determine whether an agent is registered.

        Parameters
        ----------
        name : str
            Agent name.

        Returns
        -------
        bool
            True when the agent is registered, otherwise False.

        Notes
        -----
        Invalid names return False rather than raising an exception.
        This makes the method suitable for lightweight capability checks.
        """

        if not isinstance(name, str):
            return False

        normalized_name = name.strip()

        if not normalized_name:
            return False

        return normalized_name in self._agents

    # =========================================================================
    # Listing
    # =========================================================================

    def list_agents(self) -> list[str]:
        """
        Return registered agent names in deterministic order.

        Returns
        -------
        list[str]
            Alphabetically sorted registered agent names.
        """

        return sorted(self._agents.keys())

    # =========================================================================
    # Count
    # =========================================================================

    def count(self) -> int:
        """
        Return the number of registered agents.

        Returns
        -------
        int
            Number of registered agents.
        """

        return len(self._agents)

    # =========================================================================
    # Validation
    # =========================================================================

    @staticmethod
    def _validate_name(
        name: str,
    ) -> None:
        """
        Validate an agent name.

        Parameters
        ----------
        name : str
            Agent name to validate.

        Raises
        ------
        AgentRegistryError
            If the name is not a valid non-empty string.
        """

        if not isinstance(name, str):
            raise AgentRegistryError(
                "Agent name must be a string."
            )

        if not name.strip():
            raise AgentRegistryError(
                "Agent name cannot be empty."
            )


# =============================================================================
# Main
# =============================================================================


if __name__ == "__main__":

    class ExampleAgent:
        """
        Simple example agent used for manual registry testing.
        """

        def execute(self, request: str) -> str:
            """
            Return a simple example result.
            """

            return f"Executed: {request}"


    registry = AgentRegistry()

    registry.register(
        "process_analysis",
        ExampleAgent(),
    )

    print("=" * 80)
    print("AGENT REGISTRY PREVIEW")
    print("=" * 80)
    print("Registered agents:", registry.list_agents())
    print("Agent count:", registry.count())
    print(
        "Contains process_analysis:",
        registry.contains("process_analysis"),
    )
    print(
        "Retrieved agent:",
        registry.get("process_analysis").__class__.__name__,
    )

