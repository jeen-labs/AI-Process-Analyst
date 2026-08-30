"""
Tests:
    Stable public API for Process Intelligence.

Phase:
    Milestone 5 - Process Intelligence
    Phase 5.12 - Stabilise Public Process Intelligence API

Purpose:
    Protect the intentionally supported package-level Process Intelligence
    public API from accidental changes.
"""

from __future__ import annotations

import inspect

import src.process_intelligence as process_intelligence

from src.process_intelligence import (
    DigitalTwinReference,
    ProcessIntelligenceContractError,
    ProcessIntelligenceFinding,
    ProcessIntelligenceRequest,
    ProcessIntelligenceResult,
    ProcessKpiPrediction,
    ProcessObservation,
    ProcessOptimizationRecommendation,
)


# =============================================================================
# Stable Package-Level Public API
# =============================================================================


EXPECTED_PUBLIC_EXPORTS = {
    "DigitalTwinReference",
    "ProcessIntelligenceContractError",
    "ProcessIntelligenceFinding",
    "ProcessIntelligenceRequest",
    "ProcessIntelligenceResult",
    "ProcessKpiPrediction",
    "ProcessObservation",
    "ProcessOptimizationRecommendation",
}


def test_process_intelligence_has_explicit_public_exports() -> None:
    """The package must define an explicit stable public API."""
    assert hasattr(process_intelligence, "__all__")
    assert process_intelligence.__all__


def test_process_intelligence_public_exports_are_exact() -> None:
    """The package-level public export contract must remain unchanged."""
    assert set(process_intelligence.__all__) == EXPECTED_PUBLIC_EXPORTS


def test_process_intelligence_public_exports_are_unique() -> None:
    """The public export list must not contain duplicate names."""
    assert len(process_intelligence.__all__) == len(
        set(process_intelligence.__all__)
    )


def test_process_intelligence_public_exports_are_available() -> None:
    """Every declared public export must exist on the package."""
    for export_name in process_intelligence.__all__:
        assert hasattr(
            process_intelligence,
            export_name,
        ), (
            "Process Intelligence public export is missing: "
            f"{export_name}"
        )


def test_process_intelligence_public_exports_are_directly_importable() -> None:
    """Every supported package-level export must be directly importable."""
    public_objects = {
        "DigitalTwinReference": DigitalTwinReference,
        "ProcessIntelligenceContractError": ProcessIntelligenceContractError,
        "ProcessIntelligenceFinding": ProcessIntelligenceFinding,
        "ProcessIntelligenceRequest": ProcessIntelligenceRequest,
        "ProcessIntelligenceResult": ProcessIntelligenceResult,
        "ProcessKpiPrediction": ProcessKpiPrediction,
        "ProcessObservation": ProcessObservation,
        "ProcessOptimizationRecommendation": ProcessOptimizationRecommendation,
    }

    for name in EXPECTED_PUBLIC_EXPORTS:
        assert public_objects[name] is getattr(
            process_intelligence,
            name,
        )


# =============================================================================
# Public API Object Types
# =============================================================================


def test_process_intelligence_public_contract_types_are_stable() -> None:
    """The stable exports must continue to expose the expected object types."""
    assert inspect.isclass(DigitalTwinReference)
    assert inspect.isclass(ProcessIntelligenceContractError)
    assert inspect.isclass(ProcessIntelligenceFinding)
    assert inspect.isclass(ProcessIntelligenceRequest)
    assert inspect.isclass(ProcessIntelligenceResult)
    assert inspect.isclass(ProcessKpiPrediction)
    assert inspect.isclass(ProcessObservation)
    assert inspect.isclass(ProcessOptimizationRecommendation)


# =============================================================================
# Public API Compatibility
# =============================================================================


def test_process_intelligence_implementation_apis_are_not_package_contract_exports() -> None:
    """
    Implementation capabilities may be available at package level, but they
    must not accidentally become part of the explicitly supported package
    __all__ contract.
    """
    implementation_names = {
        "ProcessMiner",
        "ProcessDiscoverer",
        "ProcessConformanceAnalyzer",
        "ProcessPerformanceAnalyzer",
        "ProcessKpiPredictor",
        "ProcessOptimizer",
        "ProcessDigitalTwin",
    }

    assert implementation_names.isdisjoint(
        set(process_intelligence.__all__)
    )