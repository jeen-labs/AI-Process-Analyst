"""
===============================================================================
Tests:
    Process Conformance Analysis

Phase:
    Milestone 5 - Process Intelligence
    Phase 5.4 - Process Conformance Analysis
===============================================================================
"""

from datetime import datetime, timedelta, timezone

import pytest

from src.process_intelligence.process_conformance import (
    ConformanceFinding,
    ExpectedProcessModel,
    ProcessConformanceAnalyzer,
    ProcessConformanceError,
    ProcessConformanceResult,
    TraceConformanceResult,
)
from src.process_intelligence.process_intelligence_models import (
    ProcessEvent,
    ProcessTrace,
)


def _timestamp(offset_seconds: int = 0) -> datetime:
    return datetime(
        2026,
        8,
        28,
        10,
        0,
        tzinfo=timezone.utc,
    ) + timedelta(seconds=offset_seconds)


def _trace(
    case_id: str,
    activities: tuple[str, ...],
) -> ProcessTrace:
    events = tuple(
        ProcessEvent(
            case_id=case_id,
            activity=activity,
            timestamp=_timestamp(index * 60),
        )
        for index, activity in enumerate(activities)
    )

    return ProcessTrace(
        case_id=case_id,
        events=events,
    )


def _model(
    activities: tuple[str, ...] = (
        "receive",
        "approve",
        "complete",
    ),
) -> ExpectedProcessModel:
    return ExpectedProcessModel(
        process_id="proc-001",
        activities=activities,
    )


# =============================================================================
# Expected Process Model
# =============================================================================


def test_expected_process_model_can_be_created() -> None:
    model = _model()

    assert model.process_id == "proc-001"
    assert model.activities == (
        "receive",
        "approve",
        "complete",
    )


def test_expected_process_model_rejects_empty_process_id() -> None:
    with pytest.raises(ProcessConformanceError):
        ExpectedProcessModel(
            process_id="",
            activities=("receive",),
        )


def test_expected_process_model_rejects_empty_activities() -> None:
    with pytest.raises(ProcessConformanceError):
        ExpectedProcessModel(
            process_id="proc-001",
            activities=(),
        )


def test_expected_process_model_rejects_invalid_activity() -> None:
    with pytest.raises(ProcessConformanceError):
        ExpectedProcessModel(
            process_id="proc-001",
            activities=("receive", ""),
        )


# =============================================================================
# Conformance Finding
# =============================================================================


def test_conformance_finding_can_be_created() -> None:
    finding = ConformanceFinding(
        finding_type="unexpected_activity",
        activity="cancel",
        expected_activity="approve",
        position=1,
        message="Unexpected activity.",
    )

    assert finding.finding_type == "unexpected_activity"
    assert finding.activity == "cancel"
    assert finding.expected_activity == "approve"
    assert finding.position == 1


def test_conformance_finding_rejects_invalid_type() -> None:
    with pytest.raises(ProcessConformanceError):
        ConformanceFinding(
            finding_type="invalid",
        )


def test_conformance_finding_rejects_negative_position() -> None:
    with pytest.raises(ProcessConformanceError):
        ConformanceFinding(
            finding_type="unexpected_activity",
            position=-1,
        )


# =============================================================================
# Trace Conformance Result
# =============================================================================


def test_trace_conformance_result_can_be_created() -> None:
    result = TraceConformanceResult(
        case_id="case-001",
        score=1.0,
        conformant=True,
    )

    assert result.case_id == "case-001"
    assert result.score == 1.0
    assert result.conformant is True
    assert result.findings == ()


def test_trace_conformance_result_rejects_invalid_score() -> None:
    with pytest.raises(ProcessConformanceError):
        TraceConformanceResult(
            case_id="case-001",
            score=1.1,
            conformant=False,
        )


def test_trace_conformance_result_rejects_invalid_findings() -> None:
    with pytest.raises(ProcessConformanceError):
        TraceConformanceResult(
            case_id="case-001",
            score=0.5,
            conformant=False,
            findings=("invalid",),
        )


# =============================================================================
# Process Conformance Result
# =============================================================================


def test_process_conformance_result_can_be_created() -> None:
    trace_result = TraceConformanceResult(
        case_id="case-001",
        score=1.0,
        conformant=True,
    )

    result = ProcessConformanceResult(
        process_id="proc-001",
        trace_results=(trace_result,),
        average_score=1.0,
        conformant_case_count=1,
        non_conformant_case_count=0,
        finding_counts={},
    )

    assert result.process_id == "proc-001"
    assert result.trace_count == 1
    assert result.average_score == 1.0
    assert result.conformant_case_count == 1
    assert result.non_conformant_case_count == 0


def test_process_conformance_result_rejects_inconsistent_case_counts() -> None:
    trace_result = TraceConformanceResult(
        case_id="case-001",
        score=1.0,
        conformant=True,
    )

    with pytest.raises(ProcessConformanceError):
        ProcessConformanceResult(
            process_id="proc-001",
            trace_results=(trace_result,),
            average_score=1.0,
            conformant_case_count=0,
            non_conformant_case_count=0,
        )


# =============================================================================
# Fully Conformant Trace
# =============================================================================


def test_conformance_accepts_fully_conformant_trace() -> None:
    analyzer = ProcessConformanceAnalyzer()

    result = analyzer.analyse_trace(
        _trace(
            "case-001",
            (
                "receive",
                "approve",
                "complete",
            ),
        ),
        _model(),
    )

    assert result.case_id == "case-001"
    assert result.conformant is True
    assert result.score == 1.0
    assert result.findings == ()


# =============================================================================
# Unexpected Activity
# =============================================================================


def test_conformance_detects_unexpected_activity() -> None:
    analyzer = ProcessConformanceAnalyzer()

    result = analyzer.analyse_trace(
        _trace(
            "case-001",
            (
                "receive",
                "review",
                "approve",
                "complete",
            ),
        ),
        _model(),
    )

    assert result.conformant is False
    assert any(
        finding.finding_type == "unexpected_activity"
        for finding in result.findings
    )


# =============================================================================
# Missing Activity
# =============================================================================


def test_conformance_detects_missing_activity() -> None:
    analyzer = ProcessConformanceAnalyzer()

    result = analyzer.analyse_trace(
        _trace(
            "case-001",
            (
                "receive",
                "complete",
            ),
        ),
        _model(),
    )

    assert result.conformant is False
    assert any(
        finding.finding_type == "missing_activity"
        and finding.expected_activity == "approve"
        for finding in result.findings
    )


# =============================================================================
# Ordering Violation
# =============================================================================


def test_conformance_detects_ordering_violation() -> None:
    analyzer = ProcessConformanceAnalyzer()

    result = analyzer.analyse_trace(
        _trace(
            "case-001",
            (
                "receive",
                "complete",
                "approve",
            ),
        ),
        _model(),
    )

    assert result.conformant is False
    assert any(
        finding.finding_type == "ordering_violation"
        for finding in result.findings
    )


# =============================================================================
# Empty Trace
# =============================================================================


def test_conformance_detects_all_missing_activities_for_empty_trace() -> None:
    analyzer = ProcessConformanceAnalyzer()

    result = analyzer.analyse_trace(
        _trace("case-001", ()),
        _model(),
    )

    assert result.conformant is False
    assert result.score == 0.0
    assert len(result.findings) == 3
    assert all(
        finding.finding_type == "missing_activity"
        for finding in result.findings
    )


# =============================================================================
# Aggregate Analysis
# =============================================================================


def test_conformance_analyse_multiple_traces() -> None:
    analyzer = ProcessConformanceAnalyzer()

    result = analyzer.analyse(
        (
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
                    "complete",
                ),
            ),
        ),
        _model(),
    )

    assert result.process_id == "proc-001"
    assert result.trace_count == 2
    assert result.conformant_case_count == 1
    assert result.non_conformant_case_count == 1
    assert result.average_score < 1.0
    assert result.finding_counts["missing_activity"] >= 1


def test_conformance_analyse_empty_trace_collection() -> None:
    analyzer = ProcessConformanceAnalyzer()

    result = analyzer.analyse(
        (),
        _model(),
    )

    assert result.trace_count == 0
    assert result.average_score == 0.0
    assert result.conformant_case_count == 0
    assert result.non_conformant_case_count == 0
    assert result.finding_counts == {}


# =============================================================================
# Validation
# =============================================================================


def test_analyse_trace_rejects_invalid_trace() -> None:
    analyzer = ProcessConformanceAnalyzer()

    with pytest.raises(ProcessConformanceError):
        analyzer.analyse_trace(
            "invalid",
            _model(),
        )


def test_analyse_trace_rejects_invalid_model() -> None:
    analyzer = ProcessConformanceAnalyzer()

    with pytest.raises(ProcessConformanceError):
        analyzer.analyse_trace(
            _trace(
                "case-001",
                ("receive",),
            ),
            "invalid",
        )


def test_analyse_rejects_invalid_model() -> None:
    analyzer = ProcessConformanceAnalyzer()

    with pytest.raises(ProcessConformanceError):
        analyzer.analyse(
            (),
            "invalid",
        )


def test_analyse_rejects_non_iterable_traces() -> None:
    analyzer = ProcessConformanceAnalyzer()

    with pytest.raises(ProcessConformanceError):
        analyzer.analyse(
            None,
            _model(),
        )


# =============================================================================
# Immutability
# =============================================================================


def test_expected_process_model_is_immutable() -> None:
    model = _model()

    with pytest.raises(AttributeError):
        model.process_id = "changed"  # type: ignore[misc]


def test_conformance_result_is_immutable() -> None:
    result = TraceConformanceResult(
        case_id="case-001",
        score=1.0,
        conformant=True,
    )

    with pytest.raises(AttributeError):
        result.score = 0.5  # type: ignore[misc]


# =============================================================================
# Validation Edge Cases
# =============================================================================


def test_trace_conformance_result_rejects_non_numeric_score() -> None:
    with pytest.raises(ProcessConformanceError):
        TraceConformanceResult(
            case_id="case-001",
            score="1.0",  # type: ignore[arg-type]
            conformant=True,
        )


def test_process_conformance_result_rejects_non_numeric_average_score() -> None:
    trace_result = TraceConformanceResult(
        case_id="case-001",
        score=1.0,
        conformant=True,
    )

    with pytest.raises(ProcessConformanceError):
        ProcessConformanceResult(
            process_id="proc-001",
            trace_results=(trace_result,),
            average_score="1.0",  # type: ignore[arg-type]
            conformant_case_count=1,
            non_conformant_case_count=0,
        )


def test_process_conformance_result_rejects_negative_case_count() -> None:
    trace_result = TraceConformanceResult(
        case_id="case-001",
        score=1.0,
        conformant=True,
    )

    with pytest.raises(ProcessConformanceError):
        ProcessConformanceResult(
            process_id="proc-001",
            trace_results=(trace_result,),
            average_score=1.0,
            conformant_case_count=-1,
            non_conformant_case_count=2,
        )