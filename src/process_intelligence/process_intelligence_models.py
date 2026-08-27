"""
===============================================================================
AI Process Analyst
===============================================================================

Module:
    process_intelligence.process_intelligence_models

Purpose:
    Define the stable data models used by the Process Intelligence platform.

Milestone:
    Milestone 5 - Process Intelligence

Phase:
    Phase 5.1 - Define Process Intelligence Data Models

Responsibilities:
    - Define process event records.
    - Define process traces.
    - Define process activity observations.
    - Define process transition observations.
    - Define process intelligence metrics.
    - Define the Process Intelligence dataset.
    - Provide deterministic, validated data contracts for later
      process-mining, simulation, prediction, optimization, and
      digital-twin phases.

This module intentionally contains data models only.

It does NOT:
    - Mine process models.
    - Perform process discovery.
    - Perform simulation.
    - Predict KPIs.
    - Optimize processes.
    - Build a digital twin.
    - Execute business rules.
    - Perform LLM inference.
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Mapping


# =============================================================================
# Errors
# =============================================================================


class ProcessIntelligenceModelError(ValueError):
    """
    Raised when a Process Intelligence model is invalid.
    """


# =============================================================================
# Validation Helpers
# =============================================================================


def _require_non_empty_string(
    value: Any,
    field_name: str,
) -> None:
    """
    Validate that a value is a non-empty string.
    """

    if not isinstance(value, str) or not value.strip():
        raise ProcessIntelligenceModelError(
            f"{field_name} must be a non-empty string."
        )


def _require_non_negative_integer(
    value: Any,
    field_name: str,
) -> None:
    """
    Validate that a value is a non-negative integer.
    """

    if isinstance(value, bool) or not isinstance(value, int):
        raise ProcessIntelligenceModelError(
            f"{field_name} must be an integer."
        )

    if value < 0:
        raise ProcessIntelligenceModelError(
            f"{field_name} must not be negative."
        )


def _require_non_negative_number(
    value: Any,
    field_name: str,
) -> None:
    """
    Validate that a value is a non-negative numeric value.
    """

    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ProcessIntelligenceModelError(
            f"{field_name} must be numeric."
        )

    if value < 0:
        raise ProcessIntelligenceModelError(
            f"{field_name} must not be negative."
        )


def _require_mapping(
    value: Any,
    field_name: str,
) -> None:
    """
    Validate that a value is a mapping.
    """

    if not isinstance(value, Mapping):
        raise ProcessIntelligenceModelError(
            f"{field_name} must be a mapping."
        )


# =============================================================================
# Process Event
# =============================================================================


@dataclass(frozen=True)
class ProcessEvent:
    """
    Represent one timestamped process event.

    Parameters
    ----------
    case_id:
        Identifier of the process instance/case.

    activity:
        Name of the activity represented by the event.

    timestamp:
        Timestamp at which the event occurred.

    resource:
        Optional resource responsible for the event.

    attributes:
        Optional additional event attributes.
    """

    case_id: str
    activity: str
    timestamp: datetime
    resource: str | None = None
    attributes: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _require_non_empty_string(
            self.case_id,
            "case_id",
        )

        _require_non_empty_string(
            self.activity,
            "activity",
        )

        if not isinstance(self.timestamp, datetime):
            raise ProcessIntelligenceModelError(
                "timestamp must be a datetime."
            )

        if self.resource is not None:
            _require_non_empty_string(
                self.resource,
                "resource",
            )

        _require_mapping(
            self.attributes,
            "attributes",
        )


# =============================================================================
# Process Trace
# =============================================================================


@dataclass(frozen=True)
class ProcessTrace:
    """
    Represent the ordered event history of one process case.
    """

    case_id: str
    events: tuple[ProcessEvent, ...]

    def __post_init__(self) -> None:
        _require_non_empty_string(
            self.case_id,
            "case_id",
        )

        if not isinstance(self.events, tuple):
            raise ProcessIntelligenceModelError(
                "events must be a tuple of ProcessEvent objects."
            )

        for event in self.events:
            if not isinstance(event, ProcessEvent):
                raise ProcessIntelligenceModelError(
                    "events must contain only ProcessEvent objects."
                )

            if event.case_id != self.case_id:
                raise ProcessIntelligenceModelError(
                    "all events must belong to the trace case_id."
                )

        for previous, current in zip(
            self.events,
            self.events[1:],
        ):
            if current.timestamp < previous.timestamp:
                raise ProcessIntelligenceModelError(
                    "events must be ordered by timestamp."
                )


# =============================================================================
# Activity Observation
# =============================================================================


@dataclass(frozen=True)
class ActivityObservation:
    """
    Represent aggregated observations for one process activity.
    """

    activity: str
    occurrence_count: int
    total_duration_seconds: float = 0.0
    attributes: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _require_non_empty_string(
            self.activity,
            "activity",
        )

        _require_non_negative_integer(
            self.occurrence_count,
            "occurrence_count",
        )

        _require_non_negative_number(
            self.total_duration_seconds,
            "total_duration_seconds",
        )

        _require_mapping(
            self.attributes,
            "attributes",
        )

    @property
    def average_duration_seconds(self) -> float:
        """
        Return the average observed duration.

        Returns:
            0.0 when occurrence_count is zero.
        """

        if self.occurrence_count == 0:
            return 0.0

        return (
            self.total_duration_seconds
            / self.occurrence_count
        )


# =============================================================================
# Transition Observation
# =============================================================================


@dataclass(frozen=True)
class TransitionObservation:
    """
    Represent an observed transition between two activities.
    """

    source_activity: str
    target_activity: str
    occurrence_count: int

    def __post_init__(self) -> None:
        _require_non_empty_string(
            self.source_activity,
            "source_activity",
        )

        _require_non_empty_string(
            self.target_activity,
            "target_activity",
        )

        _require_non_negative_integer(
            self.occurrence_count,
            "occurrence_count",
        )


# =============================================================================
# Process Intelligence Metrics
# =============================================================================


@dataclass(frozen=True)
class ProcessIntelligenceMetrics:
    """
    Represent high-level process intelligence measurements.

    Metrics are intentionally generic at this stage so that later
    mining, simulation, prediction, optimization, and digital-twin
    phases can extend them without changing the foundational model.
    """

    case_count: int = 0
    event_count: int = 0
    activity_count: int = 0
    transition_count: int = 0
    average_case_duration_seconds: float = 0.0
    throughput_per_day: float = 0.0
    custom_metrics: Mapping[str, float] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        _require_non_negative_integer(
            self.case_count,
            "case_count",
        )

        _require_non_negative_integer(
            self.event_count,
            "event_count",
        )

        _require_non_negative_integer(
            self.activity_count,
            "activity_count",
        )

        _require_non_negative_integer(
            self.transition_count,
            "transition_count",
        )

        _require_non_negative_number(
            self.average_case_duration_seconds,
            "average_case_duration_seconds",
        )

        _require_non_negative_number(
            self.throughput_per_day,
            "throughput_per_day",
        )

        _require_mapping(
            self.custom_metrics,
            "custom_metrics",
        )

        for name, value in self.custom_metrics.items():
            _require_non_empty_string(
                name,
                "custom metric name",
            )

            if isinstance(value, bool) or not isinstance(
                value,
                (int, float),
            ):
                raise ProcessIntelligenceModelError(
                    "custom metric values must be numeric."
                )


# =============================================================================
# Process Intelligence Dataset
# =============================================================================


@dataclass(frozen=True)
class ProcessIntelligenceDataset:
    """
    Represent a complete Process Intelligence observation dataset.
    """

    traces: tuple[ProcessTrace, ...]
    activity_observations: tuple[
        ActivityObservation,
        ...
    ] = ()
    transition_observations: tuple[
        TransitionObservation,
        ...
    ] = ()
    metrics: ProcessIntelligenceMetrics | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.traces, tuple):
            raise ProcessIntelligenceModelError(
                "traces must be a tuple."
            )

        for trace in self.traces:
            if not isinstance(trace, ProcessTrace):
                raise ProcessIntelligenceModelError(
                    "traces must contain only ProcessTrace objects."
                )

        if not isinstance(
            self.activity_observations,
            tuple,
        ):
            raise ProcessIntelligenceModelError(
                "activity_observations must be a tuple."
            )

        for observation in self.activity_observations:
            if not isinstance(
                observation,
                ActivityObservation,
            ):
                raise ProcessIntelligenceModelError(
                    "activity_observations must contain "
                    "only ActivityObservation objects."
                )

        if not isinstance(
            self.transition_observations,
            tuple,
        ):
            raise ProcessIntelligenceModelError(
                "transition_observations must be a tuple."
            )

        for observation in self.transition_observations:
            if not isinstance(
                observation,
                TransitionObservation,
            ):
                raise ProcessIntelligenceModelError(
                    "transition_observations must contain "
                    "only TransitionObservation objects."
                )

        if self.metrics is not None and not isinstance(
            self.metrics,
            ProcessIntelligenceMetrics,
        ):
            raise ProcessIntelligenceModelError(
                "metrics must be ProcessIntelligenceMetrics or None."
            )

    @property
    def case_count(self) -> int:
        """
        Return the number of process cases represented by the dataset.
        """

        return len(self.traces)

    @property
    def event_count(self) -> int:
        """
        Return the total number of events represented by the dataset.
        """

        return sum(
            len(trace.events)
            for trace in self.traces
        )


# =============================================================================
# Public Exports
# =============================================================================


__all__ = [
    "ProcessIntelligenceModelError",
    "ProcessEvent",
    "ProcessTrace",
    "ActivityObservation",
    "TransitionObservation",
    "ProcessIntelligenceMetrics",
    "ProcessIntelligenceDataset",
]