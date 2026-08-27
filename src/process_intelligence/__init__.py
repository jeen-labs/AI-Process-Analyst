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

Phase:
    Phase 5.1 - Define Process Intelligence Contracts

This module exposes the stable public Process Intelligence API.

Implementation details should remain inside the corresponding internal
modules. Consumers should import Process Intelligence contracts from this
package rather than depending on internal module paths.
===============================================================================
"""

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