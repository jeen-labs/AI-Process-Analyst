"""
===============================================================================
AI Process Analyst
===============================================================================

Module:
    tests/test_governance_backward_compatibility.py

Purpose:
    Verify that the Milestone 4 Governance Platform does not break the
    existing Milestone 3 orchestration contracts.

Milestone:
    Milestone 4 - Governance Platform

Phase:
    Phase 4.10 - Verify Backward Compatibility

Compatibility guarantees covered
--------------------------------
- Existing orchestration Governance remains usable.
- Existing OrchestrationEngine construction remains valid.
- Existing orchestration result structure remains unchanged.
- Existing governance decision structure remains unchanged.
- Existing agent execution behaviour remains unchanged.
- Existing planning-only behaviour remains unchanged.
- Existing orchestration validation remains unchanged.
- Existing deterministic behaviour remains unchanged.
- New Governance Platform imports remain additive and do not replace the
  existing orchestration Governance API.

The purpose of this test is compatibility verification, not migration of
the legacy orchestration governance implementation.

Author:
    Jeen Labs
===============================================================================
"""

# =============================================================================
# Imports
# =============================================================================

from typing import Any

import pytest

from src.governance import (
    GovernanceDecisionBoundary,
    GovernanceRequest,
)

from src.orchestration.agent_registry import AgentRegistry
from src.orchestration.contracts import OrchestrationResult
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


class CompatibilityTestAgent:
    """
    Deterministic agent used to verify the existing execution contract.

    This deliberately implements the same minimal execute() interface used
    by the existing orchestration tests.
    """

    def __init__(self) -> None:
        self.calls: list[Any] = []

    def execute(
        self,
        request: Any,
    ) -> dict[str, Any]:
        """
        Execute the compatibility test request.
        """

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
    """
    Return the existing Milestone 3 Planner.
    """

    return Planner()


@pytest.fixture
def registry() -> AgentRegistry:
    """
    Return the existing AgentRegistry.
    """

    return AgentRegistry()


@pytest.fixture
def legacy_governance() -> Governance:
    """
    Return the existing orchestration Governance implementation.

    This is intentionally NOT replaced by the new Milestone 4 Governance
    Platform. Backward compatibility requires the legacy contract to remain
    usable.
    """

    return Governance()


@pytest.fixture
def agent() -> CompatibilityTestAgent:
    """
    Return a deterministic compatibility test agent.
    """

    return CompatibilityTestAgent()


@pytest.fixture
def engine_components(
    planner: Planner,
    registry: AgentRegistry,
    legacy_governance: Governance,
    agent: CompatibilityTestAgent,
):
    """
    Construct the existing Milestone 3 orchestration stack.

    This mirrors the established OrchestrationEngine dependency structure.
    """

    registry.register(
        "process_analysis",
        agent,
    )

    execution_manager = ExecutionManager(
        agent_registry=registry,
        governance=legacy_governance,
    )

    engine = OrchestrationEngine(
        planner=planner,
        agent_registry=registry,
        governance=legacy_governance,
        execution_manager=execution_manager,
    )

    return engine, agent


# =============================================================================
# Public Governance API Compatibility
# =============================================================================


def test_new_governance_platform_is_importable():
    """
    The new Governance Platform must be available without removing the
    existing orchestration governance layer.
    """

    assert GovernanceDecisionBoundary is not None


def test_governance_request_contract_is_importable():
    """
    The new GovernanceRequest contract must be available through the public
    governance package.
    """

    assert GovernanceRequest is not None


def test_legacy_orchestration_governance_remains_importable():
    """
    The existing Milestone 3 Governance class must remain importable.
    """

    assert Governance is not None


# =============================================================================
# Legacy Orchestration Construction Compatibility
# =============================================================================


def test_existing_orchestration_engine_still_initialises(
    planner: Planner,
    registry: AgentRegistry,
    legacy_governance: Governance,
):
    """
    Existing OrchestrationEngine construction must remain valid.
    """

    execution_manager = ExecutionManager(
        agent_registry=registry,
        governance=legacy_governance,
    )

    engine = OrchestrationEngine(
        planner=planner,
        agent_registry=registry,
        governance=legacy_governance,
        execution_manager=execution_manager,
    )

    assert engine is not None


def test_existing_orchestration_dependencies_are_preserved(
    engine_components,
):
    """
    The engine must continue operating with the original Milestone 3
    dependency arrangement.
    """

    engine, agent = engine_components

    assert engine is not None
    assert agent.calls == []


# =============================================================================
# Legacy Governance Behaviour
# =============================================================================


def test_existing_governance_allows_existing_process_analysis_action(
    legacy_governance: Governance,
):
    """
    The existing process_analysis governance decision must remain allowed.
    """

    decision = legacy_governance.is_allowed(
        "process_analysis"
    )

    assert decision is True


def test_existing_governance_denies_unknown_action(
    legacy_governance: Governance,
):
    """
    Existing governance behaviour for an unknown action must remain denied.
    """

    decision = legacy_governance.is_allowed(
        "unknown_action"
    )

    assert decision is False


# =============================================================================
# Legacy Orchestration Result Contract
# =============================================================================


def test_existing_orchestration_returns_dict(
    engine_components,
):
    """
    Existing orchestration must continue returning a dictionary-compatible
    result.
    """

    engine, _ = engine_components

    result = engine.orchestrate(
        "Analyse customer onboarding."
    )

    assert isinstance(result, dict)


def test_existing_orchestration_result_keys_are_preserved(
    engine_components,
):
    """
    The established Milestone 3 result keys must remain unchanged.
    """

    engine, _ = engine_components

    result: OrchestrationResult = engine.orchestrate(
        "Analyse customer onboarding."
    )

    assert set(result.keys()) == {
        "request",
        "plan",
        "action",
        "governance",
        "result",
    }


def test_existing_orchestration_result_types_are_preserved(
    engine_components,
):
    """
    The established result field types must remain unchanged.
    """

    engine, _ = engine_components

    result: OrchestrationResult = engine.orchestrate(
        "Analyse customer onboarding."
    )

    assert isinstance(
        result["request"],
        str,
    )

    assert isinstance(
        result["plan"],
        dict,
    )

    assert isinstance(
        result["action"],
        str,
    )

    assert isinstance(
        result["governance"],
        dict,
    )

    assert isinstance(
        result["result"],
        dict,
    )


def test_existing_governance_result_is_preserved(
    engine_components,
):
    """
    The existing governance result structure must remain unchanged.
    """

    engine, _ = engine_components

    result = engine.orchestrate(
        "Analyse customer onboarding."
    )

    assert result["governance"] == {
        "action": "process_analysis",
        "allowed": True,
        "reason": "Action is permitted by the current policy.",
    }


def test_existing_execution_result_is_preserved(
    engine_components,
):
    """
    The existing execution result must remain unchanged.
    """

    engine, _ = engine_components

    result = engine.orchestrate(
        "Analyse customer onboarding."
    )

    assert result["result"] == {
        "agent": "process_analysis",
        "request": "Analyse customer onboarding.",
        "status": "executed",
    }


# =============================================================================
# Legacy Request Normalisation
# =============================================================================


def test_existing_request_normalisation_is_preserved(
    engine_components,
):
    """
    Existing request trimming behaviour must remain unchanged.
    """

    engine, _ = engine_components

    result = engine.orchestrate(
        "   Analyse customer onboarding.   "
    )

    assert result["request"] == (
        "Analyse customer onboarding."
    )


# =============================================================================
# Legacy Agent Execution Behaviour
# =============================================================================


def test_existing_registered_agent_execution_is_preserved(
    engine_components,
):
    """
    Existing registered-agent execution must continue working.
    """

    engine, agent = engine_components

    result = engine.orchestrate(
        "Analyse customer onboarding."
    )

    assert result["action"] == "process_analysis"

    assert agent.calls == [
        "Analyse customer onboarding."
    ]


def test_existing_has_agent_behaviour_is_preserved(
    engine_components,
):
    """
    Existing has_agent() behaviour must remain available.
    """

    engine, agent = engine_components

    assert engine.has_agent(
        "process_analysis"
    ) is True

    assert engine.has_agent(
        "unknown_action"
    ) is False

    assert agent.calls == []


# =============================================================================
# Legacy Non-Execution Behaviour
# =============================================================================


def test_existing_is_allowed_does_not_execute_agent(
    engine_components,
):
    """
    Governance inspection must not execute an agent.
    """

    engine, agent = engine_components

    assert engine.is_allowed(
        "process_analysis"
    ) is True

    assert agent.calls == []


def test_existing_create_plan_does_not_execute_agent(
    engine_components,
):
    """
    Planning-only behaviour must remain non-executing.
    """

    engine, agent = engine_components

    plan = engine.create_plan(
        "Analyse customer onboarding."
    )

    assert isinstance(plan, dict)

    assert plan["plan_type"] == (
        "process_analysis"
    )

    assert plan["request"] == (
        "Analyse customer onboarding."
    )

    assert agent.calls == []


# =============================================================================
# Legacy Error Behaviour
# =============================================================================


def test_existing_missing_agent_error_is_preserved(
    planner: Planner,
    registry: AgentRegistry,
    legacy_governance: Governance,
):
    """
    Existing missing-agent protection must remain unchanged.
    """

    execution_manager = ExecutionManager(
        agent_registry=registry,
        governance=legacy_governance,
    )

    engine = OrchestrationEngine(
        planner=planner,
        agent_registry=registry,
        governance=legacy_governance,
        execution_manager=execution_manager,
    )

    with pytest.raises(
        OrchestrationEngineError,
        match="No agent registered",
    ):
        engine.orchestrate(
            "Analyse customer onboarding."
        )


def test_existing_empty_request_validation_is_preserved(
    engine_components,
):
    """
    Existing empty-request validation must remain unchanged.
    """

    engine, _ = engine_components

    with pytest.raises(
        OrchestrationEngineError,
    ):
        engine.orchestrate("")


def test_existing_whitespace_request_validation_is_preserved(
    engine_components,
):
    """
    Existing whitespace-only request validation must remain unchanged.
    """

    engine, _ = engine_components

    with pytest.raises(
        OrchestrationEngineError,
    ):
        engine.orchestrate("   ")


# =============================================================================
# Determinism
# =============================================================================


def test_existing_orchestration_determinism_is_preserved(
    engine_components,
):
    """
    Identical requests must continue producing identical results.
    """

    engine, _ = engine_components

    first = engine.orchestrate(
        "Analyse customer onboarding."
    )

    second = engine.orchestrate(
        "Analyse customer onboarding."
    )

    assert first == second


# =============================================================================
# Compatibility Boundary
# =============================================================================


def test_new_governance_platform_does_not_replace_legacy_governance(
    legacy_governance: Governance,
):
    """
    Milestone 4 governance must be additive.

    The new Governance Platform and the existing orchestration Governance
    object must remain separate abstractions during the compatibility phase.
    """

    boundary = GovernanceDecisionBoundary

    assert boundary is not Governance

    assert legacy_governance.is_allowed(
        "process_analysis"
    ) is True