"""
===============================================================================
AI Process Analyst
===============================================================================

Tests:
    Process Mining

Milestone:
    Milestone 5 - Process Intelligence

Phase:
    Phase 5.2 - Implement Process Mining

Responsibilities tested:
    - Process variant identification.
    - Activity frequency analysis.
    - Directly-follows transition analysis.
    - Activity duration aggregation.
    - Case duration calculation.
    - Basic process metrics.
    - Deterministic ordering.
    - Empty datasets.
    - Invalid input handling.
    - Convenience Process Mining API.
===============================================================================
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from src.process_intelligence.process_intelligence_models import (
    ProcessEvent,
    ProcessTrace,
)
from src.process_intelligence.process_mining import (
    ProcessMiner,
    ProcessMiningError,
    ProcessMiningResult,
    ProcessVariant,
    mine_process,
)


# =============================================================================
# Helpers
# =============================================================================


def _timestamp(offset_seconds: int = 0) -> datetime:
    """
    Return a deterministic UTC timestamp.
    """

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
    """
    Build a deterministic ProcessTrace from an activity sequence.
    """

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
# Process Variant
# =============================================================================


def test_process_variant_can_be_created() -> None:
    variant = ProcessVariant(
        activities=(
            "receive",
            "approve",
            "complete",
        ),
        occurrence_count=3,
    )

    assert variant.activities == (
        "receive",
        "approve",
        "complete",
    )
    assert variant.occurrence_count == 3


def test_process_variant_rejects_invalid_activities() -> None:
    with pytest.raises(ProcessMiningError):
        ProcessVariant(
            activities=("receive", ""),
            occurrence_count=1,
        )


def test_process_variant_rejects_negative_occurrence_count() -> None:
    with pytest.raises(ProcessMiningError):
        ProcessVariant(
            activities=("receive",),
            occurrence_count=-1,
        )


# =============================================================================
# Basic Mining
# =============================================================================


def test_process_miner_can_mine_single_trace() -> None:
    trace = _trace(
        "case-001",
        (
            "receive",
            "approve",
            "complete",
        ),
    )

    result = ProcessMiner().mine((trace,))

    assert isinstance(result, ProcessMiningResult)
    assert result.case_count == 1
    assert result.event_count == 3
    assert result.activity_count == 3
    assert result.transition_count == 2
    assert result.variant_count == 1


def test_process_mining_convenience_function() -> None:
    trace = _trace(
        "case-001",
        (
            "receive",
            "approve",
            "complete",
        ),
    )

    result = mine_process((trace,))

    assert isinstance(result, ProcessMiningResult)
    assert result.case_count == 1
    assert result.event_count == 3


# =============================================================================
# Activity Frequency
# =============================================================================


def test_process_mining_calculates_activity_frequencies() -> None:
    traces = (
        _trace(
            "case-001",
            (
                "receive",
                "approve",
                "complete",
            ),
        ),
        _trace(
            "case-002",
            (
                "receive",
                "approve",
                "complete",
            ),
        ),
    )

    result = ProcessMiner().mine(traces)

    observations = {
        observation.activity: observation
        for observation in result.activity_observations
    }

    assert observations["receive"].occurrence_count == 2
    assert observations["approve"].occurrence_count == 2
    assert observations["complete"].occurrence_count == 2


def test_process_mining_activity_observations_are_deterministically_ordered() -> None:
    trace = _trace(
        "case-001",
        (
            "z_activity",
            "a_activity",
            "m_activity",
        ),
    )

    result = ProcessMiner().mine((trace,))

    assert tuple(
        observation.activity
        for observation in result.activity_observations
    ) == (
        "a_activity",
        "m_activity",
        "z_activity",
    )


# =============================================================================
# Activity Duration
# =============================================================================


def test_process_mining_calculates_activity_duration() -> None:
    trace = _trace(
        "case-001",
        (
            "receive",
            "approve",
            "complete",
        ),
        interval_seconds=60,
    )

    result = ProcessMiner().mine((trace,))

    observations = {
        observation.activity: observation
        for observation in result.activity_observations
    }

    assert observations["receive"].total_duration_seconds == 60
    assert observations["approve"].total_duration_seconds == 60
    assert observations["complete"].total_duration_seconds == 0


def test_process_mining_calculates_average_activity_duration() -> None:
    traces = (
        _trace(
            "case-001",
            (
                "receive",
                "approve",
            ),
            interval_seconds=60,
        ),
        _trace(
            "case-002",
            (
                "receive",
                "approve",
            ),
            interval_seconds=120,
        ),
    )

    result = ProcessMiner().mine(traces)

    observations = {
        observation.activity: observation
        for observation in result.activity_observations
    }

    assert observations["receive"].occurrence_count == 2
    assert observations["receive"].total_duration_seconds == 180
    assert observations["receive"].average_duration_seconds == 90


# =============================================================================
# Transition Mining
# =============================================================================


def test_process_mining_calculates_directly_follows_transitions() -> None:
    traces = (
        _trace(
            "case-001",
            (
                "receive",
                "approve",
                "complete",
            ),
        ),
        _trace(
            "case-002",
            (
                "receive",
                "approve",
                "complete",
            ),
        ),
    )

    result = ProcessMiner().mine(traces)

    transitions = {
        (
            observation.source_activity,
            observation.target_activity,
        ): observation.occurrence_count
        for observation in result.transition_observations
    }

    assert transitions[("receive", "approve")] == 2
    assert transitions[("approve", "complete")] == 2


def test_process_mining_transition_observations_are_deterministically_ordered() -> None:
    traces = (
        _trace(
            "case-001",
            (
                "z",
                "b",
                "c",
            ),
        ),
        _trace(
            "case-002",
            (
                "a",
                "b",
                "c",
            ),
    ),
    )

    result = ProcessMiner().mine(traces)

    transitions = tuple(
        (
            observation.source_activity,
            observation.target_activity,
        )
        for observation in result.transition_observations
    )

    assert transitions == (
        ("a", "b"),
        ("b", "c"),
        ("z", "b"),
    )


# =============================================================================
# Process Variants
# =============================================================================


def test_process_mining_identifies_process_variants() -> None:
    traces = (
        _trace(
            "case-001",
            (
                "receive",
                "approve",
                "complete",
            ),
        ),
        _trace(
            "case-002",
            (
                "receive",
                "approve",
                "complete",
            ),
        ),
        _trace(
            "case-003",
            (
                "receive",
                "reject",
            ),
        ),
    )

    result = ProcessMiner().mine(traces)

    assert len(result.variants) == 2

    assert result.variants[0] == ProcessVariant(
        activities=(
            "receive",
            "approve",
            "complete",
        ),
        occurrence_count=2,
    )

    assert result.variants[1] == ProcessVariant(
        activities=(
            "receive",
            "reject",
        ),
        occurrence_count=1,
    )


def test_process_variants_are_ordered_by_frequency_then_sequence() -> None:
    traces = (
        _trace(
            "case-001",
            (
                "b",
                "complete",
            ),
        ),
        _trace(
            "case-002",
            (
                "a",
                "complete",
            ),
        ),
        _trace(
            "case-003",
            (
                "a",
                "complete",
            ),
        ),
    )

    result = ProcessMiner().mine(traces)

    assert result.variants[0].activities == (
        "a",
        "complete",
    )
    assert result.variants[0].occurrence_count == 2

    assert result.variants[1].activities == (
        "b",
        "complete",
    )
    assert result.variants[1].occurrence_count == 1


# =============================================================================
# Metrics
# =============================================================================


def test_process_mining_calculates_case_metrics() -> None:
    traces = (
        _trace(
            "case-001",
            (
                "receive",
                "approve",
                "complete",
            ),
            interval_seconds=60,
        ),
        _trace(
            "case-002",
            (
                "receive",
                "approve",
                "complete",
            ),
            interval_seconds=120,
        ),
    )

    result = ProcessMiner().mine(traces)

    assert result.metrics.case_count == 2
    assert result.metrics.event_count == 6
    assert result.metrics.activity_count == 3
    assert result.metrics.transition_count == 2
    assert result.metrics.average_case_duration_seconds == 180


def test_process_mining_calculates_throughput_per_day() -> None:
    trace = _trace(
        "case-001",
        (
            "receive",
            "approve",
            "complete",
        ),
        interval_seconds=60,
    )

    result = ProcessMiner().mine((trace,))

    assert result.metrics.throughput_per_day == 720.0


def test_process_mining_zero_duration_case_has_zero_throughput() -> None:
    trace = _trace(
        "case-001",
        (
            "receive",
        ),
    )

    result = ProcessMiner().mine((trace,))

    assert result.metrics.average_case_duration_seconds == 0.0
    assert result.metrics.throughput_per_day == 0.0


# =============================================================================
# Empty Dataset
# =============================================================================


def test_process_mining_accepts_empty_trace_collection() -> None:
    result = ProcessMiner().mine(())

    assert result.case_count == 0
    assert result.event_count == 0
    assert result.activity_count == 0
    assert result.transition_count == 0
    assert result.variant_count == 0
    assert result.activity_observations == ()
    assert result.transition_observations == ()
    assert result.variants == ()
    assert result.metrics.average_case_duration_seconds == 0.0
    assert result.metrics.throughput_per_day == 0.0


def test_process_mining_accepts_empty_trace() -> None:
    trace = ProcessTrace(
        case_id="case-empty",
        events=(),
    )

    result = ProcessMiner().mine((trace,))

    assert result.case_count == 1
    assert result.event_count == 0
    assert result.variant_count == 1
    assert result.variants[0].activities == ()
    assert result.variants[0].occurrence_count == 1


# =============================================================================
# Invalid Input
# =============================================================================


def test_process_mining_rejects_string_input() -> None:
    with pytest.raises(ProcessMiningError):
        ProcessMiner().mine("invalid")


def test_process_mining_rejects_non_iterable_input() -> None:
    with pytest.raises(ProcessMiningError):
        ProcessMiner().mine(None)


def test_process_mining_rejects_invalid_trace() -> None:
    with pytest.raises(ProcessMiningError):
        ProcessMiner().mine(
            (
                "not-a-process-trace",
            )
        )


# =============================================================================
# Result Dataset
# =============================================================================


def test_process_mining_result_contains_dataset() -> None:
    trace = _trace(
        "case-001",
        (
            "receive",
            "approve",
            "complete",
        ),
    )

    result = ProcessMiner().mine((trace,))

    assert result.dataset.case_count == 1
    assert result.dataset.event_count == 3
    assert result.dataset.metrics == result.metrics
    assert (
        result.dataset.activity_observations
        == result.activity_observations
    )
    assert (
        result.dataset.transition_observations
        == result.transition_observations
    )


# =============================================================================
# Determinism
# =============================================================================


def test_process_mining_is_deterministic() -> None:
    traces = (
        _trace(
            "case-001",
            (
                "receive",
                "approve",
                "complete",
            ),
        ),
        _trace(
            "case-002",
            (
                "receive",
                "reject",
            ),
        ),
    )

    first = ProcessMiner().mine(traces)
    second = ProcessMiner().mine(traces)

    assert first == second


# =============================================================================
# Immutability
# =============================================================================


def test_process_variant_is_immutable() -> None:
    variant = ProcessVariant(
        activities=("receive",),
        occurrence_count=1,
    )

    with pytest.raises(AttributeError):
        variant.occurrence_count = 2  # type: ignore[misc]


# =============================================================================
# Public Module Exports
# =============================================================================


def test_process_mining_module_exports_are_available() -> None:
    import src.process_intelligence.process_mining as process_mining

    assert set(process_mining.__all__) == {
        "ProcessMiningError",
        "ProcessVariant",
        "ProcessMiningResult",
        "ProcessMiner",
        "mine_process",
    }


# =============================================================================
# Validation Edge Cases
# =============================================================================


def test_process_variant_rejects_non_tuple_activities() -> None:
    with pytest.raises(ProcessMiningError):
        ProcessVariant(
            activities=["receive", "approve"],  # type: ignore[arg-type]
            occurrence_count=1,
        )


def test_process_variant_rejects_non_integer_occurrence_count() -> None:
    with pytest.raises(ProcessMiningError):
        ProcessVariant(
            activities=("receive", "approve"),
            occurrence_count="1",  # type: ignore[arg-type]
        )