"""
===============================================================================
AI Process Analyst
===============================================================================

Module:
    process_intelligence.process_discovery

Purpose:
    Provide deterministic process-discovery capabilities for the
    Process Intelligence platform.

Phase:
    Milestone 5 - Process Intelligence
    Phase 5.3 - Process Discovery

Responsibilities:
    - Discover process activities from process traces.
    - Discover direct activity transitions.
    - Count transition frequencies.
    - Identify process start activities.
    - Identify process end activities.
    - Build a deterministic discovered process model.
    - Provide stable results for later conformance, simulation,
      optimization, and digital-twin phases.

This module intentionally focuses on process discovery.

It does NOT:
    - Perform conformance checking.
    - Perform process simulation.
    - Predict KPIs.
    - Optimize processes.
    - Build a digital twin.
    - Execute business rules.
    - Perform LLM inference.
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .process_intelligence_models import (
    ProcessTrace,
)


# =============================================================================
# Errors
# =============================================================================


class ProcessDiscoveryError(ValueError):
    """
    Raised when process discovery input or configuration is invalid.
    """


# =============================================================================
# Discovered Transition
# =============================================================================


@dataclass(frozen=True)
class DiscoveredTransition:
    """
    Represent a discovered directed transition between two activities.

    Parameters
    ----------
    source_activity:
        Activity from which the transition originates.

    target_activity:
        Activity to which the transition leads.

    occurrence_count:
        Number of observed traces containing this direct transition.
    """

    source_activity: str
    target_activity: str
    occurrence_count: int

    def __post_init__(self) -> None:
        if (
            not isinstance(self.source_activity, str)
            or not self.source_activity.strip()
        ):
            raise ProcessDiscoveryError(
                "source_activity must be a non-empty string."
            )

        if (
            not isinstance(self.target_activity, str)
            or not self.target_activity.strip()
        ):
            raise ProcessDiscoveryError(
                "target_activity must be a non-empty string."
            )

        if not isinstance(self.occurrence_count, int):
            raise ProcessDiscoveryError(
                "occurrence_count must be an integer."
            )

        if self.occurrence_count < 0:
            raise ProcessDiscoveryError(
                "occurrence_count must not be negative."
            )


# =============================================================================
# Discovered Process Model
# =============================================================================


@dataclass(frozen=True)
class DiscoveredProcessModel:
    """
    Represent the deterministic process model discovered from traces.

    Parameters
    ----------
    activities:
        Sorted tuple containing all discovered activities.

    transitions:
        Sorted tuple containing discovered directed transitions.

    start_activities:
        Sorted tuple containing activities observed as the first
        activity of a trace.

    end_activities:
        Sorted tuple containing activities observed as the final
        activity of a trace.

    activity_frequencies:
        Tuple of ``(activity, count)`` pairs representing the number
        of traces in which each activity occurred.

    case_count:
        Number of traces used for discovery.
    """

    activities: tuple[str, ...]
    transitions: tuple[DiscoveredTransition, ...]
    start_activities: tuple[str, ...]
    end_activities: tuple[str, ...]
    activity_frequencies: tuple[tuple[str, int], ...]
    case_count: int

    def __post_init__(self) -> None:
        if not isinstance(self.activities, tuple):
            raise ProcessDiscoveryError(
                "activities must be a tuple."
            )

        if not isinstance(self.transitions, tuple):
            raise ProcessDiscoveryError(
                "transitions must be a tuple."
            )

        if not isinstance(self.start_activities, tuple):
            raise ProcessDiscoveryError(
                "start_activities must be a tuple."
            )

        if not isinstance(self.end_activities, tuple):
            raise ProcessDiscoveryError(
                "end_activities must be a tuple."
            )

        if not isinstance(self.activity_frequencies, tuple):
            raise ProcessDiscoveryError(
                "activity_frequencies must be a tuple."
            )

        if not isinstance(self.case_count, int):
            raise ProcessDiscoveryError(
                "case_count must be an integer."
            )

        if self.case_count < 0:
            raise ProcessDiscoveryError(
                "case_count must not be negative."
            )

        for activity in self.activities:
            if (
                not isinstance(activity, str)
                or not activity.strip()
            ):
                raise ProcessDiscoveryError(
                    "activities must contain non-empty strings."
                )

        for transition in self.transitions:
            if not isinstance(
                transition,
                DiscoveredTransition,
            ):
                raise ProcessDiscoveryError(
                    "transitions must contain only "
                    "DiscoveredTransition objects."
                )

        for activity in self.start_activities:
            if (
                not isinstance(activity, str)
                or not activity.strip()
            ):
                raise ProcessDiscoveryError(
                    "start_activities must contain "
                    "non-empty strings."
                )

        for activity in self.end_activities:
            if (
                not isinstance(activity, str)
                or not activity.strip()
            ):
                raise ProcessDiscoveryError(
                    "end_activities must contain "
                    "non-empty strings."
                )

        for activity, count in self.activity_frequencies:
            if (
                not isinstance(activity, str)
                or not activity.strip()
            ):
                raise ProcessDiscoveryError(
                    "activity frequency names must be "
                    "non-empty strings."
                )

            if not isinstance(count, int):
                raise ProcessDiscoveryError(
                    "activity frequency counts must be integers."
                )

            if count < 0:
                raise ProcessDiscoveryError(
                    "activity frequency counts must not be negative."
                )

    @property
    def transition_count(self) -> int:
        """
        Return the number of distinct discovered transitions.
        """

        return len(self.transitions)

    @property
    def activity_count(self) -> int:
        """
        Return the number of distinct discovered activities.
        """

        return len(self.activities)

    def frequency_for_activity(
        self,
        activity: str,
    ) -> int:
        """
        Return the observed trace frequency for an activity.

        Unknown activities return zero.
        """

        for name, count in self.activity_frequencies:
            if name == activity:
                return count

        return 0


# =============================================================================
# Process Discovery Result
# =============================================================================


@dataclass(frozen=True)
class ProcessDiscoveryResult:
    """
    Represent the result of a process-discovery operation.

    Parameters
    ----------
    model:
        Discovered process model.

    source_case_count:
        Number of input traces used during discovery.
    """

    model: DiscoveredProcessModel
    source_case_count: int

    def __post_init__(self) -> None:
        if not isinstance(
            self.model,
            DiscoveredProcessModel,
        ):
            raise ProcessDiscoveryError(
                "model must be a DiscoveredProcessModel."
            )

        if not isinstance(self.source_case_count, int):
            raise ProcessDiscoveryError(
                "source_case_count must be an integer."
            )

        if self.source_case_count < 0:
            raise ProcessDiscoveryError(
                "source_case_count must not be negative."
            )


# =============================================================================
# Process Discoverer
# =============================================================================


class ProcessDiscoverer:
    """
    Discover a deterministic process model from process traces.

    The discoverer uses direct-follow relationships:

        Activity A -> Activity B

    whenever A is immediately followed by B within a trace.

    Transition counts represent the number of traces in which the
    direct transition is observed.

    Activity frequencies represent the number of traces in which an
    activity occurs at least once.
    """

    def discover(
        self,
        traces: Iterable[ProcessTrace],
    ) -> ProcessDiscoveryResult:
        """
        Discover a process model from process traces.
        """

        if traces is None:
            raise ProcessDiscoveryError(
                "traces must not be None."
            )

        trace_list = tuple(traces)

        for trace in trace_list:
            if not isinstance(trace, ProcessTrace):
                raise ProcessDiscoveryError(
                    "traces must contain only ProcessTrace objects."
                )

        activity_set: set[str] = set()
        start_activity_set: set[str] = set()
        end_activity_set: set[str] = set()

        activity_frequencies: dict[str, int] = {}
        transition_frequencies: dict[
            tuple[str, str],
            int,
        ] = {}

        for trace in trace_list:
            if not trace.events:
                continue

            activities_in_trace = [
                event.activity
                for event in trace.events
            ]

            unique_activities_in_trace = set(
                activities_in_trace
            )

            activity_set.update(
                unique_activities_in_trace
            )

            first_activity = activities_in_trace[0]
            last_activity = activities_in_trace[-1]

            start_activity_set.add(first_activity)
            end_activity_set.add(last_activity)

            for activity in unique_activities_in_trace:
                activity_frequencies[activity] = (
                    activity_frequencies.get(activity, 0)
                    + 1
                )

            for previous_event, current_event in zip(
                trace.events,
                trace.events[1:],
            ):
                transition = (
                    previous_event.activity,
                    current_event.activity,
                )

                transition_frequencies[transition] = (
                    transition_frequencies.get(
                        transition,
                        0,
                    )
                    + 1
                )

        transitions = tuple(
            DiscoveredTransition(
                source_activity=source,
                target_activity=target,
                occurrence_count=count,
            )
            for (source, target), count in sorted(
                transition_frequencies.items()
            )
        )

        model = DiscoveredProcessModel(
            activities=tuple(sorted(activity_set)),
            transitions=transitions,
            start_activities=tuple(
                sorted(start_activity_set)
            ),
            end_activities=tuple(
                sorted(end_activity_set)
            ),
            activity_frequencies=tuple(
                sorted(activity_frequencies.items())
            ),
            case_count=len(trace_list),
        )

        return ProcessDiscoveryResult(
            model=model,
            source_case_count=len(trace_list),
        )


# =============================================================================
# Public Exports
# =============================================================================


__all__ = [
    "ProcessDiscoveryError",
    "DiscoveredTransition",
    "DiscoveredProcessModel",
    "ProcessDiscoveryResult",
    "ProcessDiscoverer",
]