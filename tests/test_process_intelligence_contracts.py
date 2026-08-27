"""
Tests:
    Process Intelligence contracts

Phase:
    Milestone 5 - Process Intelligence
    Phase 5.1 - Define Process Intelligence Contracts
"""

from __future__ import annotations

import pytest

from src.process_intelligence import (
    DigitalTwinReference,
    ProcessIntelligenceContractError,
    ProcessIntelligenceFinding,
    ProcessIntelligenceRequest,
    ProcessIntelligenceResult,
    ProcessKpiPrediction,
    ProcessObservation,
    ProcessOptimizationRecommendation,
)


# =============================================================================
# Process Intelligence Request
# =============================================================================


def test_process_intelligence_request_is_constructible() -> None:
    request = ProcessIntelligenceRequest(
        operation="analyse",
        process_id="proc-001",
        process_data={"activities": []},
    )

    assert request.operation == "analyse"
    assert request.process_id == "proc-001"
    assert request.process_data == {"activities": []}
    assert request.context == {}


def test_process_intelligence_request_rejects_empty_operation() -> None:
    with pytest.raises(ProcessIntelligenceContractError):
        ProcessIntelligenceRequest(
            operation="",
            process_id="proc-001",
            process_data={},
        )


def test_process_intelligence_request_rejects_empty_process_id() -> None:
    with pytest.raises(ProcessIntelligenceContractError):
        ProcessIntelligenceRequest(
            operation="analyse",
            process_id="",
            process_data={},
        )


def test_process_intelligence_request_rejects_invalid_context() -> None:
    with pytest.raises(ProcessIntelligenceContractError):
        ProcessIntelligenceRequest(
            operation="analyse",
            process_id="proc-001",
            process_data={},
            context=[],
        )


def test_process_intelligence_request_serializes() -> None:
    request = ProcessIntelligenceRequest(
        operation="analyse",
        process_id="proc-001",
        process_data={"activities": ["A", "B"]},
        context={"source": "test"},
    )

    assert request.to_dict() == {
        "operation": "analyse",
        "process_id": "proc-001",
        "process_data": {"activities": ["A", "B"]},
        "context": {"source": "test"},
    }


# =============================================================================
# Process Observation
# =============================================================================


def test_process_observation_is_constructible() -> None:
    observation = ProcessObservation(
        case_id="case-001",
        activity="Approve",
        timestamp="2026-08-27T10:00:00",
        resource="analyst",
        attributes={"department": "operations"},
    )

    assert observation.case_id == "case-001"
    assert observation.activity == "Approve"
    assert observation.resource == "analyst"
    assert observation.attributes["department"] == "operations"


def test_process_observation_rejects_empty_case_id() -> None:
    with pytest.raises(ProcessIntelligenceContractError):
        ProcessObservation(
            case_id="",
            activity="Approve",
            timestamp="2026-08-27T10:00:00",
        )


def test_process_observation_rejects_empty_activity() -> None:
    with pytest.raises(ProcessIntelligenceContractError):
        ProcessObservation(
            case_id="case-001",
            activity="",
            timestamp="2026-08-27T10:00:00",
        )


def test_process_observation_rejects_empty_timestamp() -> None:
    with pytest.raises(ProcessIntelligenceContractError):
        ProcessObservation(
            case_id="case-001",
            activity="Approve",
            timestamp="",
        )


# =============================================================================
# Finding
# =============================================================================


def test_process_intelligence_finding_is_constructible() -> None:
    finding = ProcessIntelligenceFinding(
        finding_type="bottleneck",
        description="Approval activity is a process bottleneck.",
        severity="warning",
        confidence=0.9,
        evidence={"activity": "Approve"},
    )

    assert finding.finding_type == "bottleneck"
    assert finding.severity == "warning"
    assert finding.confidence == 0.9
    assert finding.evidence["activity"] == "Approve"


def test_process_intelligence_finding_rejects_invalid_confidence() -> None:
    with pytest.raises(ProcessIntelligenceContractError):
        ProcessIntelligenceFinding(
            finding_type="bottleneck",
            description="Bottleneck detected.",
            confidence=1.5,
        )


def test_process_intelligence_finding_rejects_negative_confidence() -> None:
    with pytest.raises(ProcessIntelligenceContractError):
        ProcessIntelligenceFinding(
            finding_type="bottleneck",
            description="Bottleneck detected.",
            confidence=-0.1,
        )


# =============================================================================
# Result
# =============================================================================


def test_process_intelligence_result_is_constructible() -> None:
    finding = ProcessIntelligenceFinding(
        finding_type="delay",
        description="Activity delay detected.",
    )

    result = ProcessIntelligenceResult(
        operation="analyse",
        process_id="proc-001",
        status="completed",
        findings=(finding,),
        metrics={"cycle_time": 12.5},
    )

    assert result.operation == "analyse"
    assert result.process_id == "proc-001"
    assert result.status == "completed"
    assert len(result.findings) == 1
    assert result.metrics["cycle_time"] == 12.5


def test_process_intelligence_result_serializes_findings() -> None:
    finding = ProcessIntelligenceFinding(
        finding_type="delay",
        description="Activity delay detected.",
    )

    result = ProcessIntelligenceResult(
        operation="analyse",
        process_id="proc-001",
        status="completed",
        findings=(finding,),
    )

    serialized = result.to_dict()

    assert serialized["operation"] == "analyse"
    assert serialized["process_id"] == "proc-001"
    assert serialized["status"] == "completed"
    assert serialized["findings"][0]["finding_type"] == "delay"


def test_process_intelligence_result_rejects_invalid_finding_type() -> None:
    with pytest.raises(ProcessIntelligenceContractError):
        ProcessIntelligenceResult(
            operation="analyse",
            process_id="proc-001",
            status="completed",
            findings=("invalid",),
        )


# =============================================================================
# KPI Prediction
# =============================================================================


def test_process_kpi_prediction_is_constructible() -> None:
    prediction = ProcessKpiPrediction(
        metric="cycle_time",
        predicted_value=10.5,
        confidence=0.85,
        horizon="30_days",
    )

    assert prediction.metric == "cycle_time"
    assert prediction.predicted_value == 10.5
    assert prediction.confidence == 0.85
    assert prediction.horizon == "30_days"


def test_process_kpi_prediction_rejects_invalid_confidence() -> None:
    with pytest.raises(ProcessIntelligenceContractError):
        ProcessKpiPrediction(
            metric="cycle_time",
            predicted_value=10.5,
            confidence=2.0,
        )


# =============================================================================
# Optimization
# =============================================================================


def test_process_optimization_recommendation_is_constructible() -> None:
    recommendation = ProcessOptimizationRecommendation(
        recommendation="Automate approval routing.",
        rationale="Approval routing is repetitive and rule-driven.",
        expected_impact="Reduced cycle time.",
        confidence=0.8,
    )

    assert recommendation.recommendation.startswith("Automate")
    assert recommendation.expected_impact == "Reduced cycle time."
    assert recommendation.confidence == 0.8


def test_process_optimization_recommendation_rejects_empty_rationale() -> None:
    with pytest.raises(ProcessIntelligenceContractError):
        ProcessOptimizationRecommendation(
            recommendation="Automate routing.",
            rationale="",
        )


# =============================================================================
# Digital Twin
# =============================================================================


def test_digital_twin_reference_is_constructible() -> None:
    reference = DigitalTwinReference(
        twin_id="twin-001",
        process_id="proc-001",
        version="1.0",
    )

    assert reference.twin_id == "twin-001"
    assert reference.process_id == "proc-001"
    assert reference.version == "1.0"


def test_digital_twin_reference_rejects_empty_version() -> None:
    with pytest.raises(ProcessIntelligenceContractError):
        DigitalTwinReference(
            twin_id="twin-001",
            process_id="proc-001",
            version="",
        )


# =============================================================================
# Public API
# =============================================================================


def test_process_intelligence_public_exports_are_available() -> None:
    exported = {
        "DigitalTwinReference",
        "ProcessIntelligenceContractError",
        "ProcessIntelligenceFinding",
        "ProcessIntelligenceRequest",
        "ProcessIntelligenceResult",
        "ProcessKpiPrediction",
        "ProcessObservation",
        "ProcessOptimizationRecommendation",
    }

    import src.process_intelligence as process_intelligence

    assert set(process_intelligence.__all__) == exported


def test_contracts_are_immutable() -> None:
    request = ProcessIntelligenceRequest(
        operation="analyse",
        process_id="proc-001",
        process_data={},
    )

    with pytest.raises(AttributeError):
        request.operation = "changed"  # type: ignore[misc]