"""
AI Process Analyst

Package:
governance

Purpose:
Public package exports for the Governance Platform.

Phase:
Milestone 4 - Governance Platform
Phase 4.2 - Implement Governance Policy Engine

This package exposes the stable public contracts and policy engine
for the Governance Platform.

Additional governance components will be introduced incrementally
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
# Governance Policy Engine
# =============================================================================

from src.governance.governance_policy_engine import (
    GovernancePolicyEngine,
)

# =============================================================================
# Stable Public Exports
# =============================================================================

__all__ = [
    "GovernanceDecision",
    "GovernanceRequest",
    "GovernancePolicyEngine",
]