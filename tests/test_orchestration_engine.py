"""
AI Process Analyst

Module:
tests.test_orchestration_engine

Purpose:
Unit tests for the Phase 3.10 OrchestrationEngine.

Coverage:
- Dependency validation
- Request validation
- Planner integration
- Governance integration
- Agent registry integration
- Execution manager integration
- End-to-end orchestration
- Planning-only behaviour
- Governance checks
- Agent availability checks
- Deterministic behaviour
"""

from typing import Any

import pytest

from src.orchestration.agent_registry import AgentRegistry
from src.orchestration.execution_manager import ExecutionManager
from src.orchestration.governance import Governance
from src.orchestration.orchestration_engine import (
    OrchestrationEngine,
    OrchestrationEngineError,
)
from src.orchestration.planner import Planner


# =============================================================================
# Test Agent
# =============================================================================

class ExampleAgent:
    """
    Deterministic test agent.
    """

    def __init__(self) -> None:
        self.calls: list[Any] = []

    def execute(
        self,
        request: Any,
    ) -> dict[str, Any]:
        self.calls.append(request)
        return {
            "agent": "process_analysis",
            "request": request,
            "status": "executed",
        }


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def planner() -> Planner:
    return Planner()


@pytest.fixture
def registry() -> AgentRegistry:
    return AgentRegistry()


@pytest.fixture
def governance() -> Governance:
    return Governance()


@pytest.fixture
def agent() -> ExampleAgent:
    return ExampleAgent()


@pytest.fixture
def engine_components(
    planner: Planner,
    registry: AgentRegistry,
    governance: Governance,
    agent: ExampleAgent,
):
    registry.register(
        "process_analysis",
        agent,
    )

    execution_manager = ExecutionManager(
        agent_registry=registry,
        governance=governance,
    )

    engine = OrchestrationEngine(
        planner=planner,
        agent_registry=registry,
        governance=governance,
        execution_manager=execution_manager,
    )

    return engine, agent


# =============================================================================
# Initialisation
# =============================================================================

def test_orchestration_engine_initialises(
    planner: Planner,
    registry: AgentRegistry,
    governance: Governance,
):
    execution_manager = ExecutionManager(
        agent_registry=registry,
        governance=governance,
    )

    engine = OrchestrationEngine(
        planner=planner,
        agent_registry=registry,
        governance=governance,
        execution_manager=execution_manager,
    )

    assert engine is not None


def test_orchestration_engine_rejects_none_planner(
    registry: AgentRegistry,
    governance: Governance,
):
    execution_manager = ExecutionManager(
        agent_registry=registry,
        governance=governance,
    )

    with pytest.raises(
        OrchestrationEngineError,
        match="planner must not be None",
    ):
        OrchestrationEngine(
            planner=None,
            agent_registry=registry,
            governance=governance,
            execution_manager=execution_manager,
        )


def test_orchestration_engine_rejects_none_registry(
    planner: Planner,
    governance: Governance,
):
    execution_manager = ExecutionManager(
        agent_registry=AgentRegistry(),
        governance=governance,
    )

    with pytest.raises(
        OrchestrationEngineError,
        match="agent_registry must not be None",
    ):
        OrchestrationEngine(
            planner=planner,
            agent_registry=None,
            governance=governance,
            execution_manager=execution_manager,
        )


def test_orchestration_engine_rejects_none_governance(
    planner: Planner,
    registry: AgentRegistry,
):
    execution_manager = ExecutionManager(
        agent_registry=registry,
        governance=Governance(),
    )

    with pytest.raises(
        OrchestrationEngineError,
        match="governance must not be None",
    ):
        OrchestrationEngine(
            planner=planner,
            agent_registry=registry,
            governance=None,
            execution_manager=execution_manager,
        )


def test_orchestration_engine_rejects_none_execution_manager(
    planner: Planner,
    registry: AgentRegistry,
    governance: Governance,
):
    with pytest.raises(
        OrchestrationEngineError,
        match="execution_manager must not be None",
    ):
        OrchestrationEngine(
            planner=planner,
            agent_registry=registry,
            governance=governance,
            execution_manager=None,
        )


# =============================================================================
# Request Validation
# =============================================================================

def test_orchestrate_rejects_non_string_request(
    engine_components,
):
    engine, _ = engine_components

    with pytest.raises(
        OrchestrationEngineError,
        match="request must be a string",
    ):
        engine.orchestrate(123)


def test_orchestrate_rejects_empty_request(
    engine_components,
):
    engine, _ = engine_components

    with pytest.raises(
        OrchestrationEngineError,
        match="request must not be empty",
    ):
        engine.orchestrate("")


def test_orchestrate_rejects_whitespace_request(
    engine_components,
):
    engine, _ = engine_components

    with pytest.raises(
        OrchestrationEngineError,
        match="request must not be empty",
    ):
        engine.orchestrate("   ")


def test_orchestrate_normalises_request(
    engine_components,
):
    engine, agent = engine_components

    result = engine.orchestrate(
        "   Analyse customer onboarding.   "
    )

    assert result["request"] == (
        "Analyse customer onboarding."
    )

    assert agent.calls == [
        "Analyse customer onboarding."
    ]


# =============================================================================
# Planner Integration
# =============================================================================

def test_create_plan_delegates_to_planner(
    engine_components,
):
    engine, _ = engine_components

    plan = engine.create_plan(
        "Analyse customer onboarding."
    )

    assert isinstance(plan, dict)
    assert plan["request"] == (
        "Analyse customer onboarding."
    )
    assert plan["plan_type"] == "process_analysis"


def test_create_plan_does_not_execute_agent(
    engine_components,
):
    engine, agent = engine_components

    plan = engine.create_plan(
        "Analyse customer onboarding."
    )

    assert plan["plan_type"] == "process_analysis"
    assert agent.calls == []


def test_orchestrate_uses_planner_plan_type_as_action(
    engine_components,
):
    engine, agent = engine_components

    result = engine.orchestrate(
        "Analyse customer onboarding."
    )

    assert result["action"] == "process_analysis"
    assert agent.calls == [
        "Analyse customer onboarding."
    ]


# =============================================================================
# Governance Integration
# =============================================================================

def test_is_allowed_returns_true_for_governed_action(
    engine_components,
):
    engine, _ = engine_components

    assert engine.is_allowed(
        "process_analysis"
    ) is True


def test_is_allowed_returns_false_for_unknown_action(
    engine_components,
):
    engine, _ = engine_components

    assert engine.is_allowed(
        "unknown_action"
    ) is False


def test_orchestrate_rejects_ungoverned_plan(
    planner: Planner,
    registry: AgentRegistry,
    agent: ExampleAgent,
):
    governance = Governance(
        allowed_actions=[]
    )

    registry.register(
        "process_analysis",
        agent,
    )

    execution_manager = ExecutionManager(
        agent_registry=registry,
        governance=governance,
    )

    engine = OrchestrationEngine(
        planner=planner,
        agent_registry=registry,
        governance=governance,
        execution_manager=execution_manager,
    )

    with pytest.raises(
        OrchestrationEngineError,
        match="not permitted",
    ):
        engine.orchestrate(
            "Analyse customer onboarding."
        )

    assert agent.calls == []


# =============================================================================
# Agent Registry Integration
# =============================================================================

def test_has_agent_returns_true_for_registered_agent(
    engine_components,
):
    engine, _ = engine_components

    assert engine.has_agent(
        "process_analysis"
    ) is True


def test_has_agent_returns_false_for_unknown_agent(
    engine_components,
):
    engine, _ = engine_components

    assert engine.has_agent(
        "unknown_action"
    ) is False


def test_orchestrate_rejects_missing_agent(
    planner: Planner,
    registry: AgentRegistry,
    governance: Governance,
):
    execution_manager = ExecutionManager(
        agent_registry=registry,
        governance=governance,
    )

    engine = OrchestrationEngine(
        planner=planner,
        agent_registry=registry,
        governance=governance,
        execution_manager=execution_manager,
    )

    with pytest.raises(
        OrchestrationEngineError,
        match="No agent registered",
    ):
        engine.orchestrate(
            "Analyse customer onboarding."
        )


# =============================================================================
# Execution Integration
# =============================================================================

def test_orchestrate_executes_registered_agent(
    engine_components,
):
    engine, agent = engine_components

    result = engine.orchestrate(
        "Analyse customer onboarding."
    )

    assert result["result"] == {
        "agent": "process_analysis",
        "request": "Analyse customer onboarding.",
        "status": "executed",
    }

    assert agent.calls == [
        "Analyse customer onboarding."
    ]


def test_orchestrate_returns_governance_decision(
    engine_components,
):
    engine, _ = engine_components

    result = engine.orchestrate(
        "Analyse customer onboarding."
    )

    assert result["governance"] == {
        "action": "process_analysis",
        "allowed": True,
        "reason": "Action is permitted by the current policy.",
    }


def test_orchestrate_returns_execution_plan(
    engine_components,
):
    engine, _ = engine_components

    result = engine.orchestrate(
        "Analyse customer onboarding."
    )

    assert result["plan"]["plan_type"] == (
        "process_analysis"
    )

    assert result["plan"]["request"] == (
        "Analyse customer onboarding."
    )


def test_orchestrate_returns_complete_result(
    engine_components,
):
    engine, _ = engine_components

    result = engine.orchestrate(
        "Analyse customer onboarding."
    )

    assert set(result.keys()) == {
        "request",
        "plan",
        "action",
        "governance",
        "result",
    }


# =============================================================================
# Safety / Non-Execution Checks
# =============================================================================

def test_is_allowed_does_not_execute_agent(
    engine_components,
):
    engine, agent = engine_components

    assert engine.is_allowed(
        "process_analysis"
    ) is True

    assert agent.calls == []


def test_has_agent_does_not_execute_agent(
    engine_components,
):
    engine, agent = engine_components

    assert engine.has_agent(
        "process_analysis"
    ) is True

    assert agent.calls == []


def test_create_plan_does_not_execute_agent(
    engine_components,
):
    engine, agent = engine_components

    engine.create_plan(
        "Analyse customer onboarding."
    )

    assert agent.calls == []


# =============================================================================
# Determinism
# =============================================================================

def test_orchestration_is_deterministic(
    engine_components,
):
    engine, agent = engine_components

    first = engine.orchestrate(
        "Analyse customer onboarding."
    )

    second = engine.orchestrate(
        "Analyse customer onboarding."
    )

    assert first == second

    assert agent.calls == [
        "Analyse customer onboarding.",
        "Analyse customer onboarding.",
    ]


# =============================================================================
# Multiple Requests
# =============================================================================

def test_orchestration_supports_multiple_requests(
    engine_components,
):
    engine, agent = engine_components

    first = engine.orchestrate(
        "Analyse customer onboarding."
    )

    second = engine.orchestrate(
        "Analyse invoice approval."
    )

    assert first["request"] == (
        "Analyse customer onboarding."
    )

    assert second["request"] == (
        "Analyse invoice approval."
    )

    assert agent.calls == [
        "Analyse customer onboarding.",
        "Analyse invoice approval.",
    ]