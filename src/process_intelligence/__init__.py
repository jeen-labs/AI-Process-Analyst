"""
===============================================================================
AI Process Analyst
===============================================================================

Package:
    process_intelligence

Purpose:
    Public API for the Process Intelligence subsystem.

Milestone:
    Milestone 5 - Process Intelligence

Phases:
    Phase 5.1 - Define Process Intelligence Contracts
    Phase 5.2 - Process Mining
    Phase 5.3 - Process Discovery
    Phase 5.4 - Process Conformance Analysis
    Phase 5.5 - Process Performance Analysis

This module exposes the stable public Process Intelligence API.

Implementation details should remain inside the corresponding internal
modules. Consumers should import Process Intelligence functionality from
this package rather than depending on internal module paths.
===============================================================================
"""

# =============================================================================
# Phase 5.1 - Process Intelligence Contracts
# =============================================================================

from .process_intelligence_contracts import (
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
# Phase 5.2 - Process Mining
# =============================================================================

from .process_mining import (
    ProcessMiner,
    ProcessMiningError,
    ProcessMiningResult,
)


# =============================================================================
# Phase 5.3 - Process Discovery
# =============================================================================

from .process_discovery import (
    ProcessDiscoveryError,
    ProcessDiscoveryResult,
    ProcessDiscoverer,
)


# =============================================================================
# Phase 5.4 - Process Conformance Analysis
# =============================================================================

from .process_conformance import (
    ProcessConformanceAnalyzer,
    ProcessConformanceError,
    ProcessConformanceResult,
)


# =============================================================================
# Phase 5.5 - Process Performance Analysis
# =============================================================================

from .process_performance import (
    ProcessPerformanceAnalyzer,
    ProcessPerformanceError,
    ProcessPerformanceResult,
)


# =============================================================================
# Public API
# =============================================================================
#
# IMPORTANT:
# The package's explicit __all__ contract is currently defined by the
# Process Intelligence contract tests.
#
# The Phase 5.2 - 5.5 classes remain imported above and are therefore
# available through explicit imports, for example:
#
#     from src.process_intelligence import ProcessPerformanceAnalyzer
#
# They are intentionally not included in __all__ because the public export
# contract requires these eight Phase 5.1 names exactly.
# =============================================================================

__all__ = [
    "DigitalTwinReference",
    "ProcessIntelligenceContractError",
    "ProcessIntelligenceFinding",
    "ProcessIntelligenceRequest",
    "ProcessIntelligenceResult",
    "ProcessKpiPrediction",
    "ProcessObservation",
    "ProcessOptimizationRecommendation",
]