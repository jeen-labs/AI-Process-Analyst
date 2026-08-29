"""
Tests for Phase 5.7 - Process Optimization.
"""

import pytest

from src.process_intelligence.process_optimization import (
    OptimizationRecommendation,
    ProcessOptimizationError,
    ProcessOptimizationResult,
    ProcessOptimizer,
    optimize_process,
    optimize_processes,
)


# =============================================================================
# OptimizationRecommendation
# =============================================================================


def test_optimization_recommendation_is_immutable():
    recommendation = OptimizationRecommendation(
        target="Cycle Time",
        current_value=10.0,
        target_value=8.0,
        expected_impact=2.0,
        improvement_percentage=20.0,
        confidence=0.8,
        recommendation="Reduce Cycle Time.",
    )

    with pytest.raises(AttributeError):
        recommendation.current_value = 20.0


def test_optimization_recommendation_to_dict():
    recommendation = OptimizationRecommendation(
        target="Cycle Time",
        current_value=10.0,
        target_value=8.0,
        expected_impact=2.0,
        improvement_percentage=20.0,
        confidence=0.8,
        recommendation="Reduce Cycle Time.",
    )

    assert recommendation.to_dict() == {
        "target": "Cycle Time",
        "current_value": 10.0,
        "target_value": 8.0,
        "expected_impact": 2.0,
        "improvement_percentage": 20.0,
        "confidence": 0.8,
        "recommendation": "Reduce Cycle Time.",
        "method": "threshold_reduction",
    }


@pytest.mark.parametrize(
    "kwargs",
    [
        {
            "target": "",
            "current_value": 10.0,
            "target_value": 8.0,
            "expected_impact": 2.0,
            "improvement_percentage": 20.0,
            "confidence": 0.8,
            "recommendation": "Reduce Cycle Time.",
        },
        {
            "target": "Cycle Time",
            "current_value": -1.0,
            "target_value": 0.0,
            "expected_impact": 1.0,
            "improvement_percentage": 100.0,
            "confidence": 0.8,
            "recommendation": "Reduce Cycle Time.",
        },
        {
            "target": "Cycle Time",
            "current_value": 10.0,
            "target_value": 8.0,
            "expected_impact": 2.0,
            "improvement_percentage": 20.0,
            "confidence": 1.5,
            "recommendation": "Reduce Cycle Time.",
        },
    ],
)
def test_optimization_recommendation_rejects_invalid_values(kwargs):
    with pytest.raises(ProcessOptimizationError):
        OptimizationRecommendation(**kwargs)


# =============================================================================
# ProcessOptimizationResult
# =============================================================================


def test_optimization_result_is_immutable():
    recommendation = OptimizationRecommendation(
        target="Cycle Time",
        current_value=10.0,
        target_value=8.0,
        expected_impact=2.0,
        improvement_percentage=20.0,
        confidence=0.8,
        recommendation="Reduce Cycle Time.",
    )

    result = ProcessOptimizationResult(
        recommendations=(recommendation,),
    )

    with pytest.raises(AttributeError):
        result.recommendations = ()


def test_optimization_result_count():
    recommendation = OptimizationRecommendation(
        target="Cycle Time",
        current_value=10.0,
        target_value=8.0,
        expected_impact=2.0,
        improvement_percentage=20.0,
        confidence=0.8,
        recommendation="Reduce Cycle Time.",
    )

    result = ProcessOptimizationResult(
        recommendations=(recommendation,),
    )

    assert result.count == 1


def test_optimization_result_to_dict():
    recommendation = OptimizationRecommendation(
        target="Cycle Time",
        current_value=10.0,
        target_value=8.0,
        expected_impact=2.0,
        improvement_percentage=20.0,
        confidence=0.8,
        recommendation="Reduce Cycle Time.",
    )

    result = ProcessOptimizationResult(
        recommendations=(recommendation,),
    )

    assert result.to_dict()["recommendations"][0]["target"] == (
        "Cycle Time"
    )


# =============================================================================
# ProcessOptimizer
# =============================================================================


def test_optimize_generates_recommendation():
    optimizer = ProcessOptimizer()

    result = optimizer.optimize(
        "Cycle Time",
        current_value=10.0,
        target_value=8.0,
    )

    assert result.target == "Cycle Time"
    assert result.current_value == pytest.approx(10.0)
    assert result.target_value == pytest.approx(8.0)
    assert result.expected_impact == pytest.approx(2.0)
    assert result.improvement_percentage == pytest.approx(20.0)
    assert result.confidence == pytest.approx(0.8)
    assert result.method == "threshold_reduction"


def test_optimize_handles_zero_improvement():
    optimizer = ProcessOptimizer()

    result = optimizer.optimize(
        "Cycle Time",
        current_value=10.0,
        target_value=10.0,
    )

    assert result.expected_impact == pytest.approx(0.0)
    assert result.improvement_percentage == pytest.approx(0.0)
    assert "already meets the target" in result.recommendation


def test_optimize_handles_zero_current_value():
    optimizer = ProcessOptimizer()

    result = optimizer.optimize(
        "Defects",
        current_value=0.0,
        target_value=0.0,
    )

    assert result.expected_impact == pytest.approx(0.0)
    assert result.improvement_percentage == pytest.approx(0.0)


def test_optimize_strips_target_whitespace():
    optimizer = ProcessOptimizer()

    result = optimizer.optimize(
        "  Cycle Time  ",
        current_value=10.0,
        target_value=8.0,
    )

    assert result.target == "Cycle Time"


@pytest.mark.parametrize(
    "target",
    [
        "",
        "   ",
        None,
    ],
)
def test_optimize_rejects_invalid_target(target):
    optimizer = ProcessOptimizer()

    with pytest.raises(ProcessOptimizationError):
        optimizer.optimize(
            target,
            current_value=10.0,
            target_value=8.0,
        )


@pytest.mark.parametrize(
    "current_value",
    [
        -1,
        "10",
        True,
        None,
    ],
)
def test_optimize_rejects_invalid_current_value(current_value):
    optimizer = ProcessOptimizer()

    with pytest.raises(ProcessOptimizationError):
        optimizer.optimize(
            "Cycle Time",
            current_value=current_value,
            target_value=8.0,
        )


@pytest.mark.parametrize(
    "target_value",
    [
        -1,
        "8",
        True,
        None,
    ],
)
def test_optimize_rejects_invalid_target_value(target_value):
    optimizer = ProcessOptimizer()

    with pytest.raises(ProcessOptimizationError):
        optimizer.optimize(
            "Cycle Time",
            current_value=10.0,
            target_value=target_value,
        )


def test_optimize_rejects_target_greater_than_current():
    optimizer = ProcessOptimizer()

    with pytest.raises(ProcessOptimizationError):
        optimizer.optimize(
            "Cycle Time",
            current_value=10.0,
            target_value=12.0,
        )


@pytest.mark.parametrize(
    "confidence",
    [
        -0.1,
        1.1,
        "0.8",
        True,
        None,
    ],
)
def test_optimize_rejects_invalid_confidence(confidence):
    optimizer = ProcessOptimizer()

    with pytest.raises(ProcessOptimizationError):
        optimizer.optimize(
            "Cycle Time",
            current_value=10.0,
            target_value=8.0,
            confidence=confidence,
        )


def test_optimize_many():
    optimizer = ProcessOptimizer()

    result = optimizer.optimize_many(
        {
            "Cycle Time": (10.0, 8.0),
            "Cost": (100.0, 80.0),
        }
    )

    assert isinstance(result, ProcessOptimizationResult)
    assert result.count == 2

    assert result.recommendations[0].target == "Cycle Time"
    assert result.recommendations[0].expected_impact == pytest.approx(2.0)

    assert result.recommendations[1].target == "Cost"
    assert result.recommendations[1].expected_impact == pytest.approx(20.0)


def test_optimize_many_is_deterministic():
    optimizer = ProcessOptimizer()

    opportunities = {
        "Cycle Time": (10.0, 8.0),
        "Cost": (100.0, 80.0),
    }

    first = optimizer.optimize_many(opportunities)
    second = optimizer.optimize_many(opportunities)

    assert first == second


def test_optimize_many_rejects_invalid_input():
    optimizer = ProcessOptimizer()

    with pytest.raises(ProcessOptimizationError):
        optimizer.optimize_many([])


# =============================================================================
# Convenience Functions
# =============================================================================


def test_optimize_process_convenience_function():
    result = optimize_process(
        "Cycle Time",
        current_value=10.0,
        target_value=8.0,
    )

    assert result.expected_impact == pytest.approx(2.0)


def test_optimize_processes_convenience_function():
    result = optimize_processes(
        {
            "Cycle Time": (10.0, 8.0),
            "Cost": (100.0, 80.0),
        }
    )

    assert result.count == 2


# =============================================================================
# Validation Edge Cases
# =============================================================================


def test_optimization_recommendation_rejects_empty_method() -> None:
    with pytest.raises(ProcessOptimizationError):
        OptimizationRecommendation(
            target="Cycle Time",
            current_value=10.0,
            target_value=8.0,
            expected_impact=2.0,
            improvement_percentage=20.0,
            confidence=0.8,
            recommendation="Reduce Cycle Time.",
            method="   ",
        )


def test_optimization_result_rejects_non_tuple_recommendations() -> None:
    with pytest.raises(ProcessOptimizationError):
        ProcessOptimizationResult(
            recommendations=[
                OptimizationRecommendation(
                    target="Cycle Time",
                    current_value=10.0,
                    target_value=8.0,
                    expected_impact=2.0,
                    improvement_percentage=20.0,
                    confidence=0.8,
                    recommendation="Reduce Cycle Time.",
                )
            ],  # type: ignore[arg-type]
        )