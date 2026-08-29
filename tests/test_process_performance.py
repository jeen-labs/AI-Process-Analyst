"""
Tests:
    Process Performance Analysis

Phase:
    Milestone 5 - Process Intelligence
    Phase 5.5 - Process Performance Analysis
"""

from datetime import datetime, timedelta, timezone

import pytest

from src.process_intelligence.process_intelligence_models import (
    ProcessEvent,
    ProcessIntelligenceDataset,
    ProcessTrace,
)

from src.process_intelligence.process_performance import (
    ActivityPerformance,
    ProcessBottleneck,
    ProcessPerformanceAnalyzer,
    ProcessPerformanceError,
    ProcessPerformanceMetric,
    ProcessPerformanceResult,
    analyze_process_performance,
)


# =============================================================================
# Helpers
# =============================================================================


def _timestamp(offset_seconds: int = 0) -> datetime:
    return datetime(
        2026,
        8,
        27,
        10,
        0,
        tzinfo=timezone.utc,
    ) + timedelta(seconds=offset_seconds)


def _trace(
    case_id: str,
    activities: tuple[str, ...],
    interval_seconds: int = 60,
) -> ProcessTrace:
    events = tuple(
        ProcessEvent(
            case_id=case_id,
            activity=activity,
            timestamp=_timestamp(
                index * interval_seconds
            ),
        )
        for index, activity in enumerate(activities)
    )

    return ProcessTrace(
        case_id=case_id,
        events=events,
    )


# =============================================================================
# Performance Metric
# =============================================================================


def test_performance_metric_is_constructible() -> None:
    metric = ProcessPerformanceMetric(
        metric="throughput",
        value=12.5,
        unit="cases_per_day",
    )

    assert metric.metric == "throughput"
    assert metric.value == 12.5
    assert metric.unit == "cases_per_day"


def test_performance_metric_rejects_empty_name() -> None:
    with pytest.raises(ProcessPerformanceError):
        ProcessPerformanceMetric(
            metric="",
            value=1,
        )


def test_performance_metric_rejects_non_numeric_value() -> None:
    with pytest.raises(ProcessPerformanceError):
        ProcessPerformanceMetric(
            metric="throughput",
            value="high",  # type: ignore[arg-type]
        )


# =============================================================================
# Activity Performance
# =============================================================================


def test_activity_performance_is_constructible() -> None:
    performance = ActivityPerformance(
        activity="approve",
        occurrence_count=3,
        total_duration_seconds=180,
        average_duration_seconds=60,
        median_duration_seconds=60,
        minimum_duration_seconds=30,
        maximum_duration_seconds=90,
    )

    assert performance.activity == "approve"
    assert performance.occurrence_count == 3
    assert performance.average_duration_seconds == 60


def test_activity_performance_rejects_negative_count() -> None:
    with pytest.raises(ProcessPerformanceError):
        ActivityPerformance(
            activity="approve",
            occurrence_count=-1,
            total_duration_seconds=0,
            average_duration_seconds=0,
            median_duration_seconds=0,
            minimum_duration_seconds=0,
            maximum_duration_seconds=0,
        )


def test_zero_occurrence_activity_requires_zero_values() -> None:
    with pytest.raises(ProcessPerformanceError):
        ActivityPerformance(
            activity="approve",
            occurrence_count=0,
            total_duration_seconds=10,
            average_duration_seconds=0,
            median_duration_seconds=0,
            minimum_duration_seconds=0,
            maximum_duration_seconds=0,
        )


# =============================================================================
# Bottleneck
# =============================================================================


def test_process_bottleneck_is_constructible() -> None:
    bottleneck = ProcessBottleneck(
        activity="approve",
        average_duration_seconds=120,
        relative_share=0.4,
        rank=1,
    )

    assert bottleneck.activity == "approve"
    assert bottleneck.rank == 1
    assert bottleneck.relative_share == 0.4


def test_process_bottleneck_rejects_invalid_share() -> None:
    with pytest.raises(ProcessPerformanceError):
        ProcessBottleneck(
            activity="approve",
            average_duration_seconds=120,
            relative_share=1.2,
            rank=1,
        )


def test_process_bottleneck_rejects_invalid_rank() -> None:
    with pytest.raises(ProcessPerformanceError):
        ProcessBottleneck(
            activity="approve",
            average_duration_seconds=120,
            relative_share=0.5,
            rank=0,
        )


# =============================================================================
# Analyzer Validation
# =============================================================================


def test_analyzer_constructs_with_default_limit() -> None:
    analyzer = ProcessPerformanceAnalyzer()

    assert analyzer.bottleneck_limit == 5


def test_analyzer_accepts_custom_bottleneck_limit() -> None:
    analyzer = ProcessPerformanceAnalyzer(
        bottleneck_limit=2,
    )

    assert analyzer.bottleneck_limit == 2


def test_analyzer_rejects_invalid_bottleneck_limit() -> None:
    with pytest.raises(ProcessPerformanceError):
        ProcessPerformanceAnalyzer(
            bottleneck_limit=0,
        )


def test_analyzer_rejects_invalid_traces() -> None:
    with pytest.raises(ProcessPerformanceError):
        ProcessPerformanceAnalyzer().analyze(
            ("invalid",),  # type: ignore[arg-type]
        )


# =============================================================================
# Case Performance
# =============================================================================


def test_analyzer_calculates_case_count() -> None:
    traces = (
        _trace(
            "case-001",
            ("receive", "approve", "complete"),
        ),
        _trace(
            "case-002",
            ("receive", "approve", "complete"),
        ),
    )

    result = ProcessPerformanceAnalyzer().analyze(traces)

    assert result.case_count == 2


def test_analyzer_calculates_event_count() -> None:
    trace = _trace(
        "case-001",
        ("receive", "approve", "complete"),
    )

    result = ProcessPerformanceAnalyzer().analyze((trace,))

    assert result.event_count == 3


def test_analyzer_calculates_average_case_duration() -> None:
    trace = _trace(
        "case-001",
        ("receive", "approve", "complete"),
        interval_seconds=60,
    )

    result = ProcessPerformanceAnalyzer().analyze((trace,))

    assert result.average_case_duration_seconds == 120


def test_analyzer_calculates_median_case_duration() -> None:
    traces = (
        _trace(
            "case-001",
            ("receive", "complete"),
            interval_seconds=60,
        ),
        _trace(
            "case-002",
            ("receive", "complete"),
            interval_seconds=120,
        ),
        _trace(
            "case-003",
            ("receive", "complete"),
            interval_seconds=180,
        ),
    )

    result = ProcessPerformanceAnalyzer().analyze(traces)

    assert result.median_case_duration_seconds == 120


def test_analyzer_calculates_minimum_case_duration() -> None:
    traces = (
        _trace(
            "case-001",
            ("receive", "complete"),
            interval_seconds=60,
        ),
        _trace(
            "case-002",
            ("receive", "complete"),
            interval_seconds=120,
        ),
    )

    result = ProcessPerformanceAnalyzer().analyze(traces)

    assert result.minimum_case_duration_seconds == 60


def test_analyzer_calculates_maximum_case_duration() -> None:
    traces = (
        _trace(
            "case-001",
            ("receive", "complete"),
            interval_seconds=60,
        ),
        _trace(
            "case-002",
            ("receive", "complete"),
            interval_seconds=120,
        ),
    )

    result = ProcessPerformanceAnalyzer().analyze(traces)

    assert result.maximum_case_duration_seconds == 120


# =============================================================================
# Activity Performance
# =============================================================================


def test_analyzer_calculates_activity_performance() -> None:
    trace = _trace(
        "case-001",
        ("receive", "approve", "complete"),
        interval_seconds=60,
    )

    result = ProcessPerformanceAnalyzer().analyze((trace,))

    approve = next(
        item
        for item in result.activity_performance
        if item.activity == "approve"
    )

    assert approve.occurrence_count == 1
    assert approve.total_duration_seconds == 60
    assert approve.average_duration_seconds == 60


def test_analyzer_does_not_assign_duration_to_final_event() -> None:
    trace = _trace(
        "case-001",
        ("receive", "approve", "complete"),
        interval_seconds=60,
    )

    result = ProcessPerformanceAnalyzer().analyze((trace,))

    complete = next(
        item
        for item in result.activity_performance
        if item.activity == "complete"
    )

    assert complete.occurrence_count == 0
    assert complete.total_duration_seconds == 0


def test_analyzer_aggregates_activity_duration_across_cases() -> None:
    traces = (
        _trace(
            "case-001",
            ("receive", "approve", "complete"),
            interval_seconds=60,
        ),
        _trace(
            "case-002",
            ("receive", "approve", "complete"),
            interval_seconds=120,
        ),
    )

    result = ProcessPerformanceAnalyzer().analyze(traces)

    receive = next(
        item
        for item in result.activity_performance
        if item.activity == "receive"
    )

    assert receive.occurrence_count == 2
    assert receive.total_duration_seconds == 180
    assert receive.average_duration_seconds == 90


# =============================================================================
# Throughput
# =============================================================================


def test_analyzer_calculates_throughput_per_day() -> None:
    trace = _trace(
        "case-001",
        ("receive", "approve", "complete"),
        interval_seconds=60,
    )

    result = ProcessPerformanceAnalyzer().analyze((trace,))

    assert result.throughput_per_day == 720.0


def test_zero_duration_case_has_zero_throughput() -> None:
    trace = _trace(
        "case-001",
        ("receive",),
    )

    result = ProcessPerformanceAnalyzer().analyze((trace,))

    assert result.throughput_per_day == 0.0


# =============================================================================
# Bottleneck Detection
# =============================================================================


def test_analyzer_identifies_bottleneck() -> None:
    trace = _trace(
        "case-001",
        (
            "receive",
            "approve",
            "complete",
        ),
        interval_seconds=60,
    )

    result = ProcessPerformanceAnalyzer().analyze((trace,))

    assert len(result.bottlenecks) >= 1
    assert result.bottlenecks[0].activity in {
        "receive",
        "approve",
    }


def test_bottlenecks_are_limited() -> None:
    trace = _trace(
        "case-001",
        (
            "a",
            "b",
            "c",
            "d",
            "e",
            "f",
        ),
        interval_seconds=60,
    )

    result = ProcessPerformanceAnalyzer(
        bottleneck_limit=2,
    ).analyze((trace,))

    assert len(result.bottlenecks) <= 2


def test_bottleneck_ranks_are_sequential() -> None:
    trace = _trace(
        "case-001",
        (
            "a",
            "b",
            "c",
            "d",
        ),
        interval_seconds=60,
    )

    result = ProcessPerformanceAnalyzer().analyze((trace,))

    assert tuple(
        item.rank
        for item in result.bottlenecks
    ) == (1, 2, 3)


# =============================================================================
# Empty Dataset
# =============================================================================


def test_empty_traces_produce_zero_result() -> None:
    result = ProcessPerformanceAnalyzer().analyze(())

    assert result.case_count == 0
    assert result.event_count == 0
    assert result.average_case_duration_seconds == 0.0
    assert result.throughput_per_day == 0.0
    assert result.activity_performance == ()
    assert result.bottlenecks == ()


# =============================================================================
# Dataset Integration
# =============================================================================


def test_analyzer_accepts_process_intelligence_dataset() -> None:
    trace = _trace(
        "case-001",
        ("receive", "approve", "complete"),
    )

    dataset = ProcessIntelligenceDataset(
        traces=(trace,),
    )

    result = ProcessPerformanceAnalyzer().analyze_dataset(
        dataset
    )

    assert result.case_count == 1
    assert result.event_count == 3


def test_analyzer_rejects_invalid_dataset() -> None:
    with pytest.raises(ProcessPerformanceError):
        ProcessPerformanceAnalyzer().analyze_dataset(
            "invalid"  # type: ignore[arg-type]
        )


# =============================================================================
# Result Validation
# =============================================================================


def test_performance_result_is_constructible() -> None:
    result = ProcessPerformanceResult(
        case_count=1,
        event_count=2,
        average_case_duration_seconds=60,
        median_case_duration_seconds=60,
        minimum_case_duration_seconds=60,
        maximum_case_duration_seconds=60,
        throughput_per_day=1440,
        activity_performance=(),
        bottlenecks=(),
        metrics=(),
    )

    assert result.case_count == 1
    assert result.throughput_per_day == 1440


def test_performance_result_rejects_negative_case_count() -> None:
    with pytest.raises(ProcessPerformanceError):
        ProcessPerformanceResult(
            case_count=-1,
            event_count=0,
            average_case_duration_seconds=0,
            median_case_duration_seconds=0,
            minimum_case_duration_seconds=0,
            maximum_case_duration_seconds=0,
            throughput_per_day=0,
            activity_performance=(),
            bottlenecks=(),
            metrics=(),
        )


# =============================================================================
# Convenience API
# =============================================================================


def test_convenience_function_analyzes_process() -> None:
    trace = _trace(
        "case-001",
        ("receive", "complete"),
        interval_seconds=60,
    )

    result = analyze_process_performance((trace,))

    assert result.case_count == 1
    assert result.average_case_duration_seconds == 60


# =============================================================================
# Immutability
# =============================================================================


def test_performance_metric_is_immutable() -> None:
    metric = ProcessPerformanceMetric(
        metric="throughput",
        value=10,
    )

    with pytest.raises(AttributeError):
        metric.value = 20  # type: ignore[misc]


# =============================================================================
# Validation Edge Cases
# =============================================================================


def test_performance_metric_rejects_non_string_unit() -> None:
    with pytest.raises(ProcessPerformanceError):
        ProcessPerformanceMetric(
            metric="Average Case Duration",
            value=120.0,
            unit=123,  # type: ignore[arg-type]
        )


def test_activity_performance_rejects_non_numeric_duration() -> None:
    with pytest.raises(ProcessPerformanceError):
        ActivityPerformance(
            activity="approve",
            occurrence_count=1,
            total_duration_seconds="60",  # type: ignore[arg-type]
            average_duration_seconds=60.0,
            median_duration_seconds=60.0,
            minimum_duration_seconds=60.0,
            maximum_duration_seconds=60.0,
        )


def test_performance_result_rejects_invalid_activity_performance() -> None:
    with pytest.raises(ProcessPerformanceError):
        ProcessPerformanceResult(
            case_count=1,
            event_count=1,
            average_case_duration_seconds=60.0,
            median_case_duration_seconds=60.0,
            minimum_case_duration_seconds=60.0,
            maximum_case_duration_seconds=60.0,
            throughput_per_day=1440.0,
            activity_performance=("invalid",),  # type: ignore[arg-type]
            bottlenecks=(),
            metrics=(),
        )