"""
AI Process Analyst

Package:
governance

Purpose:
Public package exports for the Governance Platform.

Phase:
Milestone 4 - Governance Platform
Phase 4.1 - Define Governance Platform Contracts

This package currently exposes governance contracts only.

Governance implementation components will be introduced incrementally
through subsequent Milestone 4 phases.
"""

# =============================================================================
# Public Governance Contracts
# =============================================================================

from src.governance.governance_contracts import (
    GovernanceDecision,
    GovernanceRequest,
)


# =============================================================================
# Stable Public Exports
# =============================================================================

__all__ = [
    "GovernanceDecision",
    "GovernanceRequest",
]