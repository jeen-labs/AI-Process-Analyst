"""
Tests:
    Process Discovery

Phase:
    Milestone 5 - Process Intelligence
    Phase 5.3 - Process Discovery
"""

from datetime import datetime, timezone

import pytest

from src.process_intelligence.process_discovery import (
    DiscoveredProcessModel,
    DiscoveredTransition,
    ProcessDiscoverer,
    ProcessDiscoveryError,
    ProcessDiscoveryResult,
)
from src.process_intelligence.process_intelligence_models import (
    ProcessEvent,
    ProcessTrace,
)


def _event(
    case_id: str,
    activity: str,
    minute: int,
) -> ProcessEvent:
    return ProcessEvent(
        case_id=case_id,
        activity=activity,
        timestamp=datetime(
            2026,
            8,
            27,
            10,
            minute,
            tzinfo=timezone.utc,
        ),
    )


def _trace(
    case_id: str,
    activities: tuple[str, ...],
) -> ProcessTrace:
    return ProcessTrace(
        case_id=case_id,
        events=tuple(
            _event(
                case_id,
                activity,
                index,
            )
            for index, activity in enumerate(activities)
        ),
    )


# =============================================================================
# Discovered Transition
# =============================================================================


def test_discovered_transition_can_be_created() -> None:
    transition = DiscoveredTransition(
        source_activity="receive",
        target_activity="approve",
        occurrence_count=3,
    )

    assert transition.source_activity == "receive"
    assert transition.target_activity == "approve"
    assert transition.occurrence_count == 3


def test_discovered_transition_rejects_empty_source() -> None:
    with pytest.raises(ProcessDiscoveryError):
        DiscoveredTransition(
            source_activity="",
            target_activity="approve",
            occurrence_count=1,
        )


def test_discovered_transition_rejects_empty_target() -> None:
    with pytest.raises(ProcessDiscoveryError):
        DiscoveredTransition(
            source_activity="receive",
            target_activity="",
            occurrence_count=1,
        )


def test_discovered_transition_rejects_negative_count() -> None:
    with pytest.raises(ProcessDiscoveryError):
        DiscoveredTransition(
            source_activity="receive",
            target_activity="approve",
            occurrence_count=-1,
        )


# =============================================================================
# Discovered Process Model
# =============================================================================


def test_discovered_process_model_can_be_created() -> None:
    transition = DiscoveredTransition(
        source_activity="receive",
        target_activity="approve",
        occurrence_count=2,
    )

    model = DiscoveredProcessModel(
        activities=(
            "approve",
            "receive",
        ),
        transitions=(transition,),
        start_activities=("receive",),
        end_activities=("approve",),
        activity_frequencies=(
            ("approve", 2),
            ("receive", 2),
        ),
        case_count=2,
    )

    assert model.activity_count == 2
    assert model.transition_count == 1
    assert model.case_count == 2


def test_discovered_process_model_frequency_lookup() -> None:
    model = DiscoveredProcessModel(
        activities=("approve", "receive"),
        transitions=(),
        start_activities=("receive",),
        end_activities=("approve",),
        activity_frequencies=(
            ("approve", 3),
            ("receive", 4),
        ),
        case_count=4,
    )

    assert model.frequency_for_activity("receive") == 4
    assert model.frequency_for_activity("missing") == 0


def test_discovered_process_model_rejects_negative_case_count() -> None:
    with pytest.raises(ProcessDiscoveryError):
        DiscoveredProcessModel(
            activities=(),
            transitions=(),
            start_activities=(),
            end_activities=(),
            activity_frequencies=(),
            case_count=-1,
        )


# =============================================================================
# Process Discovery Result
# =============================================================================


def test_process_discovery_result_can_be_created() -> None:
    model = DiscoveredProcessModel(
        activities=("receive",),
        transitions=(),
        start_activities=("receive",),
        end_activities=("receive",),
        activity_frequencies=(("receive", 1),),
        case_count=1,
    )

    result = ProcessDiscoveryResult(
        model=model,
        source_case_count=1,
    )

    assert result.model == model
    assert result.source_case_count == 1


# =============================================================================
# Process Discoverer
# =============================================================================


def test_process_discovery_discovers_activities() -> None:
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

    result = ProcessDiscoverer().discover(traces)

    assert result.model.activities == (
        "approve",
        "complete",
        "receive",
    )


def test_process_discovery_discovers_transitions() -> None:
    traces = (
        _trace(
            "case-001",
            ("receive", "approve", "complete"),
        ),
    )

    result = ProcessDiscoverer().discover(traces)

    assert result.model.transitions == (
        DiscoveredTransition(
            source_activity="approve",
            target_activity="complete",
            occurrence_count=1,
        ),
        DiscoveredTransition(
            source_activity="receive",
            target_activity="approve",
            occurrence_count=1,
        ),
    )


def test_process_discovery_counts_transition_frequency() -> None:
    traces = (
        _trace(
            "case-001",
            ("receive", "approve", "complete"),
        ),
        _trace(
            "case-002",
            ("receive", "approve", "complete"),
        ),
        _trace(
            "case-003",
            ("receive", "reject"),
        ),
    )

    result = ProcessDiscoverer().discover(traces)

    transitions = {
        (
            transition.source_activity,
            transition.target_activity,
        ): transition.occurrence_count
        for transition in result.model.transitions
    }

    assert transitions[("receive", "approve")] == 2
    assert transitions[("approve", "complete")] == 2
    assert transitions[("receive", "reject")] == 1


def test_process_discovery_identifies_start_activities() -> None:
    traces = (
        _trace(
            "case-001",
            ("receive", "approve", "complete"),
        ),
        _trace(
            "case-002",
            ("receive", "reject"),
        ),
        _trace(
            "case-003",
            ("manual_receive", "approve"),
        ),
    )

    result = ProcessDiscoverer().discover(traces)

    assert result.model.start_activities == (
        "manual_receive",
        "receive",
    )


def test_process_discovery_identifies_end_activities() -> None:
    traces = (
        _trace(
            "case-001",
            ("receive", "approve", "complete"),
        ),
        _trace(
            "case-002",
            ("receive", "reject"),
        ),
        _trace(
            "case-003",
            ("receive", "approve"),
        ),
    )

    result = ProcessDiscoverer().discover(traces)

    assert result.model.end_activities == (
        "approve",
        "complete",
        "reject",
    )


def test_process_discovery_counts_activity_frequency_by_case() -> None:
    traces = (
        _trace(
            "case-001",
            ("receive", "approve", "approve", "complete"),
        ),
        _trace(
            "case-002",
            ("receive", "approve", "complete"),
        ),
        _trace(
            "case-003",
            ("receive", "reject"),
        ),
    )

    result = ProcessDiscoverer().discover(traces)

    assert result.model.frequency_for_activity("receive") == 3
    assert result.model.frequency_for_activity("approve") == 2
    assert result.model.frequency_for_activity("complete") == 2
    assert result.model.frequency_for_activity("reject") == 1


def test_process_discovery_handles_empty_trace() -> None:
    result = ProcessDiscoverer().discover(
        (
            _trace("case-001", ()),
        )
    )

    assert result.model.activities == ()
    assert result.model.transitions == ()
    assert result.model.start_activities == ()
    assert result.model.end_activities == ()
    assert result.model.case_count == 1


def test_process_discovery_handles_empty_input() -> None:
    result = ProcessDiscoverer().discover(())

    assert result.model.activities == ()
    assert result.model.transitions == ()
    assert result.model.case_count == 0
    assert result.source_case_count == 0


def test_process_discovery_rejects_invalid_trace() -> None:
    with pytest.raises(ProcessDiscoveryError):
        ProcessDiscoverer().discover(
            ("invalid",),
        )


def test_process_discovery_rejects_none() -> None:
    with pytest.raises(ProcessDiscoveryError):
        ProcessDiscoverer().discover(None)


def test_process_discovery_result_is_immutable() -> None:
    result = ProcessDiscoverer().discover(
        (
            _trace(
                "case-001",
                ("receive", "complete"),
            ),
        )
    )

    with pytest.raises(AttributeError):
        result.source_case_count = 99


# =============================================================================
# Public API
# =============================================================================


def test_process_discovery_public_exports_are_available() -> None:
    import src.process_intelligence.process_discovery as process_discovery

    expected = {
        "ProcessDiscoveryError",
        "DiscoveredTransition",
        "DiscoveredProcessModel",
        "ProcessDiscoveryResult",
        "ProcessDiscoverer",
    }

    assert set(process_discovery.__all__) == expected