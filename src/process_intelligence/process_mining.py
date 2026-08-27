"""
===============================================================================
AI Process Analyst
===============================================================================

Module:
    process_intelligence.process_mining

Purpose:
    Provide deterministic process-mining operations over the foundational
    Process Intelligence data models.

Milestone:
    Milestone 5 - Process Intelligence

Phase:
    Phase 5.2 - Implement Process Mining

Responsibilities:
    - Analyse process traces.
    - Calculate activity frequencies.
    - Calculate directly-follows transition frequencies.
    - Identify process variants.
    - Calculate basic process intelligence metrics.
    - Produce deterministic process-mining results.

This module intentionally performs descriptive process mining only.

It does NOT:
    - Discover executable process models.
    - Perform conformance checking.
    - Perform process simulation.
    - Predict KPIs.
    - Optimize processes.
    - Build digital twins.
    - Execute business rules.
    - Perform LLM inference.
===============================================================================
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable

from .process_intelligence_models import (
    ActivityObservation,
    ProcessEvent,
    ProcessIntelligenceDataset,
    ProcessIntelligenceMetrics,
    ProcessTrace,
    TransitionObservation,
)


# =============================================================================
# Errors
# =============================================================================


class ProcessMiningError(ValueError):
    """
    Raised when a Process Mining operation cannot be completed.
    """


# =============================================================================
# Process Variant
# =============================================================================


@dataclass(frozen=True)
class ProcessVariant:
    """
    Represent one observed process variant.

    A variant is identified by the ordered sequence of activities
    occurring in a process trace.
    """

    activities: tuple[str, ...]
    occurrence_count: int

    def __post_init__(self) -> None:
        if not isinstance(self.activities, tuple):
            raise ProcessMiningError(
                "activities must be a tuple."
            )

        for activity in self.activities:
            if not isinstance(activity, str) or not activity.strip():
                raise ProcessMiningError(
                    "variant activities must be non-empty strings."
                )

        if isinstance(self.occurrence_count, bool) or not isinstance(
            self.occurrence_count,
            int,
        ):
            raise ProcessMiningError(
                "occurrence_count must be an integer."
            )

        if self.occurrence_count < 0:
            raise ProcessMiningError(
                "occurrence_count must not be negative."
            )


# =============================================================================
# Process Mining Result
# =============================================================================


@dataclass(frozen=True)
class ProcessMiningResult:
    """
    Represent the deterministic output of a Process Mining operation.
    """

    dataset: ProcessIntelligenceDataset
    activity_observations: tuple[ActivityObservation, ...]
    transition_observations: tuple[TransitionObservation, ...]
    variants: tuple[ProcessVariant, ...]
    metrics: ProcessIntelligenceMetrics

    @property
    def case_count(self) -> int:
        """
        Return the number of cases analysed.
        """

        return self.metrics.case_count

    @property
    def event_count(self) -> int:
        """
        Return the number of events analysed.
        """

        return self.metrics.event_count

    @property
    def activity_count(self) -> int:
        """
        Return the number of distinct activities observed.
        """

        return self.metrics.activity_count

    @property
    def transition_count(self) -> int:
        """
        Return the number of distinct directly-follows transitions.
        """

        return self.metrics.transition_count

    @property
    def variant_count(self) -> int:
        """
        Return the number of distinct process variants.
        """

        return len(self.variants)


# =============================================================================
# Process Miner
# =============================================================================


class ProcessMiner:
    """
    Perform deterministic descriptive process mining.

    The miner operates exclusively on ProcessTrace and ProcessEvent
    structures established by the Process Intelligence data model.
    """

    def mine(
        self,
        traces: Iterable[ProcessTrace],
    ) -> ProcessMiningResult:
        """
        Mine a collection of process traces.

        Parameters
        ----------
        traces:
            Iterable containing ProcessTrace objects.

        Returns
        -------
        ProcessMiningResult
            Deterministic mining result containing activity observations,
            transition observations, process variants, and metrics.

        Raises
        ------
        ProcessMiningError
            If the input is invalid.
        """

        trace_tuple = self._validate_traces(traces)

        activity_durations = Counter()
        activity_counts = Counter()
        transition_counts = Counter()
        variant_counts = Counter()

        case_durations: list[float] = []

        for trace in trace_tuple:
            self._analyse_trace(
                trace=trace,
                activity_counts=activity_counts,
                activity_durations=activity_durations,
                transition_counts=transition_counts,
                variant_counts=variant_counts,
                case_durations=case_durations,
            )

        activity_observations = self._build_activity_observations(
            activity_counts=activity_counts,
            activity_durations=activity_durations,
        )

        transition_observations = self._build_transition_observations(
            transition_counts=transition_counts,
        )

        variants = self._build_variants(
            variant_counts=variant_counts,
        )

        metrics = self._build_metrics(
            traces=trace_tuple,
            activity_counts=activity_counts,
            transition_counts=transition_counts,
            case_durations=case_durations,
        )

        dataset = ProcessIntelligenceDataset(
            traces=trace_tuple,
            activity_observations=activity_observations,
            transition_observations=transition_observations,
            metrics=metrics,
        )

        return ProcessMiningResult(
            dataset=dataset,
            activity_observations=activity_observations,
            transition_observations=transition_observations,
            variants=variants,
            metrics=metrics,
        )

    # =========================================================================
    # Validation
    # =========================================================================

    @staticmethod
    def _validate_traces(
        traces: Iterable[ProcessTrace],
    ) -> tuple[ProcessTrace, ...]:
        """
        Validate and normalize the trace collection.
        """

        if isinstance(traces, (str, bytes)):
            raise ProcessMiningError(
                "traces must be an iterable of ProcessTrace objects."
            )

        try:
            trace_tuple = tuple(traces)
        except TypeError as exc:
            raise ProcessMiningError(
                "traces must be an iterable of ProcessTrace objects."
            ) from exc

        for trace in trace_tuple:
            if not isinstance(trace, ProcessTrace):
                raise ProcessMiningError(
                    "traces must contain only ProcessTrace objects."
                )

        return trace_tuple

    # =========================================================================
    # Trace Analysis
    # =========================================================================

    @staticmethod
    def _analyse_trace(
        *,
        trace: ProcessTrace,
        activity_counts: Counter[str],
        activity_durations: Counter[str],
        transition_counts: Counter[tuple[str, str]],
        variant_counts: Counter[tuple[str, ...]],
        case_durations: list[float],
    ) -> None:
        """
        Analyse one process trace.
        """

        events = trace.events

        if not events:
            variant_counts[()] += 1
            return

        activities = tuple(
            event.activity
            for event in events
        )

        variant_counts[activities] += 1

        for event in events:
            activity_counts[event.activity] += 1

        for previous, current in zip(
            events,
            events[1:],
        ):
            transition_counts[
                (
                    previous.activity,
                    current.activity,
                )
            ] += 1

            duration = (
                current.timestamp - previous.timestamp
            ).total_seconds()

            if duration < 0:
                raise ProcessMiningError(
                    "process trace contains negative event duration."
                )

            activity_durations[
                previous.activity
            ] += duration

        if len(events) >= 2:
            case_duration = (
                events[-1].timestamp
                - events[0].timestamp
            ).total_seconds()

            if case_duration < 0:
                raise ProcessMiningError(
                    "process trace contains negative case duration."
                )

            case_durations.append(case_duration)
        else:
            case_durations.append(0.0)

    # =========================================================================
    # Activity Observations
    # =========================================================================

    @staticmethod
    def _build_activity_observations(
        *,
        activity_counts: Counter[str],
        activity_durations: Counter[str],
    ) -> tuple[ActivityObservation, ...]:
        """
        Build deterministic activity observations.
        """

        observations = [
            ActivityObservation(
                activity=activity,
                occurrence_count=activity_counts[activity],
                total_duration_seconds=activity_durations.get(
                    activity,
                    0.0,
                ),
            )
            for activity in sorted(activity_counts)
        ]

        return tuple(observations)

    # =========================================================================
    # Transition Observations
    # =========================================================================

    @staticmethod
    def _build_transition_observations(
        *,
        transition_counts: Counter[tuple[str, str]],
    ) -> tuple[TransitionObservation, ...]:
        """
        Build deterministic directly-follows transition observations.
        """

        observations = [
            TransitionObservation(
                source_activity=source,
                target_activity=target,
                occurrence_count=count,
            )
            for (source, target), count in sorted(
                transition_counts.items()
            )
        ]

        return tuple(observations)

    # =========================================================================
    # Process Variants
    # =========================================================================

    @staticmethod
    def _build_variants(
        *,
        variant_counts: Counter[tuple[str, ...]],
    ) -> tuple[ProcessVariant, ...]:
        """
        Build deterministic process variants.

        Variants are ordered first by descending occurrence count and then
        lexicographically by their activity sequence.
        """

        ordered = sorted(
            variant_counts.items(),
            key=lambda item: (
                -item[1],
                item[0],
            ),
        )

        return tuple(
            ProcessVariant(
                activities=activities,
                occurrence_count=count,
            )
            for activities, count in ordered
        )

    # =========================================================================
    # Metrics
    # =========================================================================

    @staticmethod
    def _build_metrics(
        *,
        traces: tuple[ProcessTrace, ...],
        activity_counts: Counter[str],
        transition_counts: Counter[tuple[str, str]],
        case_durations: list[float],
    ) -> ProcessIntelligenceMetrics:
        """
        Build high-level process intelligence metrics.
        """

        event_count = sum(
            len(trace.events)
            for trace in traces
        )

        case_count = len(traces)

        average_case_duration = (
            sum(case_durations) / len(case_durations)
            if case_durations
            else 0.0
        )

        return ProcessIntelligenceMetrics(
            case_count=case_count,
            event_count=event_count,
            activity_count=len(activity_counts),
            transition_count=len(transition_counts),
            average_case_duration_seconds=(
                average_case_duration
            ),
            throughput_per_day=(
                ProcessMiner._calculate_throughput_per_day(
                    case_durations=case_durations,
                )
            ),
        )

    @staticmethod
    def _calculate_throughput_per_day(
        *,
        case_durations: list[float],
    ) -> float:
        """
        Calculate a basic throughput-per-day estimate.

        For the descriptive mining layer, throughput is derived from
        the average case duration. When there are no cases, throughput
        is zero.
        """

        if not case_durations:
            return 0.0

        average_duration = (
            sum(case_durations)
            / len(case_durations)
        )

        if average_duration <= 0:
            return 0.0

        seconds_per_day = 24 * 60 * 60

        return (
            seconds_per_day
            / average_duration
        )


# =============================================================================
# Convenience API
# =============================================================================


def mine_process(
    traces: Iterable[ProcessTrace],
) -> ProcessMiningResult:
    """
    Convenience function for deterministic Process Mining.

    Parameters
    ----------
    traces:
        Iterable of ProcessTrace objects.

    Returns
    -------
    ProcessMiningResult
        Process Mining result.
    """

    return ProcessMiner().mine(traces)


# =============================================================================
# Public Exports
# =============================================================================


__all__ = [
    "ProcessMiningError",
    "ProcessVariant",
    "ProcessMiningResult",
    "ProcessMiner",
    "mine_process",
]