"""
AI Process Analyst

Module:
orchestration.contracts

Purpose:
Define stable structural contracts used by the orchestration layer.

Phase:
Milestone 3 - Enterprise AI Orchestration Layer
Phase 3.11 - Stabilise Orchestration Contracts and Integration

This module defines the result contract returned by OrchestrationEngine.

The contract is intentionally structural. It does not implement orchestration
logic, planning, governance, agent execution, or error handling.
"""

# =============================================================================
# Standard Library Imports
# =============================================================================

from typing import Any, TypedDict


# =============================================================================
# Orchestration Result Contract
# =============================================================================

class OrchestrationResult(TypedDict):
    """
    Stable successful-result contract returned by OrchestrationEngine.

    Fields
    ------
    request : str
        Normalised orchestration request.

    plan : dict[str, Any]
        Planner-generated execution plan.

    action : str
        Normalised action selected from the execution plan.

    governance : dict[str, Any]
        Governance decision associated with the selected action.

    result : Any
        Result returned by the ExecutionManager.
    """

    request: str
    plan: dict[str, Any]
    action: str
    governance: dict[str, Any]
    result: Any
