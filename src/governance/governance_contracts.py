"""
AI Process Analyst

Module:
governance.governance_contracts

Purpose:
Define stable structural contracts used by the Governance Platform.

Phase:
Milestone 4 - Governance Platform
Phase 4.1 - Define Governance Platform Contracts

This module defines structural contracts only.

It does not implement:
- policy evaluation
- permission management
- authorization
- auditing
- security controls
- compliance controls

Those responsibilities belong to later Governance Platform components.
"""

# =============================================================================
# Standard Library Imports
# =============================================================================

from typing import Any, TypedDict


# =============================================================================
# Governance Decision Contract
# =============================================================================

class GovernanceDecision(TypedDict):
    """
    Stable structural contract for a governance decision.

    Fields
    ------
    action : str
        Action being evaluated.

    allowed : bool
        Whether the action is permitted by the governance platform.

    reason : str
        Human-readable explanation of the governance decision.
    """

    action: str
    allowed: bool
    reason: str


# =============================================================================
# Governance Request Contract
# =============================================================================

class GovernanceRequest(TypedDict):
    """
    Stable structural contract for a governance evaluation request.

    Fields
    ------
    action : str
        Action being evaluated.

    subject : str
        Identity or principal requesting the action.

    resource : str
        Resource against which the action is being evaluated.

    context : dict[str, Any]
        Additional contextual information used by future governance
        components.
    """

    action: str
    subject: str
    resource: str
    context: dict[str, Any]