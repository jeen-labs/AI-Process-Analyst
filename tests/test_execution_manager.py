"""
AI Process Analyst

Module: tests.test_execution_manager

Purpose:
    Test the ExecutionManager component of the enterprise
    orchestration layer.

Phase:
    Milestone 3 - Enterprise AI Orchestration Layer

Phase 3.9 - Execution Manager
"""

import pytest

from src.orchestration.agent_registry import AgentRegistry
from src.orchestration.execution_manager import (
    ExecutionManager,
    ExecutionManagerError,
)
from src.orchestration.governance import Governance


class ExampleAgent:
    """Simple deterministic test agent."""

    def execute(self, request):
        """Return a deterministic test response."""
        return {
            "agent": "example",
            "request": request,
        }


class NonExecutableAgent:
    """Agent-like object without an execute method."""


def create_manager():
    """Create an execution manager with the default policy."""

    registry = AgentRegistry()
    governance = Governance()

    return (
        ExecutionManager(
            agent_registry=registry,
            governance=governance,
        ),
        registry,
        governance,
    )


def test_execution_manager_initialises():
    """Execution manager should initialise with valid dependencies."""

    manager, _, _ = create_manager()

    assert isinstance(manager, ExecutionManager)


def test_execution_manager_rejects_none_registry():
    """Execution manager should reject a None registry."""

    governance = Governance()

    with pytest.raises(ExecutionManagerError):
        ExecutionManager(
            agent_registry=None,
            governance=governance,
        )


def test_execution_manager_rejects_none_governance():
    """Execution manager should reject None governance."""

    registry = AgentRegistry()

    with pytest.raises(ExecutionManagerError):
        ExecutionManager(
            agent_registry=registry,
            governance=None,
        )


def test_execution_manager_allows_governed_action():
    """Allowed actions should be recognised by the manager."""

    manager, registry, _ = create_manager()

    registry.register(
        "process_analysis",
        ExampleAgent(),
    )

    assert manager.is_allowed("process_analysis") is True


def test_execution_manager_denies_unknown_action():
    """Unknown actions should be denied by governance."""

    manager, _, _ = create_manager()

    assert manager.is_allowed("unknown_action") is False


def test_execution_manager_normalises_action_whitespace():
    """Action whitespace should be normalised."""

    manager, registry, _ = create_manager()

    registry.register(
        "process_analysis",
        ExampleAgent(),
    )

    result = manager.execute(
        "  process_analysis  ",
        "Analyse onboarding.",
    )

    assert result == {
        "agent": "example",
        "request": "Analyse onboarding.",
    }


def test_execution_manager_rejects_non_string_action():
    """Non-string actions should be rejected."""

    manager, _, _ = create_manager()

    with pytest.raises(ValueError):
        manager.execute(
            None,
            "Analyse onboarding.",
        )


def test_execution_manager_rejects_empty_action():
    """Empty actions should be rejected."""

    manager, _, _ = create_manager()

    with pytest.raises(ValueError):
        manager.execute(
            "",
            "Analyse onboarding.",
        )


def test_execution_manager_rejects_whitespace_action():
    """Whitespace-only actions should be rejected."""

    manager, _, _ = create_manager()

    with pytest.raises(ValueError):
        manager.execute(
            "   ",
            "Analyse onboarding.",
        )


def test_execution_manager_executes_registered_agent():
    """A governed registered agent should be executed."""

    manager, registry, _ = create_manager()

    agent = ExampleAgent()

    registry.register(
        "process_analysis",
        agent,
    )

    result = manager.execute(
        "process_analysis",
        "Analyse customer onboarding.",
    )

    assert result == {
        "agent": "example",
        "request": "Analyse customer onboarding.",
    }


def test_execution_manager_preserves_request():
    """The original request should be passed unchanged."""

    manager, registry, _ = create_manager()

    registry.register(
        "process_analysis",
        ExampleAgent(),
    )

    request = {
        "document": "customer onboarding process",
        "priority": "high",
    }

    result = manager.execute(
        "process_analysis",
        request,
    )

    assert result["request"] is request


def test_execution_manager_denies_execution_for_unknown_action():
    """A governance-denied action should not execute."""

    manager, _, _ = create_manager()

    with pytest.raises(ExecutionManagerError):
        manager.execute(
            "unknown_action",
            "Analyse onboarding.",
        )


def test_execution_manager_rejects_governed_action_without_agent():
    """
    A permitted action without a registered agent should fail
    before execution.
    """

    manager, _, _ = create_manager()

    with pytest.raises(ExecutionManagerError):
        manager.execute(
            "process_analysis",
            "Analyse onboarding.",
        )


def test_execution_manager_does_not_execute_denied_action():
    """A denied action must not reach the agent."""

    class TrackingAgent:
        def __init__(self):
            self.executed = False

        def execute(self, request):
            self.executed = True
            return request

    manager, registry, _ = create_manager()

    agent = TrackingAgent()

    registry.register(
        "process_analysis",
        agent,
    )

    with pytest.raises(ExecutionManagerError):
        manager.execute(
            "unknown_action",
            "Analyse onboarding.",
        )

    assert agent.executed is False


def test_execution_manager_rejects_non_executable_agent():
    """Registered objects must provide an execute method."""

    manager, registry, _ = create_manager()

    registry.register(
        "process_analysis",
        NonExecutableAgent(),
    )

    with pytest.raises(ExecutionManagerError):
        manager.execute(
            "process_analysis",
            "Analyse onboarding.",
        )


def test_execution_manager_is_deterministic():
    """Repeated execution should return the same result."""

    manager, registry, _ = create_manager()

    registry.register(
        "process_analysis",
        ExampleAgent(),
    )

    first = manager.execute(
        "process_analysis",
        "Analyse onboarding.",
    )

    second = manager.execute(
        "process_analysis",
        "Analyse onboarding.",
    )

    assert first == second


def test_execution_manager_supports_multiple_agents():
    """Execution manager should support multiple governed actions."""

    registry = AgentRegistry()

    governance = Governance(
        allowed_actions=[
            "process_analysis",
            "document_analysis",
        ]
    )

    manager = ExecutionManager(
        agent_registry=registry,
        governance=governance,
    )

    registry.register(
        "process_analysis",
        ExampleAgent(),
    )

    registry.register(
        "document_analysis",
        ExampleAgent(),
    )

    process_result = manager.execute(
        "process_analysis",
        "Analyse process.",
    )

    document_result = manager.execute(
        "document_analysis",
        "Analyse document.",
    )

    assert process_result == {
        "agent": "example",
        "request": "Analyse process.",
    }

    assert document_result == {
        "agent": "example",
        "request": "Analyse document.",
    }


def test_execution_manager_is_allowed_does_not_execute_agent():
    """is_allowed should only check governance."""

    class TrackingAgent:
        def __init__(self):
            self.executed = False

        def execute(self, request):
            self.executed = True
            return request

    manager, registry, _ = create_manager()

    agent = TrackingAgent()

    registry.register(
        "process_analysis",
        agent,
    )

    assert manager.is_allowed("process_analysis") is True
    assert agent.executed is False