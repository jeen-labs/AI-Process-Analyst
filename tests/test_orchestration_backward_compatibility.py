"""
AI Process Analyst

Module:
tests.test_orchestration_backward_compatibility

Purpose:
Backward-compatibility tests for the Phase 3.11 orchestration layer.

Phase:
Milestone 3 - Enterprise AI Orchestration Layer
Phase 3.11.6 - Verify Backward Compatibility

Coverage:

* Existing direct module imports
* Public package-level imports
* Existing OrchestrationEngine construction
* Existing orchestrate() behaviour
* Existing helper methods
* Existing result dictionary shape
* Existing governance behaviour
* Existing agent-registry behaviour
* Existing request normalisation
* Existing orchestration error behaviour
"""

from typing import Any

import pytest

# ---------------------------------------------------------------------------
# Existing direct module imports
# ---------------------------------------------------------------------------

from src.orchestration.agent_registry import AgentRegistry
from src.orchestration.contracts import OrchestrationResult
from src.orchestration.execution_manager import ExecutionManager
from src.orchestration.governance import Governance
from src.orchestration.orchestration_engine import (
    OrchestrationEngine as DirectOrchestrationEngine,
    OrchestrationEngineError,
)
from src.orchestration.planner import Planner

# ---------------------------------------------------------------------------
# Public package-level imports
# ---------------------------------------------------------------------------

from src.orchestration import (
    OrchestrationEngine,
    OrchestrationEngineError as PublicOrchestrationEngineError,
    OrchestrationResult as PublicOrchestrationResult,
)


# =============================================================================
# Test Agent
# =============================================================================

class BackwardCompatibilityAgent:
    """
    Deterministic test agent used to verify that existing orchestration
    behaviour remains compatible.
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
# Fixture
# =============================================================================

@pytest.fixture
def orchestration_stack():
    """
    Construct the orchestration stack using the existing public and internal
    components.
    """
    planner = Planner()
    registry = AgentRegistry()
    governance = Governance()
    agent = BackwardCompatibilityAgent()

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
# Import Compatibility
# =============================================================================

def test_direct_orchestration_engine_import_remains_compatible():
    """
    Existing callers importing OrchestrationEngine directly from its module
    must continue to receive the same class exposed by the public package.
    """
    assert DirectOrchestrationEngine is OrchestrationEngine


def test_orchestration_engine_error_import_remains_compatible():
    """
    Existing callers must continue to receive the same orchestration error
    class through both import paths.
    """
    assert OrchestrationEngineError is PublicOrchestrationEngineError


def test_orchestration_result_import_remains_compatible():
    """
    The OrchestrationResult contract must remain available through both the
    contracts module and the public orchestration package.
    """
    assert OrchestrationResult is PublicOrchestrationResult


# =============================================================================
# Construction Compatibility
# =============================================================================

def test_existing_engine_constructor_remains_compatible(
    orchestration_stack,
):
    """
    The existing four-component OrchestrationEngine constructor must continue
    to work without requiring new arguments.
    """
    engine, _ = orchestration_stack
    assert engine is not None
    assert isinstance(
        engine,
        OrchestrationEngine,
    )


# =============================================================================
# Orchestration Behaviour Compatibility
# =============================================================================

def test_existing_orchestrate_behaviour_remains_compatible(
    orchestration_stack,
):
    """
    Existing callers must continue to receive the same result structure and
    execution behaviour.
    """
    engine, agent = orchestration_stack

    result = engine.orchestrate(
        "Analyse customer onboarding."
    )

    assert result["request"] == (
        "Analyse customer onboarding."
    )

    assert result["action"] == "process_analysis"

    assert result["plan"]["plan_type"] == (
        "process_analysis"
    )

    assert result["governance"]["allowed"] is True

    assert result["result"] == {
        "agent": "process_analysis",
        "request": "Analyse customer onboarding.",
        "status": "executed",
    }

    assert agent.calls == [
        "Analyse customer onboarding."
    ]


def test_existing_result_remains_dictionary_compatible(
    orchestration_stack,
):
    """
    Existing callers that access the orchestration result as a dictionary
    must continue to work.
    """
    engine, _ = orchestration_stack

    result = engine.orchestrate(
        "Analyse customer onboarding."
    )

    assert isinstance(
        result,
        dict,
    )

    assert result["request"] == (
        "Analyse customer onboarding."
    )

    assert result["action"] == "process_analysis"

    assert result["result"]["status"] == "executed"


def test_existing_result_keys_remain_compatible(
    orchestration_stack,
):
    """
    The established result keys must remain unchanged.
    """
    engine, _ = orchestration_stack

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
# Helper Method Compatibility
# =============================================================================

def test_create_plan_remains_compatible(
    orchestration_stack,
):
    """
    Existing callers using create_plan() must continue to receive a plan
    dictionary.
    """
    engine, agent = orchestration_stack

    plan = engine.create_plan(
        "Analyse customer onboarding."
    )

    assert isinstance(
        plan,
        dict,
    )

    assert plan["request"] == (
        "Analyse customer onboarding."
    )

    assert plan["plan_type"] == "process_analysis"

    assert agent.calls == []


def test_is_allowed_remains_compatible(
    orchestration_stack,
):
    """
    Existing governance checks must continue to behave as before.
    """
    engine, _ = orchestration_stack

    assert engine.is_allowed(
        "process_analysis"
    ) is True

    assert engine.is_allowed(
        "unknown_action"
    ) is False


def test_has_agent_remains_compatible(
    orchestration_stack,
):
    """
    Existing agent availability checks must continue to behave as before.
    """
    engine, _ = orchestration_stack

    assert engine.has_agent(
        "process_analysis"
    ) is True

    assert engine.has_agent(
        "unknown_action"
    ) is False


# =============================================================================
# Request Compatibility
# =============================================================================

def test_existing_request_normalisation_remains_compatible(
    orchestration_stack,
):
    """
    Existing callers may provide surrounding whitespace. The established
    normalisation behaviour must remain unchanged.
    """
    engine, agent = orchestration_stack

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
# Error Compatibility
# =============================================================================

def test_existing_invalid_request_error_remains_compatible(
    orchestration_stack,
):
    """
    Existing invalid-request behaviour must remain unchanged.
    """
    engine, _ = orchestration_stack

    with pytest.raises(
        OrchestrationEngineError,
        match="request must be a string",
    ):
        engine.orchestrate(123)


def test_existing_empty_request_error_remains_compatible(
    orchestration_stack,
):
    """
    Existing empty-request validation must remain unchanged.
    """
    engine, _ = orchestration_stack

    with pytest.raises(
        OrchestrationEngineError,
        match="request must not be empty",
    ):
        engine.orchestrate("")


def test_existing_governance_boundary_remains_compatible():
    """
    Governance must continue to prevent execution of unapproved actions.
    """
    planner = Planner()
    registry = AgentRegistry()

    governance = Governance(
        allowed_actions=[],
    )

    agent = BackwardCompatibilityAgent()

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


def test_existing_missing_agent_error_remains_compatible():
    """
    Existing callers must continue to receive an orchestration error when
    no agent is registered for the planned action.
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
# Determinism Compatibility
# =============================================================================

def test_existing_deterministic_behaviour_remains_compatible(
    orchestration_stack,
):
    """
    Identical requests must continue to produce identical results.
    """
    engine, agent = orchestration_stack

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
# ExecutionManager Compatibility
# =============================================================================

def test_execution_manager_execute_remains_compatible():
    """
    Existing callers using ExecutionManager.execute() must continue to
    receive only the agent result.
    """

    registry = AgentRegistry()
    governance = Governance()
    agent = BackwardCompatibilityAgent()

    registry.register(
        "process_analysis",
        agent,
    )

    manager = ExecutionManager(
        agent_registry=registry,
        governance=governance,
    )

    result = manager.execute(
        "process_analysis",
        "Analyse customer onboarding.",
    )

    assert result == {
        "agent": "process_analysis",
        "request": "Analyse customer onboarding.",
        "status": "executed",
    }

    assert agent.calls == [
        "Analyse customer onboarding."
    ]


def test_execution_manager_execute_with_governance_returns_decision_and_result():
    """
    Verify the new execution-boundary method returns both the governance
    decision and the execution result.
    """

    registry = AgentRegistry()
    governance = Governance()
    agent = BackwardCompatibilityAgent()

    registry.register(
        "process_analysis",
        agent,
    )

    manager = ExecutionManager(
        agent_registry=registry,
        governance=governance,
    )

    decision, result = manager.execute_with_governance(
        "process_analysis",
        "Analyse customer onboarding.",
    )

    assert decision == {
        "action": "process_analysis",
        "allowed": True,
        "reason": "Action is permitted by the current policy.",
    }

    assert result == {
        "agent": "process_analysis",
        "request": "Analyse customer onboarding.",
        "status": "executed",
    }