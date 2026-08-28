"""
===============================================================================
AI Process Analyst
===============================================================================

Module:
    process_intelligence.process_conformance

Purpose:
    Provide deterministic process conformance analysis for observed process
    traces against an expected process model.

Phase:
    Milestone 5 - Process Intelligence
    Phase 5.4 - Process Conformance Analysis

Responsibilities:
    - Represent expected process paths.
    - Compare observed traces with expected process paths.
    - Detect unexpected activities.
    - Detect missing activities.
    - Detect ordering violations.
    - Calculate trace-level conformance scores.
    - Calculate aggregate conformance metrics.
    - Produce deterministic conformance findings.

This module intentionally does NOT:
    - Perform process discovery.
    - Perform process simulation.
    - Predict KPIs.
    - Optimize processes.
    - Build a digital twin.
    - Execute business rules.
    - Perform LLM inference.
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Mapping

from .process_intelligence_models import ProcessTrace


# =============================================================================
# Errors
# =============================================================================


class ProcessConformanceError(ValueError):
    """Raised when process conformance input is invalid."""


# =============================================================================
# Expected Process Model
# =============================================================================


@dataclass(frozen=True)
class ExpectedProcessModel:
    """
    Represent the expected activity sequence for a process.

    The model is intentionally sequence-based at this phase. More advanced
    process representations can be introduced later without changing the
    basic conformance result contract.
    """

    process_id: str
    activities: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.process_id, str) or not self.process_id.strip():
            raise ProcessConformanceError(
                "process_id must be a non-empty string."
            )

        if not isinstance(self.activities, tuple):
            raise ProcessConformanceError(
                "activities must be a tuple."
            )

        if not self.activities:
            raise ProcessConformanceError(
                "activities must contain at least one activity."
            )

        for activity in self.activities:
            if not isinstance(activity, str) or not activity.strip():
                raise ProcessConformanceError(
                    "activities must contain only non-empty strings."
                )


# =============================================================================
# Conformance Finding
# =============================================================================


@dataclass(frozen=True)
class ConformanceFinding:
    """
    Represent one conformance deviation.
    """

    finding_type: str
    activity: str | None = None
    expected_activity: str | None = None
    position: int | None = None
    message: str = ""

    def __post_init__(self) -> None:
        valid_types = {
            "unexpected_activity",
            "missing_activity",
            "ordering_violation",
        }

        if self.finding_type not in valid_types:
            raise ProcessConformanceError(
                "finding_type must be one of: "
                "unexpected_activity, missing_activity, "
                "ordering_violation."
            )

        if self.position is not None:
            if not isinstance(self.position, int):
                raise ProcessConformanceError(
                    "position must be an integer or None."
                )

            if self.position < 0:
                raise ProcessConformanceError(
                    "position must not be negative."
                )

        if not isinstance(self.message, str):
            raise ProcessConformanceError(
                "message must be a string."
            )


# =============================================================================
# Trace Conformance Result
# =============================================================================


@dataclass(frozen=True)
class TraceConformanceResult:
    """
    Represent conformance analysis for one process trace.
    """

    case_id: str
    score: float
    conformant: bool
    findings: tuple[ConformanceFinding, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.case_id, str) or not self.case_id.strip():
            raise ProcessConformanceError(
                "case_id must be a non-empty string."
            )

        if not isinstance(self.score, (int, float)):
            raise ProcessConformanceError(
                "score must be numeric."
            )

        if not 0.0 <= float(self.score) <= 1.0:
            raise ProcessConformanceError(
                "score must be between 0.0 and 1.0."
            )

        if not isinstance(self.conformant, bool):
            raise ProcessConformanceError(
                "conformant must be a boolean."
            )

        if not isinstance(self.findings, tuple):
            raise ProcessConformanceError(
                "findings must be a tuple."
            )

        for finding in self.findings:
            if not isinstance(finding, ConformanceFinding):
                raise ProcessConformanceError(
                    "findings must contain only ConformanceFinding objects."
                )


# =============================================================================
# Aggregate Conformance Result
# =============================================================================


@dataclass(frozen=True)
class ProcessConformanceResult:
    """
    Represent aggregate process conformance analysis.
    """

    process_id: str
    trace_results: tuple[TraceConformanceResult, ...]
    average_score: float
    conformant_case_count: int
    non_conformant_case_count: int
    finding_counts: Mapping[str, int] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.process_id, str) or not self.process_id.strip():
            raise ProcessConformanceError(
                "process_id must be a non-empty string."
            )

        if not isinstance(self.trace_results, tuple):
            raise ProcessConformanceError(
                "trace_results must be a tuple."
            )

        for result in self.trace_results:
            if not isinstance(result, TraceConformanceResult):
                raise ProcessConformanceError(
                    "trace_results must contain only "
                    "TraceConformanceResult objects."
                )

        if not isinstance(self.average_score, (int, float)):
            raise ProcessConformanceError(
                "average_score must be numeric."
            )

        if not 0.0 <= float(self.average_score) <= 1.0:
            raise ProcessConformanceError(
                "average_score must be between 0.0 and 1.0."
            )

        for name, value in {
            "conformant_case_count": self.conformant_case_count,
            "non_conformant_case_count": self.non_conformant_case_count,
        }.items():
            if not isinstance(value, int):
                raise ProcessConformanceError(
                    f"{name} must be an integer."
                )

            if value < 0:
                raise ProcessConformanceError(
                    f"{name} must not be negative."
                )

        if (
            self.conformant_case_count
            + self.non_conformant_case_count
            != len(self.trace_results)
        ):
            raise ProcessConformanceError(
                "case counts must match trace_results."
            )

        if not isinstance(self.finding_counts, Mapping):
            raise ProcessConformanceError(
                "finding_counts must be a mapping."
            )

        for finding_type, count in self.finding_counts.items():
            if not isinstance(finding_type, str) or not finding_type.strip():
                raise ProcessConformanceError(
                    "finding type names must be non-empty strings."
                )

            if not isinstance(count, int):
                raise ProcessConformanceError(
                    "finding counts must be integers."
                )

            if count < 0:
                raise ProcessConformanceError(
                    "finding counts must not be negative."
                )

    @property
    def trace_count(self) -> int:
        """Return the number of analysed traces."""

        return len(self.trace_results)


# =============================================================================
# Process Conformance Analyzer
# =============================================================================


class ProcessConformanceAnalyzer:
    """
    Analyse observed process traces against an expected activity sequence.
    """

    def analyse_trace(
        self,
        trace: ProcessTrace,
        model: ExpectedProcessModel,
    ) -> TraceConformanceResult:
        """
        Analyse one trace against the expected process model.
        """

        if not isinstance(trace, ProcessTrace):
            raise ProcessConformanceError(
                "trace must be a ProcessTrace."
            )

        if not isinstance(model, ExpectedProcessModel):
            raise ProcessConformanceError(
                "model must be an ExpectedProcessModel."
            )

        observed = tuple(
            event.activity
            for event in trace.events
        )
        expected = model.activities

        findings: list[ConformanceFinding] = []

        # ---------------------------------------------------------------------
        # Empty trace
        # ---------------------------------------------------------------------

        if not observed:
            for position, activity in enumerate(expected):
                findings.append(
                    ConformanceFinding(
                        finding_type="missing_activity",
                        expected_activity=activity,
                        position=position,
                        message=(
                            f"Expected activity '{activity}' was not observed."
                        ),
                    )
                )

            return TraceConformanceResult(
                case_id=trace.case_id,
                score=0.0,
                conformant=False,
                findings=tuple(findings),
            )

        # ---------------------------------------------------------------------
        # Determine sequence alignment.
        #
        # The algorithm walks through the observed sequence while maintaining
        # the next expected position.
        #
        # This intentionally remains deterministic and dependency-free.
        # ---------------------------------------------------------------------

        expected_index = 0
        matched = 0
        total_expected = len(expected)

        for observed_position, activity in enumerate(observed):
            if expected_index >= total_expected:
                findings.append(
                    ConformanceFinding(
                        finding_type="unexpected_activity",
                        activity=activity,
                        position=observed_position,
                        message=(
                            f"Unexpected activity '{activity}' occurred "
                            "after the expected process sequence."
                        ),
                    )
                )
                continue

            expected_activity = expected[expected_index]

            if activity == expected_activity:
                matched += 1
                expected_index += 1
                continue

            # -----------------------------------------------------------------
            # If the observed activity occurs later in the expected sequence,
            # earlier expected activities were skipped.
            # -----------------------------------------------------------------

            later_index = self._find_later_expected_activity(
                expected,
                expected_index + 1,
                activity,
            )

            if later_index is not None:
                for missing_index in range(
                    expected_index,
                    later_index,
                ):
                    missing_activity = expected[missing_index]

                    findings.append(
                        ConformanceFinding(
                            finding_type="missing_activity",
                            expected_activity=missing_activity,
                            position=observed_position,
                            message=(
                                f"Expected activity '{missing_activity}' "
                                f"was not observed before '{activity}'."
                            ),
                        )
                    )

                findings.append(
                    ConformanceFinding(
                        finding_type="ordering_violation",
                        activity=activity,
                        expected_activity=expected_activity,
                        position=observed_position,
                        message=(
                            f"Activity '{activity}' occurred where "
                            f"'{expected_activity}' was expected."
                        ),
                    )
                )

                matched += 1
                expected_index = later_index + 1
                continue

            # -----------------------------------------------------------------
            # Otherwise the observed activity is not expected at this point.
            # -----------------------------------------------------------------

            findings.append(
                ConformanceFinding(
                    finding_type="unexpected_activity",
                    activity=activity,
                    expected_activity=expected_activity,
                    position=observed_position,
                    message=(
                        f"Unexpected activity '{activity}' occurred; "
                        f"expected '{expected_activity}'."
                    ),
                )
            )

        # ---------------------------------------------------------------------
        # Remaining expected activities were not observed.
        # ---------------------------------------------------------------------

        for missing_index in range(
            expected_index,
            total_expected,
        ):
            missing_activity = expected[missing_index]

            findings.append(
                ConformanceFinding(
                    finding_type="missing_activity",
                    expected_activity=missing_activity,
                    position=len(observed),
                    message=(
                        f"Expected activity '{missing_activity}' "
                        "was not observed."
                    ),
                )
            )

        # ---------------------------------------------------------------------
        # Score
        #
        # Score represents the proportion of expected activities successfully
        # represented by the observed trace, penalised by unexpected activities.
        #
        # A fully conformant trace therefore receives 1.0.
        # ---------------------------------------------------------------------

        deviation_count = len(findings)

        if not findings:
            score = 1.0
        else:
            denominator = max(
                len(expected),
                len(observed),
                1,
            )
            score = max(
                0.0,
                min(
                    1.0,
                    (matched - deviation_count) / denominator,
                ),
            )

        return TraceConformanceResult(
            case_id=trace.case_id,
            score=score,
            conformant=not findings,
            findings=tuple(findings),
        )

    def analyse(
        self,
        traces: Iterable[ProcessTrace],
        model: ExpectedProcessModel,
    ) -> ProcessConformanceResult:
        """
        Analyse multiple process traces against one expected process model.
        """

        if not isinstance(model, ExpectedProcessModel):
            raise ProcessConformanceError(
                "model must be an ExpectedProcessModel."
            )

        if isinstance(traces, (str, bytes)):
            raise ProcessConformanceError(
                "traces must be an iterable of ProcessTrace objects."
            )

        try:
            trace_items = tuple(traces)
        except TypeError as exc:
            raise ProcessConformanceError(
                "traces must be iterable."
            ) from exc

        results = tuple(
            self.analyse_trace(trace, model)
            for trace in trace_items
        )

        if results:
            average_score = (
                sum(result.score for result in results)
                / len(results)
            )
        else:
            average_score = 0.0

        conformant_case_count = sum(
            1
            for result in results
            if result.conformant
        )

        non_conformant_case_count = (
            len(results) - conformant_case_count
        )

        finding_counts: dict[str, int] = {}

        for result in results:
            for finding in result.findings:
                finding_counts[finding.finding_type] = (
                    finding_counts.get(finding.finding_type, 0)
                    + 1
                )

        return ProcessConformanceResult(
            process_id=model.process_id,
            trace_results=results,
            average_score=average_score,
            conformant_case_count=conformant_case_count,
            non_conformant_case_count=non_conformant_case_count,
            finding_counts=finding_counts,
        )

    @staticmethod
    def _find_later_expected_activity(
        expected: tuple[str, ...],
        start_index: int,
        activity: str,
    ) -> int | None:
        """
        Find an activity later in the expected sequence.
        """

        for index in range(
            start_index,
            len(expected),
        ):
            if expected[index] == activity:
                return index

        return None


# =============================================================================
# Public Exports
# =============================================================================


__all__ = [
    "ProcessConformanceError",
    "ExpectedProcessModel",
    "ConformanceFinding",
    "TraceConformanceResult",
    "ProcessConformanceResult",
    "ProcessConformanceAnalyzer",
]