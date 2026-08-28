"""
===============================================================================
AI Process Analyst
===============================================================================

Module:
    process_intelligence.process_performance

Purpose:
    Provide deterministic process performance analysis over Process Intelligence
    traces and observations.

Phase:
    Milestone 5 - Process Intelligence
    Phase 5.5 - Process Performance Analysis

Responsibilities:
    - Calculate process cycle-time statistics.
    - Calculate activity duration statistics.
    - Identify slow activities.
    - Calculate activity frequency.
    - Calculate transition frequency.
    - Calculate throughput.
    - Identify performance bottlenecks.
    - Produce deterministic performance summaries.

This module intentionally performs analytical calculations only.

It does NOT:
    - Perform LLM inference.
    - Predict future KPIs.
    - Optimize process execution.
    - Modify process data.
    - Execute business actions.
    - Build a digital twin.
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from statistics import mean, median
from typing import Iterable

from .process_intelligence_models import (
    ActivityObservation,
    ProcessEvent,
    ProcessIntelligenceDataset,
    ProcessIntelligenceModelError,
    ProcessTrace,
    TransitionObservation,
)


# =============================================================================
# Errors
# =============================================================================


class ProcessPerformanceError(ValueError):
    """
    Raised when process performance analysis input is invalid.
    """


# =============================================================================
# Performance Metric
# =============================================================================


@dataclass(frozen=True)
class ProcessPerformanceMetric:
    """
    Represent one calculated process performance metric.
    """

    metric: str
    value: float
    unit: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.metric, str) or not self.metric.strip():
            raise ProcessPerformanceError(
                "metric must be a non-empty string."
            )

        if not isinstance(self.value, (int, float)):
            raise ProcessPerformanceError(
                "value must be numeric."
            )

        if not isinstance(self.unit, str):
            raise ProcessPerformanceError(
                "unit must be a string."
            )


# =============================================================================
# Activity Performance
# =============================================================================


@dataclass(frozen=True)
class ActivityPerformance:
    """
    Represent calculated performance information for one activity.
    """

    activity: str
    occurrence_count: int
    total_duration_seconds: float
    average_duration_seconds: float
    median_duration_seconds: float
    minimum_duration_seconds: float
    maximum_duration_seconds: float

    def __post_init__(self) -> None:
        if not isinstance(self.activity, str) or not self.activity.strip():
            raise ProcessPerformanceError(
                "activity must be a non-empty string."
            )

        if not isinstance(self.occurrence_count, int):
            raise ProcessPerformanceError(
                "occurrence_count must be an integer."
            )

        if self.occurrence_count < 0:
            raise ProcessPerformanceError(
                "occurrence_count must not be negative."
            )

        numeric_fields = {
            "total_duration_seconds": self.total_duration_seconds,
            "average_duration_seconds": self.average_duration_seconds,
            "median_duration_seconds": self.median_duration_seconds,
            "minimum_duration_seconds": self.minimum_duration_seconds,
            "maximum_duration_seconds": self.maximum_duration_seconds,
        }

        for name, value in numeric_fields.items():
            if not isinstance(value, (int, float)):
                raise ProcessPerformanceError(
                    f"{name} must be numeric."
                )

            if value < 0:
                raise ProcessPerformanceError(
                    f"{name} must not be negative."
                )

        if self.occurrence_count == 0:
            expected = {
                "total_duration_seconds": 0.0,
                "average_duration_seconds": 0.0,
                "median_duration_seconds": 0.0,
                "minimum_duration_seconds": 0.0,
                "maximum_duration_seconds": 0.0,
            }

            for name, expected_value in expected.items():
                if getattr(self, name) != expected_value:
                    raise ProcessPerformanceError(
                        f"{name} must be 0 when occurrence_count is 0."
                    )


# =============================================================================
# Bottleneck
# =============================================================================


@dataclass(frozen=True)
class ProcessBottleneck:
    """
    Represent a detected process performance bottleneck.
    """

    activity: str
    average_duration_seconds: float
    relative_share: float
    rank: int

    def __post_init__(self) -> None:
        if not isinstance(self.activity, str) or not self.activity.strip():
            raise ProcessPerformanceError(
                "activity must be a non-empty string."
            )

        if not isinstance(
            self.average_duration_seconds,
            (int, float),
        ):
            raise ProcessPerformanceError(
                "average_duration_seconds must be numeric."
            )

        if self.average_duration_seconds < 0:
            raise ProcessPerformanceError(
                "average_duration_seconds must not be negative."
            )

        if not isinstance(self.relative_share, (int, float)):
            raise ProcessPerformanceError(
                "relative_share must be numeric."
            )

        if not 0.0 <= self.relative_share <= 1.0:
            raise ProcessPerformanceError(
                "relative_share must be between 0 and 1."
            )

        if not isinstance(self.rank, int):
            raise ProcessPerformanceError(
                "rank must be an integer."
            )

        if self.rank < 1:
            raise ProcessPerformanceError(
                "rank must be greater than or equal to 1."
            )


# =============================================================================
# Performance Result
# =============================================================================


@dataclass(frozen=True)
class ProcessPerformanceResult:
    """
    Complete deterministic process performance analysis result.
    """

    case_count: int
    event_count: int
    average_case_duration_seconds: float
    median_case_duration_seconds: float
    minimum_case_duration_seconds: float
    maximum_case_duration_seconds: float
    throughput_per_day: float
    activity_performance: tuple[ActivityPerformance, ...]
    bottlenecks: tuple[ProcessBottleneck, ...]
    metrics: tuple[ProcessPerformanceMetric, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.case_count, int):
            raise ProcessPerformanceError(
                "case_count must be an integer."
            )

        if self.case_count < 0:
            raise ProcessPerformanceError(
                "case_count must not be negative."
            )

        if not isinstance(self.event_count, int):
            raise ProcessPerformanceError(
                "event_count must be an integer."
            )

        if self.event_count < 0:
            raise ProcessPerformanceError(
                "event_count must not be negative."
            )

        numeric_fields = {
            "average_case_duration_seconds":
                self.average_case_duration_seconds,
            "median_case_duration_seconds":
                self.median_case_duration_seconds,
            "minimum_case_duration_seconds":
                self.minimum_case_duration_seconds,
            "maximum_case_duration_seconds":
                self.maximum_case_duration_seconds,
            "throughput_per_day": self.throughput_per_day,
        }

        for name, value in numeric_fields.items():
            if not isinstance(value, (int, float)):
                raise ProcessPerformanceError(
                    f"{name} must be numeric."
                )

            if value < 0:
                raise ProcessPerformanceError(
                    f"{name} must not be negative."
                )

        if not isinstance(self.activity_performance, tuple):
            raise ProcessPerformanceError(
                "activity_performance must be a tuple."
            )

        for item in self.activity_performance:
            if not isinstance(item, ActivityPerformance):
                raise ProcessPerformanceError(
                    "activity_performance must contain only "
                    "ActivityPerformance objects."
                )

        if not isinstance(self.bottlenecks, tuple):
            raise ProcessPerformanceError(
                "bottlenecks must be a tuple."
            )

        for item in self.bottlenecks:
            if not isinstance(item, ProcessBottleneck):
                raise ProcessPerformanceError(
                    "bottlenecks must contain only "
                    "ProcessBottleneck objects."
                )

        if not isinstance(self.metrics, tuple):
            raise ProcessPerformanceError(
                "metrics must be a tuple."
            )

        for item in self.metrics:
            if not isinstance(item, ProcessPerformanceMetric):
                raise ProcessPerformanceError(
                    "metrics must contain only "
                    "ProcessPerformanceMetric objects."
                )

        if self.case_count == 0:
            zero_fields = (
                "average_case_duration_seconds",
                "median_case_duration_seconds",
                "minimum_case_duration_seconds",
                "maximum_case_duration_seconds",
                "throughput_per_day",
            )

            for name in zero_fields:
                if getattr(self, name) != 0.0:
                    raise ProcessPerformanceError(
                        f"{name} must be 0 when case_count is 0."
                    )


# =============================================================================
# Process Performance Analyzer
# =============================================================================


class ProcessPerformanceAnalyzer:
    """
    Calculate deterministic performance measurements from process traces.
    """

    def __init__(
        self,
        bottleneck_limit: int = 5,
    ) -> None:
        if not isinstance(bottleneck_limit, int):
            raise ProcessPerformanceError(
                "bottleneck_limit must be an integer."
            )

        if bottleneck_limit < 1:
            raise ProcessPerformanceError(
                "bottleneck_limit must be greater than or equal to 1."
            )

        self.bottleneck_limit = bottleneck_limit

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    def analyze(
        self,
        traces: Iterable[ProcessTrace],
    ) -> ProcessPerformanceResult:
        """
        Analyze process performance from traces.
        """

        trace_tuple = self._validate_traces(traces)

        case_durations = [
            self._case_duration_seconds(trace)
            for trace in trace_tuple
            if trace.events
        ]

        event_count = sum(
            len(trace.events)
            for trace in trace_tuple
        )

        activity_durations = self._collect_activity_durations(
            trace_tuple
        )

        activity_performance = tuple(
            self._build_activity_performance(
                activity,
                durations,
            )
            for activity, durations in sorted(
                activity_durations.items()
            )
        )

        throughput = self._calculate_throughput(
            case_durations
        )

        bottlenecks = self._identify_bottlenecks(
            activity_performance
        )

        metrics = self._build_metrics(
            case_durations=case_durations,
            throughput=throughput,
            activity_performance=activity_performance,
            bottlenecks=bottlenecks,
        )

        return ProcessPerformanceResult(
            case_count=len(trace_tuple),
            event_count=event_count,
            average_case_duration_seconds=(
                mean(case_durations)
                if case_durations
                else 0.0
            ),
            median_case_duration_seconds=(
                median(case_durations)
                if case_durations
                else 0.0
            ),
            minimum_case_duration_seconds=(
                min(case_durations)
                if case_durations
                else 0.0
            ),
            maximum_case_duration_seconds=(
                max(case_durations)
                if case_durations
                else 0.0
            ),
            throughput_per_day=throughput,
            activity_performance=activity_performance,
            bottlenecks=bottlenecks,
            metrics=metrics,
        )

    def analyze_dataset(
        self,
        dataset: ProcessIntelligenceDataset,
    ) -> ProcessPerformanceResult:
        """
        Analyze an existing Process Intelligence dataset.
        """

        if not isinstance(
            dataset,
            ProcessIntelligenceDataset,
        ):
            raise ProcessPerformanceError(
                "dataset must be a ProcessIntelligenceDataset."
            )

        return self.analyze(dataset.traces)

    # -------------------------------------------------------------------------
    # Validation
    # -------------------------------------------------------------------------

    @staticmethod
    def _validate_traces(
        traces: Iterable[ProcessTrace],
    ) -> tuple[ProcessTrace, ...]:
        if isinstance(traces, (str, bytes)):
            raise ProcessPerformanceError(
                "traces must be an iterable of ProcessTrace objects."
            )

        try:
            trace_tuple = tuple(traces)
        except TypeError as exc:
            raise ProcessPerformanceError(
                "traces must be iterable."
            ) from exc

        for trace in trace_tuple:
            if not isinstance(trace, ProcessTrace):
                raise ProcessPerformanceError(
                    "traces must contain only ProcessTrace objects."
                )

        return trace_tuple

    # -------------------------------------------------------------------------
    # Case Duration
    # -------------------------------------------------------------------------

    @staticmethod
    def _case_duration_seconds(
        trace: ProcessTrace,
    ) -> float:
        if not trace.events:
            return 0.0

        return (
            trace.events[-1].timestamp
            - trace.events[0].timestamp
        ).total_seconds()

    # -------------------------------------------------------------------------
    # Activity Duration
    # -------------------------------------------------------------------------

    @staticmethod
    def _collect_activity_durations(
        traces: tuple[ProcessTrace, ...],
    ) -> dict[str, list[float]]:
        """
        Calculate activity durations.

        Every activity observed in the traces is registered in the result.

        An activity duration is measured from the activity event to
        the immediately following event in the same trace.

        The final event of a trace has no following event and therefore
        contributes no duration. Its activity remains present with an
        empty duration list so that downstream performance reporting can
        represent it with zero duration statistics.
        """

        durations: dict[str, list[float]] = {}

        for trace in traces:
            # Register every observed activity, including the final activity.
            for event in trace.events:
                durations.setdefault(
                    event.activity,
                    [],
                )

            # Calculate durations only where a following event exists.
            for current, following in zip(
                trace.events,
                trace.events[1:],
            ):
                duration = (
                    following.timestamp
                    - current.timestamp
                ).total_seconds()

                if duration < 0:
                    raise ProcessPerformanceError(
                        "trace events must be ordered by timestamp."
                    )

                durations[current.activity].append(
                    duration
                )

        return durations

    @staticmethod
    def _build_activity_performance(
        activity: str,
        durations: list[float],
    ) -> ActivityPerformance:
        if not durations:
            return ActivityPerformance(
                activity=activity,
                occurrence_count=0,
                total_duration_seconds=0.0,
                average_duration_seconds=0.0,
                median_duration_seconds=0.0,
                minimum_duration_seconds=0.0,
                maximum_duration_seconds=0.0,
            )

        return ActivityPerformance(
            activity=activity,
            occurrence_count=len(durations),
            total_duration_seconds=sum(durations),
            average_duration_seconds=mean(durations),
            median_duration_seconds=median(durations),
            minimum_duration_seconds=min(durations),
            maximum_duration_seconds=max(durations),
        )

    # -------------------------------------------------------------------------
    # Throughput
    # -------------------------------------------------------------------------

    @staticmethod
    def _calculate_throughput(
        case_durations: list[float],
    ) -> float:
        """
        Calculate theoretical daily throughput from average cycle time.

        Throughput is expressed as cases per 24 hours.
        """

        if not case_durations:
            return 0.0

        average_duration = mean(case_durations)

        if average_duration <= 0:
            return 0.0

        return 86400.0 / average_duration

    # -------------------------------------------------------------------------
    # Bottleneck Detection
    # -------------------------------------------------------------------------

    def _identify_bottlenecks(
        self,
        activity_performance: tuple[ActivityPerformance, ...],
    ) -> tuple[ProcessBottleneck, ...]:
        """
        Identify activities with the greatest observed durations.

        Activities with zero occurrences are excluded because they have
        no measured duration and therefore cannot be a bottleneck.
        """

        if not activity_performance:
            return ()

        # Only activities with at least one measured duration can be
        # considered bottlenecks.
        measured_activities = tuple(
            item
            for item in activity_performance
            if item.occurrence_count > 0
        )

        if not measured_activities:
            return ()

        total_duration = sum(
            item.total_duration_seconds
            for item in measured_activities
        )

        ranked = sorted(
            measured_activities,
            key=lambda item: (
                item.average_duration_seconds,
                item.total_duration_seconds,
                item.activity,
            ),
            reverse=True,
        )

        selected = ranked[: self.bottleneck_limit]

        result: list[ProcessBottleneck] = []

        for rank, item in enumerate(selected, start=1):
            if total_duration > 0:
                relative_share = (
                    item.total_duration_seconds
                    / total_duration
                )
            else:
                relative_share = 0.0

            result.append(
                ProcessBottleneck(
                    activity=item.activity,
                    average_duration_seconds=(
                        item.average_duration_seconds
                    ),
                    relative_share=relative_share,
                    rank=rank,
                )
            )

        return tuple(result)

    # -------------------------------------------------------------------------
    # Metrics
    # -------------------------------------------------------------------------

    @staticmethod
    def _build_metrics(
        case_durations: list[float],
        throughput: float,
        activity_performance: tuple[ActivityPerformance, ...],
        bottlenecks: tuple[ProcessBottleneck, ...],
    ) -> tuple[ProcessPerformanceMetric, ...]:
        average_case_duration = (
            mean(case_durations)
            if case_durations
            else 0.0
        )

        return (
            ProcessPerformanceMetric(
                metric="average_case_duration",
                value=average_case_duration,
                unit="seconds",
            ),
            ProcessPerformanceMetric(
                metric="throughput",
                value=throughput,
                unit="cases_per_day",
            ),
            ProcessPerformanceMetric(
                metric="activity_count",
                value=float(len(activity_performance)),
                unit="activities",
            ),
            ProcessPerformanceMetric(
                metric="bottleneck_count",
                value=float(len(bottlenecks)),
                unit="activities",
            ),
        )


# =============================================================================
# Convenience Functions
# =============================================================================


def analyze_process_performance(
    traces: Iterable[ProcessTrace],
    bottleneck_limit: int = 5,
) -> ProcessPerformanceResult:
    """
    Convenience function for process performance analysis.
    """

    return ProcessPerformanceAnalyzer(
        bottleneck_limit=bottleneck_limit,
    ).analyze(traces)


__all__ = [
    "ProcessPerformanceError",
    "ProcessPerformanceMetric",
    "ActivityPerformance",
    "ProcessBottleneck",
    "ProcessPerformanceResult",
    "ProcessPerformanceAnalyzer",
    "analyze_process_performance",
]