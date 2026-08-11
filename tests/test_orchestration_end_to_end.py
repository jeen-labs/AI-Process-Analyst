"""
AI Process Analyst

Module:
tests.test_orchestration_end_to_end

Purpose:
End-to-end integration tests for the enterprise orchestration layer.

Phase:
Milestone 3 - Enterprise AI Orchestration Layer
Phase 3.11.5 - Add End-to-End Integration Tests

Coverage:

* Public orchestration package entry point
* Real Planner integration
* Real Governance integration
* Real AgentRegistry integration
* Real ExecutionManager integration
* Complete orchestration execution path
* Stable OrchestrationResult contract
* Multiple end-to-end requests
* Governance rejection
* Missing-agent rejection
"""

from typing import Any

import pytest

from src.orchestration import (
    OrchestrationEngine,
    OrchestrationEngineError,
)
from src.orchestration.agent_registry import AgentRegistry
from src.orchestration.execution_manager import ExecutionManager
from src.orchestration.governance import Governance
from src.orchestration.planner import Planner


# =============================================================================
# End-to-End Test Agent
# =============================================================================

class EndToEndAgent:
    """
    Deterministic agent used by the real orchestration stack.
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
def end_to_end_components():
    """
    Construct the real orchestration dependency graph.

    No Planner, Governance, or ExecutionManager test doubles are used.
    """
    planner = Planner()
    registry = AgentRegistry()
    governance = Governance()
    agent = EndToEndAgent()

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
# Complete End-to-End Execution
# =============================================================================

def test_end_to_end_orchestration_executes_complete_stack(
    end_to_end_components,
):
    """
    Verify the complete orchestration path:

    request
        -> Planner
        -> Governance
        -> AgentRegistry
        -> ExecutionManager
        -> Agent
        -> OrchestrationResult
    """
    engine, agent = end_to_end_components

    result = engine.orchestrate(
        "Analyse customer onboarding."
    )

    assert isinstance(result, dict)

    assert result["request"] == (
        "Analyse customer onboarding."
    )

    assert result["action"] == "process_analysis"

    assert result["plan"]["request"] == (
        "Analyse customer onboarding."
    )

    assert result["plan"]["plan_type"] == (
        "process_analysis"
    )

    assert result["governance"] == {
        "action": "process_analysis",
        "allowed": True,
        "reason": "Action is permitted by the current policy.",
    }

    assert result["result"] == {
        "agent": "process_analysis",
        "request": "Analyse customer onboarding.",
        "status": "executed",
    }

    assert agent.calls == [
        "Analyse customer onboarding."
    ]


# =============================================================================
# Public Package Entry Point
# =============================================================================

def test_end_to_end_uses_public_orchestration_package_api(
    end_to_end_components,
):
    """
    Verify that the end-to-end orchestration flow works through the
    stable package-level OrchestrationEngine import.
    """
    engine, _ = end_to_end_components

    assert isinstance(
        engine,
        OrchestrationEngine,
    )

    result = engine.orchestrate(
        "Analyse invoice approval."
    )

    assert isinstance(result, dict)

    assert result["request"] == (
        "Analyse invoice approval."
    )

    assert result["action"] == "process_analysis"


# =============================================================================
# Request Normalisation Through Complete Stack
# =============================================================================

def test_end_to_end_preserves_request_normalisation(
    end_to_end_components,
):
    """
    Verify that request normalisation survives the complete
    orchestration path.
    """
    engine, agent = end_to_end_components

    result = engine.orchestrate(
        "   Analyse customer onboarding.   "
    )

    assert result["request"] == (
        "Analyse customer onboarding."
    )

    assert result["result"]["request"] == (
        "Analyse customer onboarding."
    )

    assert agent.calls == [
        "Analyse customer onboarding."
    ]


# =============================================================================
# Multiple End-to-End Requests
# =============================================================================

def test_end_to_end_supports_multiple_requests(
    end_to_end_components,
):
    """
    Verify that the same real orchestration stack can process
    multiple independent requests.
    """
    engine, agent = end_to_end_components

    first = engine.orchestrate(
        "Analyse customer onboarding."
    )

    second = engine.orchestrate(
        "Analyse invoice approval."
    )

    assert first["request"] == (
        "Analyse customer onboarding."
    )

    assert first["action"] == "process_analysis"

    assert second["request"] == (
        "Analyse invoice approval."
    )

    assert second["action"] == "process_analysis"

    assert agent.calls == [
        "Analyse customer onboarding.",
        "Analyse invoice approval.",
    ]


# =============================================================================
# Governance Boundary
# =============================================================================

def test_end_to_end_governance_rejection_prevents_execution():
    """
    Verify that governance remains a hard boundary in the complete
    orchestration path.
    """
    planner = Planner()
    registry = AgentRegistry()

    governance = Governance(
        allowed_actions=[],
    )

    agent = EndToEndAgent()

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
# Agent Registry Boundary
# =============================================================================

def test_end_to_end_missing_agent_prevents_execution():
    """
    Verify that a valid planned and governed action cannot execute when
    the required agent is absent.
    """
    planner = Planner()
    registry = AgentRegistry()
    governance = Governance()

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
# Deterministic End-to-End Behaviour
# =============================================================================

def test_end_to_end_result_is_deterministic(
    end_to_end_components,
):
    """
    Verify that identical requests produce identical complete results
    through the real orchestration stack.
    """
    engine, agent = end_to_end_components

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