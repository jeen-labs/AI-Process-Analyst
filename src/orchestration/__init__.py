"""
AI Process Analyst

Package:
orchestration

Purpose:
Public package exports for the orchestration layer.

Phase:
Milestone 3 - Enterprise AI Orchestration Layer
Phase 3.11 - Stabilise Orchestration Contracts and Integration

Phase 5.9:
Process Intelligence / Orchestration Integration

This module exposes the stable public orchestration API.

Internal implementation modules should not be required by callers that use
the public orchestration interface.
"""

# =============================================================================
# Public Orchestration Contracts
# =============================================================================

from src.orchestration.contracts import OrchestrationResult


# =============================================================================
# Public Orchestration Engine
# =============================================================================

from src.orchestration.orchestration_engine import (
    OrchestrationEngine,
    OrchestrationEngineError,
)


# =============================================================================
# Process Intelligence Integration
# =============================================================================
#
# Phase 5.9 integration API.
#
# These objects remain directly importable from src.orchestration, while the
# historical __all__ contract below remains unchanged for backward
# compatibility.
# =============================================================================

from src.orchestration.process_intelligence_integration import (
    ProcessIntelligenceIntegration,
    ProcessIntelligenceOrchestrationError,
    ProcessIntelligenceOrchestrationResult,
    integrate_process_intelligence,
)


# =============================================================================
# Stable Public Exports
# =============================================================================
#
# IMPORTANT:
# Keep this list unchanged.
#
# Existing callers and the orchestration public API regression tests expect
# the original Phase 3.11 public export contract.
#
# Phase 5.9 integration objects are intentionally imported above but are not
# added to __all__, preserving backward compatibility.
# =============================================================================

__all__ = [
    "OrchestrationEngine",
    "OrchestrationEngineError",
    "OrchestrationResult",
]