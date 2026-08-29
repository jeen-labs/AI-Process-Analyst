"""
Tests for Phase 5.8 - Digital Twin Foundation.
"""

import pytest

from src.process_intelligence.process_digital_twin import (
    DigitalTwinState,
    DigitalTwinTransition,
    ProcessDigitalTwin,
    ProcessDigitalTwinError,
    ProcessDigitalTwinSnapshot,
    build_digital_twin,
)


# =============================================================================
# DigitalTwinState
# =============================================================================


def test_digital_twin_state_is_immutable():
    state = DigitalTwinState(
        state_name="Approved",
        observation_count=10,
        active=True,
    )

    with pytest.raises(AttributeError):
        state.observation_count = 20


def test_digital_twin_state_to_dict():
    state = DigitalTwinState(
        state_name="Approved",
        observation_count=10,
        active=True,
    )

    assert state.to_dict() == {
        "state_name": "Approved",
        "observation_count": 10,
        "active": True,
    }


@pytest.mark.parametrize(
    "kwargs",
    [
        {
            "state_name": "",
            "observation_count": 10,
        },
        {
            "state_name": "Approved",
            "observation_count": -1,
        },
        {
            "state_name": "Approved",
            "observation_count": 10,
            "active": "yes",
        },
    ],
)
def test_digital_twin_state_rejects_invalid_values(kwargs):
    with pytest.raises(ProcessDigitalTwinError):
        DigitalTwinState(**kwargs)


def test_digital_twin_state_strips_name():
    state = DigitalTwinState(
        state_name="  Approved  ",
        observation_count=5,
    )

    assert state.state_name == "Approved"


# =============================================================================
# DigitalTwinTransition
# =============================================================================


def test_digital_twin_transition_is_immutable():
    transition = DigitalTwinTransition(
        source_state="Submitted",
        target_state="Approved",
        occurrence_count=7,
    )

    with pytest.raises(AttributeError):
        transition.occurrence_count = 10


def test_digital_twin_transition_to_dict():
    transition = DigitalTwinTransition(
        source_state="Submitted",
        target_state="Approved",
        occurrence_count=7,
    )

    assert transition.to_dict() == {
        "source_state": "Submitted",
        "target_state": "Approved",
        "occurrence_count": 7,
    }


@pytest.mark.parametrize(
    "kwargs",
    [
        {
            "source_state": "",
            "target_state": "Approved",
            "occurrence_count": 1,
        },
        {
            "source_state": "Submitted",
            "target_state": "",
            "occurrence_count": 1,
        },
        {
            "source_state": "Submitted",
            "target_state": "Approved",
            "occurrence_count": -1,
        },
    ],
)
def test_digital_twin_transition_rejects_invalid_values(kwargs):
    with pytest.raises(ProcessDigitalTwinError):
        DigitalTwinTransition(**kwargs)


def test_digital_twin_transition_strips_state_names():
    transition = DigitalTwinTransition(
        source_state="  Submitted  ",
        target_state="  Approved  ",
        occurrence_count=3,
    )

    assert transition.source_state == "Submitted"
    assert transition.target_state == "Approved"


# =============================================================================
# ProcessDigitalTwinSnapshot
# =============================================================================


def _sample_states():
    return (
        DigitalTwinState(
            state_name="Submitted",
            observation_count=20,
            active=False,
        ),
        DigitalTwinState(
            state_name="Approved",
            observation_count=15,
            active=True,
        ),
        DigitalTwinState(
            state_name="Completed",
            observation_count=10,
            active=False,
        ),
    )


def _sample_transitions():
    return (
        DigitalTwinTransition(
            source_state="Submitted",
            target_state="Approved",
            occurrence_count=15,
        ),
        DigitalTwinTransition(
            source_state="Approved",
            target_state="Completed",
            occurrence_count=10,
        ),
    )


def test_snapshot_is_immutable():
    snapshot = ProcessDigitalTwinSnapshot(
        process_name="Purchase-to-Pay",
        states=_sample_states(),
        transitions=_sample_transitions(),
        total_observations=45,
        active_state_count=1,
        transition_count=2,
        total_transition_occurrences=25,
    )

    with pytest.raises(AttributeError):
        snapshot.process_name = "Other Process"


def test_snapshot_state_count():
    snapshot = ProcessDigitalTwinSnapshot(
        process_name="Purchase-to-Pay",
        states=_sample_states(),
        transitions=_sample_transitions(),
        total_observations=45,
        active_state_count=1,
        transition_count=2,
        total_transition_occurrences=25,
    )

    assert snapshot.state_count == 3


def test_snapshot_to_dict():
    snapshot = ProcessDigitalTwinSnapshot(
        process_name="Purchase-to-Pay",
        states=_sample_states(),
        transitions=_sample_transitions(),
        total_observations=45,
        active_state_count=1,
        transition_count=2,
        total_transition_occurrences=25,
    )

    result = snapshot.to_dict()

    assert result["process_name"] == "Purchase-to-Pay"
    assert result["state_count"] == 3
    assert result["total_observations"] == 45
    assert result["active_state_count"] == 1
    assert result["transition_count"] == 2
    assert result["total_transition_occurrences"] == 25
    assert len(result["states"]) == 3
    assert len(result["transitions"]) == 2


@pytest.mark.parametrize(
    "kwargs",
    [
        {
            "process_name": "",
            "states": (),
            "transitions": (),
            "total_observations": 0,
            "active_state_count": 0,
            "transition_count": 0,
            "total_transition_occurrences": 0,
        },
        {
            "process_name": "Process",
            "states": (),
            "transitions": (),
            "total_observations": -1,
            "active_state_count": 0,
            "transition_count": 0,
            "total_transition_occurrences": 0,
        },
    ],
)
def test_snapshot_rejects_invalid_values(kwargs):
    with pytest.raises(ProcessDigitalTwinError):
        ProcessDigitalTwinSnapshot(**kwargs)


# =============================================================================
# ProcessDigitalTwin
# =============================================================================


def test_build_snapshot():
    twin = ProcessDigitalTwin()

    snapshot = twin.build_snapshot(
        "Purchase-to-Pay",
        _sample_states(),
        _sample_transitions(),
    )

    assert isinstance(snapshot, ProcessDigitalTwinSnapshot)
    assert snapshot.process_name == "Purchase-to-Pay"
    assert snapshot.state_count == 3
    assert snapshot.total_observations == 45
    assert snapshot.active_state_count == 1
    assert snapshot.transition_count == 2
    assert snapshot.total_transition_occurrences == 25


def test_build_snapshot_accepts_generators():
    twin = ProcessDigitalTwin()

    states = (
        state
        for state in _sample_states()
    )

    transitions = (
        transition
        for transition in _sample_transitions()
    )

    snapshot = twin.build_snapshot(
        "Purchase-to-Pay",
        states,
        transitions,
    )

    assert snapshot.state_count == 3
    assert snapshot.transition_count == 2


def test_build_snapshot_is_deterministic():
    twin = ProcessDigitalTwin()

    first = twin.build_snapshot(
        "Purchase-to-Pay",
        _sample_states(),
        _sample_transitions(),
    )

    second = twin.build_snapshot(
        "Purchase-to-Pay",
        _sample_states(),
        _sample_transitions(),
    )

    assert first == second


def test_build_snapshot_preserves_state_order():
    twin = ProcessDigitalTwin()

    states = (
        DigitalTwinState("B", 2),
        DigitalTwinState("A", 3),
        DigitalTwinState("C", 4),
    )

    snapshot = twin.build_snapshot(
        "Test Process",
        states,
        (),
    )

    assert [
        state.state_name
        for state in snapshot.states
    ] == ["B", "A", "C"]


def test_build_snapshot_preserves_transition_order():
    twin = ProcessDigitalTwin()

    transitions = (
        DigitalTwinTransition("B", "C", 2),
        DigitalTwinTransition("A", "B", 3),
    )

    snapshot = twin.build_snapshot(
        "Test Process",
        (),
        transitions,
    )

    assert [
        (
            transition.source_state,
            transition.target_state,
        )
        for transition in snapshot.transitions
    ] == [
        ("B", "C"),
        ("A", "B"),
    ]


@pytest.mark.parametrize(
    "process_name",
    [
        "",
        "   ",
        None,
        123,
    ],
)
def test_build_snapshot_rejects_invalid_process_name(process_name):
    twin = ProcessDigitalTwin()

    with pytest.raises(ProcessDigitalTwinError):
        twin.build_snapshot(
            process_name,
            (),
            (),
        )


@pytest.mark.parametrize(
    "states",
    [
        "invalid",
        None,
        [DigitalTwinState("Valid", 1), "invalid"],
    ],
)
def test_build_snapshot_rejects_invalid_states(states):
    twin = ProcessDigitalTwin()

    with pytest.raises(ProcessDigitalTwinError):
        twin.build_snapshot(
            "Test Process",
            states,
            (),
        )


@pytest.mark.parametrize(
    "transitions",
    [
        "invalid",
        None,
        [
            DigitalTwinTransition(
                "A",
                "B",
                1,
            ),
            "invalid",
        ],
    ],
)
def test_build_snapshot_rejects_invalid_transitions(transitions):
    twin = ProcessDigitalTwin()

    with pytest.raises(ProcessDigitalTwinError):
        twin.build_snapshot(
            "Test Process",
            (),
            transitions,
        )


def test_build_snapshot_does_not_modify_source_state_collection():
    twin = ProcessDigitalTwin()

    source_states = [
        DigitalTwinState(
            state_name="Submitted",
            observation_count=10,
        ),
        DigitalTwinState(
            state_name="Approved",
            observation_count=5,
        ),
    ]

    original = list(source_states)

    snapshot = twin.build_snapshot(
        "Test Process",
        source_states,
        (),
    )

    assert source_states == original
    assert source_states is not snapshot.states


def test_build_snapshot_does_not_modify_source_transition_collection():
    twin = ProcessDigitalTwin()

    source_transitions = [
        DigitalTwinTransition(
            source_state="Submitted",
            target_state="Approved",
            occurrence_count=5,
        ),
    ]

    original = list(source_transitions)

    snapshot = twin.build_snapshot(
        "Test Process",
        (),
        source_transitions,
    )

    assert source_transitions == original
    assert source_transitions is not snapshot.transitions


def test_empty_process_can_be_represented():
    twin = ProcessDigitalTwin()

    snapshot = twin.build_snapshot(
        "Empty Process",
        (),
        (),
    )

    assert snapshot.state_count == 0
    assert snapshot.transition_count == 0
    assert snapshot.total_observations == 0
    assert snapshot.active_state_count == 0
    assert snapshot.total_transition_occurrences == 0


# =============================================================================
# Convenience API
# =============================================================================


def test_build_digital_twin_convenience_function():
    snapshot = build_digital_twin(
        "Purchase-to-Pay",
        _sample_states(),
        _sample_transitions(),
    )

    assert isinstance(snapshot, ProcessDigitalTwinSnapshot)
    assert snapshot.process_name == "Purchase-to-Pay"
    assert snapshot.total_observations == 45


# =============================================================================
# Validation Edge Cases
# =============================================================================


def test_digital_twin_state_rejects_non_integer_observation_count() -> None:
    with pytest.raises(ProcessDigitalTwinError):
        DigitalTwinState(
            state_name="Approved",
            observation_count="10",  # type: ignore[arg-type]
        )


def test_digital_twin_transition_rejects_non_integer_occurrence_count() -> None:
    with pytest.raises(ProcessDigitalTwinError):
        DigitalTwinTransition(
            source_state="Submitted",
            target_state="Approved",
            occurrence_count="10",  # type: ignore[arg-type]
        )


def test_snapshot_rejects_non_integer_total_observations() -> None:
    with pytest.raises(ProcessDigitalTwinError):
        ProcessDigitalTwinSnapshot(
            process_name="Purchase-to-Pay",
            states=(),
            transitions=(),
            total_observations="45",  # type: ignore[arg-type]
            active_state_count=0,
            transition_count=0,
            total_transition_occurrences=0,
        )