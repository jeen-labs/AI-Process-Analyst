"""
===============================================================================
AI Process Analyst
===============================================================================

Module:
    process_intelligence.process_digital_twin

Purpose:
    Provide a deterministic digital-twin foundation for Process Intelligence.

Milestone:
    Milestone 5 - Process Intelligence

Phase:
    Phase 5.8 - Digital Twin Foundation

Responsibilities:
    - Validate digital-twin inputs.
    - Represent process state.
    - Represent process transitions.
    - Build deterministic digital-twin snapshots.
    - Calculate state metrics.
    - Preserve source-data immutability.
    - Avoid autonomous execution.

This module intentionally provides a deterministic representation layer.
It does not execute processes, modify source process data, invoke an LLM,
perform optimization, or make autonomous operational decisions.
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


# =============================================================================
# Errors
# =============================================================================


class ProcessDigitalTwinError(ValueError):
    """
    Raised when a digital-twin operation cannot be completed.
    """


# =============================================================================
# Process State
# =============================================================================


@dataclass(frozen=True)
class DigitalTwinState:
    """
    Represent one state in the digital twin.

    Attributes:
        state_name:
            Name of the process state.

        observation_count:
            Number of observations represented by the state.

        active:
            Whether the state is currently active in the snapshot.
    """

    state_name: str
    observation_count: int
    active: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.state_name, str) or not self.state_name.strip():
            raise ProcessDigitalTwinError(
                "state_name must be a non-empty string."
            )

        if not isinstance(self.observation_count, int):
            raise ProcessDigitalTwinError(
                "observation_count must be an integer."
            )

        if self.observation_count < 0:
            raise ProcessDigitalTwinError(
                "observation_count must not be negative."
            )

        if not isinstance(self.active, bool):
            raise ProcessDigitalTwinError(
                "active must be a boolean."
            )

        object.__setattr__(
            self,
            "state_name",
            self.state_name.strip(),
        )

    def to_dict(self) -> dict[str, object]:
        """
        Return a serializable representation of the state.
        """
        return {
            "state_name": self.state_name,
            "observation_count": self.observation_count,
            "active": self.active,
        }


# =============================================================================
# Process Transition
# =============================================================================


@dataclass(frozen=True)
class DigitalTwinTransition:
    """
    Represent one process transition in the digital twin.

    Attributes:
        source_state:
            State from which the transition originates.

        target_state:
            State to which the transition leads.

        occurrence_count:
            Number of observed occurrences of the transition.
    """

    source_state: str
    target_state: str
    occurrence_count: int

    def __post_init__(self) -> None:
        if (
            not isinstance(self.source_state, str)
            or not self.source_state.strip()
        ):
            raise ProcessDigitalTwinError(
                "source_state must be a non-empty string."
            )

        if (
            not isinstance(self.target_state, str)
            or not self.target_state.strip()
        ):
            raise ProcessDigitalTwinError(
                "target_state must be a non-empty string."
            )

        if not isinstance(self.occurrence_count, int):
            raise ProcessDigitalTwinError(
                "occurrence_count must be an integer."
            )

        if self.occurrence_count < 0:
            raise ProcessDigitalTwinError(
                "occurrence_count must not be negative."
            )

        object.__setattr__(
            self,
            "source_state",
            self.source_state.strip(),
        )

        object.__setattr__(
            self,
            "target_state",
            self.target_state.strip(),
        )

    def to_dict(self) -> dict[str, object]:
        """
        Return a serializable representation of the transition.
        """
        return {
            "source_state": self.source_state,
            "target_state": self.target_state,
            "occurrence_count": self.occurrence_count,
        }


# =============================================================================
# Digital Twin Snapshot
# =============================================================================


@dataclass(frozen=True)
class ProcessDigitalTwinSnapshot:
    """
    Represent a deterministic snapshot of a process digital twin.

    The snapshot is immutable and contains copied state and transition
    representations rather than references to mutable source collections.
    """

    process_name: str
    states: tuple[DigitalTwinState, ...]
    transitions: tuple[DigitalTwinTransition, ...]
    total_observations: int
    active_state_count: int
    transition_count: int
    total_transition_occurrences: int

    def __post_init__(self) -> None:
        if (
            not isinstance(self.process_name, str)
            or not self.process_name.strip()
        ):
            raise ProcessDigitalTwinError(
                "process_name must be a non-empty string."
            )

        if not isinstance(self.states, tuple):
            raise ProcessDigitalTwinError(
                "states must be a tuple of DigitalTwinState objects."
            )

        if not isinstance(self.transitions, tuple):
            raise ProcessDigitalTwinError(
                "transitions must be a tuple of DigitalTwinTransition objects."
            )

        for state in self.states:
            if not isinstance(state, DigitalTwinState):
                raise ProcessDigitalTwinError(
                    "states must contain only DigitalTwinState objects."
                )

        for transition in self.transitions:
            if not isinstance(transition, DigitalTwinTransition):
                raise ProcessDigitalTwinError(
                    "transitions must contain only DigitalTwinTransition "
                    "objects."
                )

        for field_name in (
            "total_observations",
            "active_state_count",
            "transition_count",
            "total_transition_occurrences",
        ):
            value = getattr(self, field_name)

            if not isinstance(value, int):
                raise ProcessDigitalTwinError(
                    f"{field_name} must be an integer."
                )

            if value < 0:
                raise ProcessDigitalTwinError(
                    f"{field_name} must not be negative."
                )

        object.__setattr__(
            self,
            "process_name",
            self.process_name.strip(),
        )

    @property
    def state_count(self) -> int:
        """
        Return the number of represented states.
        """
        return len(self.states)

    def to_dict(self) -> dict[str, object]:
        """
        Return a serializable representation of the snapshot.
        """
        return {
            "process_name": self.process_name,
            "states": [
                state.to_dict()
                for state in self.states
            ],
            "transitions": [
                transition.to_dict()
                for transition in self.transitions
            ],
            "total_observations": self.total_observations,
            "active_state_count": self.active_state_count,
            "transition_count": self.transition_count,
            "total_transition_occurrences": (
                self.total_transition_occurrences
            ),
            "state_count": self.state_count,
        }


# =============================================================================
# Digital Twin Builder
# =============================================================================


class ProcessDigitalTwin:
    """
    Build deterministic digital-twin snapshots.

    The class represents observed process structure only.

    It does not:
        - execute transitions,
        - alter source observations,
        - invoke optimization,
        - invoke an LLM,
        - make autonomous decisions.
    """

    def build_snapshot(
        self,
        process_name: str,
        states: Iterable[DigitalTwinState],
        transitions: Iterable[DigitalTwinTransition],
    ) -> ProcessDigitalTwinSnapshot:
        """
        Build a deterministic digital-twin snapshot.
        """
        self._validate_process_name(process_name)

        validated_states = self._validate_states(states)
        validated_transitions = self._validate_transitions(transitions)

        total_observations = sum(
            state.observation_count
            for state in validated_states
        )

        active_state_count = sum(
            1
            for state in validated_states
            if state.active
        )

        transition_count = len(validated_transitions)

        total_transition_occurrences = sum(
            transition.occurrence_count
            for transition in validated_transitions
        )

        return ProcessDigitalTwinSnapshot(
            process_name=process_name.strip(),
            states=validated_states,
            transitions=validated_transitions,
            total_observations=total_observations,
            active_state_count=active_state_count,
            transition_count=transition_count,
            total_transition_occurrences=(
                total_transition_occurrences
            ),
        )

    @staticmethod
    def _validate_process_name(process_name: str) -> None:
        if (
            not isinstance(process_name, str)
            or not process_name.strip()
        ):
            raise ProcessDigitalTwinError(
                "process_name must be a non-empty string."
            )

    @staticmethod
    def _validate_states(
        states: Iterable[DigitalTwinState],
    ) -> tuple[DigitalTwinState, ...]:
        if isinstance(states, (str, bytes)):
            raise ProcessDigitalTwinError(
                "states must be an iterable of DigitalTwinState objects."
            )

        try:
            materialized = tuple(states)
        except TypeError as exc:
            raise ProcessDigitalTwinError(
                "states must be an iterable of DigitalTwinState objects."
            ) from exc

        for state in materialized:
            if not isinstance(state, DigitalTwinState):
                raise ProcessDigitalTwinError(
                    "states must contain only DigitalTwinState objects."
                )

        return tuple(
            DigitalTwinState(
                state_name=state.state_name,
                observation_count=state.observation_count,
                active=state.active,
            )
            for state in materialized
        )

    @staticmethod
    def _validate_transitions(
        transitions: Iterable[DigitalTwinTransition],
    ) -> tuple[DigitalTwinTransition, ...]:
        if isinstance(transitions, (str, bytes)):
            raise ProcessDigitalTwinError(
                "transitions must be an iterable of "
                "DigitalTwinTransition objects."
            )

        try:
            materialized = tuple(transitions)
        except TypeError as exc:
            raise ProcessDigitalTwinError(
                "transitions must be an iterable of "
                "DigitalTwinTransition objects."
            ) from exc

        for transition in materialized:
            if not isinstance(
                transition,
                DigitalTwinTransition,
            ):
                raise ProcessDigitalTwinError(
                    "transitions must contain only "
                    "DigitalTwinTransition objects."
                )

        return tuple(
            DigitalTwinTransition(
                source_state=transition.source_state,
                target_state=transition.target_state,
                occurrence_count=transition.occurrence_count,
            )
            for transition in materialized
        )


# =============================================================================
# Convenience API
# =============================================================================


def build_digital_twin(
    process_name: str,
    states: Iterable[DigitalTwinState],
    transitions: Iterable[DigitalTwinTransition],
) -> ProcessDigitalTwinSnapshot:
    """
    Convenience function for building a deterministic digital-twin snapshot.
    """
    return ProcessDigitalTwin().build_snapshot(
        process_name,
        states,
        transitions,
    )


# =============================================================================
# Public Module API
# =============================================================================


__all__ = [
    "ProcessDigitalTwinError",
    "DigitalTwinState",
    "DigitalTwinTransition",
    "ProcessDigitalTwinSnapshot",
    "ProcessDigitalTwin",
    "build_digital_twin",
]