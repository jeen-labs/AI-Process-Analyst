"""
Tests for the Process Intelligence data model contracts.
"""

from datetime import datetime, timedelta, timezone

import pytest

from src.process_intelligence.process_intelligence_models import (
    ActivityObservation,
    ProcessEvent,
    ProcessIntelligenceDataset,
    ProcessIntelligenceMetrics,
    ProcessIntelligenceModelError,
    ProcessTrace,
    TransitionObservation,
)


def _timestamp(offset_seconds: int = 0) -> datetime:
    return datetime(
        2026,
        8,
        27,
        10,
        0,
        tzinfo=timezone.utc,
    ) + timedelta(seconds=offset_seconds)


# =============================================================================
# Process Event
# =============================================================================


def test_process_event_can_be_created() -> None:
    event = ProcessEvent(
        case_id="case-001",
        activity="receive_order",
        timestamp=_timestamp(),
        resource="operator-1",
        attributes={
            "channel": "online",
        },
    )

    assert event.case_id == "case-001"
    assert event.activity == "receive_order"
    assert event.resource == "operator-1"
    assert event.attributes["channel"] == "online"


def test_process_event_requires_case_id() -> None:
    with pytest.raises(ProcessIntelligenceModelError):
        ProcessEvent(
            case_id="",
            activity="receive_order",
            timestamp=_timestamp(),
        )


def test_process_event_requires_activity() -> None:
    with pytest.raises(ProcessIntelligenceModelError):
        ProcessEvent(
            case_id="case-001",
            activity="",
            timestamp=_timestamp(),
        )


def test_process_event_requires_datetime() -> None:
    with pytest.raises(ProcessIntelligenceModelError):
        ProcessEvent(
            case_id="case-001",
            activity="receive_order",
            timestamp="2026-08-27",
        )


# =============================================================================
# Process Trace
# =============================================================================


def test_process_trace_accepts_ordered_events() -> None:
    events = (
        ProcessEvent(
            case_id="case-001",
            activity="receive_order",
            timestamp=_timestamp(0),
        ),
        ProcessEvent(
            case_id="case-001",
            activity="approve_order",
            timestamp=_timestamp(60),
        ),
    )

    trace = ProcessTrace(
        case_id="case-001",
        events=events,
    )

    assert trace.case_id == "case-001"
    assert len(trace.events) == 2


def test_process_trace_rejects_wrong_case_id() -> None:
    events = (
        ProcessEvent(
            case_id="case-002",
            activity="receive_order",
            timestamp=_timestamp(),
        ),
    )

    with pytest.raises(ProcessIntelligenceModelError):
        ProcessTrace(
            case_id="case-001",
            events=events,
        )


def test_process_trace_rejects_unordered_events() -> None:
    events = (
        ProcessEvent(
            case_id="case-001",
            activity="approve_order",
            timestamp=_timestamp(60),
        ),
        ProcessEvent(
            case_id="case-001",
            activity="receive_order",
            timestamp=_timestamp(0),
        ),
    )

    with pytest.raises(ProcessIntelligenceModelError):
        ProcessTrace(
            case_id="case-001",
            events=events,
        )


# =============================================================================
# Activity Observation
# =============================================================================


def test_activity_observation_calculates_average_duration() -> None:
    observation = ActivityObservation(
        activity="approve_order",
        occurrence_count=4,
        total_duration_seconds=200,
    )

    assert observation.average_duration_seconds == 50


def test_zero_occurrence_activity_has_zero_average_duration() -> None:
    observation = ActivityObservation(
        activity="approve_order",
        occurrence_count=0,
        total_duration_seconds=0,
    )

    assert observation.average_duration_seconds == 0.0


def test_activity_observation_rejects_negative_count() -> None:
    with pytest.raises(ProcessIntelligenceModelError):
        ActivityObservation(
            activity="approve_order",
            occurrence_count=-1,
        )


def test_activity_observation_rejects_negative_duration() -> None:
    with pytest.raises(ProcessIntelligenceModelError):
        ActivityObservation(
            activity="approve_order",
            occurrence_count=1,
            total_duration_seconds=-1,
        )


# =============================================================================
# Transition Observation
# =============================================================================


def test_transition_observation_can_be_created() -> None:
    observation = TransitionObservation(
        source_activity="receive_order",
        target_activity="approve_order",
        occurrence_count=12,
    )

    assert observation.source_activity == "receive_order"
    assert observation.target_activity == "approve_order"
    assert observation.occurrence_count == 12


def test_transition_observation_rejects_negative_count() -> None:
    with pytest.raises(ProcessIntelligenceModelError):
        TransitionObservation(
            source_activity="receive_order",
            target_activity="approve_order",
            occurrence_count=-1,
        )


# =============================================================================
# Process Intelligence Metrics
# =============================================================================


def test_metrics_can_be_created() -> None:
    metrics = ProcessIntelligenceMetrics(
        case_count=10,
        event_count=40,
        activity_count=6,
        transition_count=8,
        average_case_duration_seconds=7200,
        throughput_per_day=5,
        custom_metrics={
            "rework_rate": 0.12,
        },
    )

    assert metrics.case_count == 10
    assert metrics.event_count == 40
    assert metrics.custom_metrics["rework_rate"] == 0.12


def test_metrics_reject_negative_counts() -> None:
    with pytest.raises(ProcessIntelligenceModelError):
        ProcessIntelligenceMetrics(
            case_count=-1,
        )


def test_metrics_reject_negative_duration() -> None:
    with pytest.raises(ProcessIntelligenceModelError):
        ProcessIntelligenceMetrics(
            average_case_duration_seconds=-1,
        )


def test_metrics_reject_non_numeric_custom_metric() -> None:
    with pytest.raises(ProcessIntelligenceModelError):
        ProcessIntelligenceMetrics(
            custom_metrics={
                "rework_rate": "high",
            },
        )


# =============================================================================
# Process Intelligence Dataset
# =============================================================================


def test_dataset_counts_cases() -> None:
    trace_one = ProcessTrace(
        case_id="case-001",
        events=(
            ProcessEvent(
                case_id="case-001",
                activity="receive",
                timestamp=_timestamp(),
            ),
        ),
    )

    trace_two = ProcessTrace(
        case_id="case-002",
        events=(
            ProcessEvent(
                case_id="case-002",
                activity="receive",
                timestamp=_timestamp(),
            ),
        ),
    )

    dataset = ProcessIntelligenceDataset(
        traces=(
            trace_one,
            trace_two,
        ),
    )

    assert dataset.case_count == 2


def test_dataset_counts_events() -> None:
    trace = ProcessTrace(
        case_id="case-001",
        events=(
            ProcessEvent(
                case_id="case-001",
                activity="receive",
                timestamp=_timestamp(0),
            ),
            ProcessEvent(
                case_id="case-001",
                activity="approve",
                timestamp=_timestamp(60),
            ),
            ProcessEvent(
                case_id="case-001",
                activity="complete",
                timestamp=_timestamp(120),
            ),
        ),
    )

    dataset = ProcessIntelligenceDataset(
        traces=(trace,),
    )

    assert dataset.event_count == 3


def test_dataset_accepts_observations_and_metrics() -> None:
    trace = ProcessTrace(
        case_id="case-001",
        events=(
            ProcessEvent(
                case_id="case-001",
                activity="receive",
                timestamp=_timestamp(),
            ),
        ),
    )

    dataset = ProcessIntelligenceDataset(
        traces=(trace,),
        activity_observations=(
            ActivityObservation(
                activity="receive",
                occurrence_count=1,
            ),
        ),
        transition_observations=(
            TransitionObservation(
                source_activity="receive",
                target_activity="complete",
                occurrence_count=1,
            ),
        ),
        metrics=ProcessIntelligenceMetrics(
            case_count=1,
            event_count=1,
        ),
    )

    assert len(dataset.activity_observations) == 1
    assert len(dataset.transition_observations) == 1
    assert dataset.metrics is not None


def test_dataset_rejects_invalid_trace() -> None:
    with pytest.raises(ProcessIntelligenceModelError):
        ProcessIntelligenceDataset(
            traces=("not-a-trace",),
        )


def test_dataset_rejects_invalid_activity_observation() -> None:
    with pytest.raises(ProcessIntelligenceModelError):
        ProcessIntelligenceDataset(
            traces=(),
            activity_observations=("invalid",),
        )


def test_dataset_rejects_invalid_transition_observation() -> None:
    with pytest.raises(ProcessIntelligenceModelError):
        ProcessIntelligenceDataset(
            traces=(),
            transition_observations=("invalid",),
        )


def test_dataset_rejects_invalid_metrics() -> None:
    with pytest.raises(ProcessIntelligenceModelError):
        ProcessIntelligenceDataset(
            traces=(),
            metrics="invalid",
        )


# =============================================================================
# Immutability
# =============================================================================


def test_models_are_immutable() -> None:
    event = ProcessEvent(
        case_id="case-001",
        activity="receive",
        timestamp=_timestamp(),
    )

    with pytest.raises(AttributeError):
        event.activity = "changed"


# =============================================================================
# Validation Edge Cases
# =============================================================================


def test_process_event_rejects_invalid_resource() -> None:
    with pytest.raises(ProcessIntelligenceModelError):
        ProcessEvent(
            case_id="case-001",
            activity="receive_order",
            timestamp=_timestamp(),
            resource="   ",
        )


def test_process_event_rejects_invalid_attributes() -> None:
    with pytest.raises(ProcessIntelligenceModelError):
        ProcessEvent(
            case_id="case-001",
            activity="receive_order",
            timestamp=_timestamp(),
            attributes="invalid",
        )