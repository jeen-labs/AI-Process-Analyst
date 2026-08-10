"""
AI Process Analyst

Package:
orchestration

Purpose:
Public package exports for the orchestration layer.

Phase:
Milestone 3 - Enterprise AI Orchestration Layer
Phase 3.11 - Stabilise Orchestration Contracts and Integration

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
# Stable Public Exports
# =============================================================================

__all__ = [
    "OrchestrationEngine",
    "OrchestrationEngineError",
    "OrchestrationResult",
]