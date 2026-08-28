"""
===============================================================================
AI Process Analyst
===============================================================================

Test Module:
    tests.test_process_intelligence_orchestration

Purpose:
    Validate Phase 5.9 Process Intelligence / Orchestration integration.

Coverage:
    - deterministic integration
    - input validation
    - Process Intelligence result preservation
    - KPI prediction integration
    - optimization recommendation integration
    - digital twin integration
    - defensive copying
    - immutability
    - serialization
    - no autonomous execution
    - backward-compatible separation from OrchestrationEngine
===============================================================================
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from src.orchestration import (
    OrchestrationEngine,
    OrchestrationEngineError,
    OrchestrationResult,
    ProcessIntelligenceIntegration,
    ProcessIntelligenceOrchestrationError,
    ProcessIntelligenceOrchestrationResult,
    integrate_process_intelligence,
)

from src.process_intelligence import (
    DigitalTwinState,
    DigitalTwinTransition,
    ProcessDigitalTwinSnapshot,
    ProcessIntelligenceFinding,
    ProcessIntelligenceResult,
    ProcessKpiPrediction,
    ProcessOptimizationRecommendation,
)


# =============================================================================
# Fixtures / Factories
# =============================================================================


def make_process_intelligence_result() -> ProcessIntelligenceResult:
    return ProcessIntelligenceResult(
        operation="performance_analysis",
        process_id="customer_onboarding",
        status="completed",
        findings=(
            ProcessIntelligenceFinding(
                finding_type="bottleneck",
                description="Approval stage is the primary bottleneck.",
                severity="warning",
                confidence=0.9,
                evidence={
                    "activity": "approval",
                    "delay_minutes": 42,
                },
            ),
        ),
        metrics={
            "cycle_time": 120.0,
            "throughput": 15.0,
        },
    )


def make_kpi_predictions() -> tuple[ProcessKpiPrediction, ...]:
    return (
        ProcessKpiPrediction(
            metric="cycle_time",
            predicted_value=110.0,
            confidence=0.85,
            horizon="next_period",
        ),
    )


def make_recommendations() -> (
    tuple[ProcessOptimizationRecommendation, ...]
):
    return (
        ProcessOptimizationRecommendation(
            recommendation="Reduce approval delay.",
            rationale="Approval is the primary observed bottleneck.",
            expected_impact="Reduce cycle time.",
            confidence=0.8,
        ),
    )


def make_digital_twin_snapshot() -> ProcessDigitalTwinSnapshot:
    return ProcessDigitalTwinSnapshot(
        process_name="customer_onboarding",
        states=(
            DigitalTwinState(
                state_name="submitted",
                observation_count=10,
                active=False,
            ),
            DigitalTwinState(
                state_name="approval",
                observation_count=8,
                active=True,
            ),
        ),
        transitions=(
            DigitalTwinTransition(
                source_state="submitted",
                target_state="approval",
                occurrence_count=8,
            ),
        ),
        total_observations=18,
        active_state_count=1,
        transition_count=1,
        total_transition_occurrences=8,
    )


# =============================================================================
# Basic Integration
# =============================================================================


def test_integration_returns_expected_result_type() -> None:
    result = ProcessIntelligenceIntegration().integrate(
        make_process_intelligence_result(),
    )

    assert isinstance(
        result,
        ProcessIntelligenceOrchestrationResult,
    )


def test_integration_preserves_process_identity() -> None:
    result = ProcessIntelligenceIntegration().integrate(
        make_process_intelligence_result(),
    )

    assert result.process_id == "customer_onboarding"
    assert result.operation == "performance_analysis"
    assert result.status == "completed"


def test_integration_preserves_findings() -> None:
    result = ProcessIntelligenceIntegration().integrate(
        make_process_intelligence_result(),
    )

    assert result.finding_count == 1
    assert result.findings[0].finding_type == "bottleneck"
    assert result.findings[0].confidence == 0.9


def test_integration_preserves_metrics() -> None:
    result = ProcessIntelligenceIntegration().integrate(
        make_process_intelligence_result(),
    )

    assert result.metrics == {
        "cycle_time": 120.0,
        "throughput": 15.0,
    }


# =============================================================================
# KPI Prediction Integration
# =============================================================================


def test_kpi_predictions_are_integrated() -> None:
    result = ProcessIntelligenceIntegration().integrate(
        make_process_intelligence_result(),
        kpi_predictions=make_kpi_predictions(),
    )

    assert result.prediction_count == 1
    assert result.kpi_predictions[0].metric == "cycle_time"
    assert result.kpi_predictions[0].predicted_value == 110.0


def test_kpi_predictions_are_optional() -> None:
    result = ProcessIntelligenceIntegration().integrate(
        make_process_intelligence_result(),
    )

    assert result.prediction_count == 0
    assert result.kpi_predictions == ()


def test_invalid_kpi_predictions_are_rejected() -> None:
    with pytest.raises(
        ProcessIntelligenceOrchestrationError,
        match="kpi_predictions",
    ):
        ProcessIntelligenceIntegration().integrate(
            make_process_intelligence_result(),
            kpi_predictions=["invalid"],
        )


def test_string_kpi_predictions_are_rejected() -> None:
    with pytest.raises(
        ProcessIntelligenceOrchestrationError,
        match="kpi_predictions",
    ):
        ProcessIntelligenceIntegration().integrate(
            make_process_intelligence_result(),
            kpi_predictions="invalid",
        )


# =============================================================================
# Optimization Recommendation Integration
# =============================================================================


def test_optimization_recommendations_are_integrated() -> None:
    result = ProcessIntelligenceIntegration().integrate(
        make_process_intelligence_result(),
        optimization_recommendations=make_recommendations(),
    )

    assert result.recommendation_count == 1

    recommendation = result.optimization_recommendations[0]

    assert recommendation.recommendation == (
        "Reduce approval delay."
    )
    assert recommendation.confidence == 0.8


def test_optimization_recommendations_are_optional() -> None:
    result = ProcessIntelligenceIntegration().integrate(
        make_process_intelligence_result(),
    )

    assert result.recommendation_count == 0
    assert result.optimization_recommendations == ()


def test_invalid_optimization_recommendations_are_rejected() -> None:
    with pytest.raises(
        ProcessIntelligenceOrchestrationError,
        match="optimization_recommendations",
    ):
        ProcessIntelligenceIntegration().integrate(
            make_process_intelligence_result(),
            optimization_recommendations=["invalid"],
        )


# =============================================================================
# Digital Twin Integration
# =============================================================================


def test_digital_twin_snapshot_is_integrated() -> None:
    snapshot = make_digital_twin_snapshot()

    result = ProcessIntelligenceIntegration().integrate(
        make_process_intelligence_result(),
        digital_twin_snapshot=snapshot,
    )

    assert result.has_digital_twin is True
    assert result.digital_twin_snapshot is not None
    assert (
        result.digital_twin_snapshot.process_name
        == "customer_onboarding"
    )


def test_digital_twin_snapshot_is_optional() -> None:
    result = ProcessIntelligenceIntegration().integrate(
        make_process_intelligence_result(),
    )

    assert result.has_digital_twin is False
    assert result.digital_twin_snapshot is None


def test_invalid_digital_twin_snapshot_is_rejected() -> None:
    with pytest.raises(
        ProcessIntelligenceOrchestrationError,
        match="digital_twin_snapshot",
    ):
        ProcessIntelligenceIntegration().integrate(
            make_process_intelligence_result(),
            digital_twin_snapshot="invalid",
        )


# =============================================================================
# Full Integration
# =============================================================================


def test_all_process_intelligence_outputs_can_be_integrated() -> None:
    result = ProcessIntelligenceIntegration().integrate(
        make_process_intelligence_result(),
        kpi_predictions=make_kpi_predictions(),
        optimization_recommendations=make_recommendations(),
        digital_twin_snapshot=make_digital_twin_snapshot(),
    )

    assert result.process_id == "customer_onboarding"
    assert result.finding_count == 1
    assert result.prediction_count == 1
    assert result.recommendation_count == 1
    assert result.has_digital_twin is True


def test_convenience_api_matches_class_api() -> None:
    result = integrate_process_intelligence(
        make_process_intelligence_result(),
        kpi_predictions=make_kpi_predictions(),
        optimization_recommendations=make_recommendations(),
        digital_twin_snapshot=make_digital_twin_snapshot(),
    )

    assert isinstance(
        result,
        ProcessIntelligenceOrchestrationResult,
    )

    assert result.finding_count == 1
    assert result.prediction_count == 1
    assert result.recommendation_count == 1
    assert result.has_digital_twin is True


# =============================================================================
# Validation
# =============================================================================


def test_invalid_process_intelligence_result_is_rejected() -> None:
    with pytest.raises(
        ProcessIntelligenceOrchestrationError,
        match="process_intelligence_result",
    ):
        ProcessIntelligenceIntegration().integrate(
            "invalid",
        )


# =============================================================================
# Immutability
# =============================================================================


def test_integrated_result_is_frozen() -> None:
    result = ProcessIntelligenceIntegration().integrate(
        make_process_intelligence_result(),
    )

    with pytest.raises(FrozenInstanceError):
        result.status = "changed"  # type: ignore[misc]


def test_integrated_result_uses_tuple_for_findings() -> None:
    result = ProcessIntelligenceIntegration().integrate(
        make_process_intelligence_result(),
    )

    assert isinstance(result.findings, tuple)


def test_integrated_result_uses_tuple_for_predictions() -> None:
    result = ProcessIntelligenceIntegration().integrate(
        make_process_intelligence_result(),
        kpi_predictions=make_kpi_predictions(),
    )

    assert isinstance(result.kpi_predictions, tuple)


def test_integrated_result_uses_tuple_for_recommendations() -> None:
    result = ProcessIntelligenceIntegration().integrate(
        make_process_intelligence_result(),
        optimization_recommendations=make_recommendations(),
    )

    assert isinstance(
        result.optimization_recommendations,
        tuple,
    )


# =============================================================================
# Defensive Copying
# =============================================================================


def test_metrics_are_defensively_copied() -> None:
    source = make_process_intelligence_result()

    result = ProcessIntelligenceIntegration().integrate(
        source,
    )

    assert result.metrics == source.metrics
    assert result.metrics is not source.metrics


def test_findings_are_defensively_copied() -> None:
    source = make_process_intelligence_result()

    result = ProcessIntelligenceIntegration().integrate(
        source,
    )

    assert result.findings[0] == source.findings[0]
    assert result.findings[0] is not source.findings[0]


def test_kpi_predictions_are_defensively_copied() -> None:
    source_prediction = make_kpi_predictions()[0]

    result = ProcessIntelligenceIntegration().integrate(
        make_process_intelligence_result(),
        kpi_predictions=(source_prediction,),
    )

    assert result.kpi_predictions[0] == source_prediction
    assert result.kpi_predictions[0] is not source_prediction


def test_recommendations_are_defensively_copied() -> None:
    source_recommendation = make_recommendations()[0]

    result = ProcessIntelligenceIntegration().integrate(
        make_process_intelligence_result(),
        optimization_recommendations=(source_recommendation,),
    )

    assert (
        result.optimization_recommendations[0]
        == source_recommendation
    )

    assert (
        result.optimization_recommendations[0]
        is not source_recommendation
    )


def test_digital_twin_snapshot_is_defensively_copied() -> None:
    source = make_digital_twin_snapshot()

    result = ProcessIntelligenceIntegration().integrate(
        make_process_intelligence_result(),
        digital_twin_snapshot=source,
    )

    assert result.digital_twin_snapshot == source
    assert result.digital_twin_snapshot is not source


# =============================================================================
# Determinism
# =============================================================================


def test_same_inputs_produce_same_output() -> None:
    source = make_process_intelligence_result()
    predictions = make_kpi_predictions()
    recommendations = make_recommendations()
    snapshot = make_digital_twin_snapshot()

    first = ProcessIntelligenceIntegration().integrate(
        source,
        predictions,
        recommendations,
        snapshot,
    )

    second = ProcessIntelligenceIntegration().integrate(
        source,
        predictions,
        recommendations,
        snapshot,
    )

    assert first.to_dict() == second.to_dict()


# =============================================================================
# Serialization
# =============================================================================


def test_to_dict_contains_all_integrated_outputs() -> None:
    result = ProcessIntelligenceIntegration().integrate(
        make_process_intelligence_result(),
        kpi_predictions=make_kpi_predictions(),
        optimization_recommendations=make_recommendations(),
        digital_twin_snapshot=make_digital_twin_snapshot(),
    )

    data = result.to_dict()

    assert data["process_id"] == "customer_onboarding"
    assert data["operation"] == "performance_analysis"
    assert data["status"] == "completed"

    assert len(data["findings"]) == 1
    assert len(data["kpi_predictions"]) == 1
    assert len(data["optimization_recommendations"]) == 1

    assert data["digital_twin_snapshot"] is not None

    assert data["finding_count"] == 1
    assert data["prediction_count"] == 1
    assert data["recommendation_count"] == 1
    assert data["has_digital_twin"] is True


# =============================================================================
# No Autonomous Execution
# =============================================================================


def test_integration_does_not_require_orchestration_engine() -> None:
    """
    Process Intelligence integration is intentionally independent of
    OrchestrationEngine execution dependencies.
    """
    result = ProcessIntelligenceIntegration().integrate(
        make_process_intelligence_result(),
    )

    assert result.process_id == "customer_onboarding"


def test_integration_does_not_execute_optimization_recommendations() -> None:
    """
    Optimization recommendations remain analytical information only.
    """
    result = ProcessIntelligenceIntegration().integrate(
        make_process_intelligence_result(),
        optimization_recommendations=make_recommendations(),
    )

    recommendation = result.optimization_recommendations[0]

    assert recommendation.recommendation == (
        "Reduce approval delay."
    )

    # No execution result, execution status, or execution callback exists.
    assert not hasattr(
        result,
        "execute",
    )


def test_integration_does_not_execute_digital_twin_transitions() -> None:
    """
    Digital-twin transitions remain descriptive only.
    """
    result = ProcessIntelligenceIntegration().integrate(
        make_process_intelligence_result(),
        digital_twin_snapshot=make_digital_twin_snapshot(),
    )

    assert result.digital_twin_snapshot is not None

    assert not hasattr(
        result.digital_twin_snapshot,
        "execute",
    )


# =============================================================================
# Backward Compatibility
# =============================================================================


def test_existing_orchestration_engine_exports_remain_available() -> None:
    assert OrchestrationEngine is not None
    assert OrchestrationEngineError is not None
    assert OrchestrationResult is not None


def test_integration_does_not_change_orchestration_result_contract() -> None:
    """
    The Phase 5.9 integration object is separate from OrchestrationResult.

    Existing callers of the orchestration engine therefore retain the
    existing structural contract.
    """
    assert set(OrchestrationResult.__annotations__.keys()) == {
        "request",
        "plan",
        "action",
        "governance",
        "result",
    }