"""
AI Process Analyst

Package:
governance

Purpose:
Public package exports for the Governance Platform.

Phase:
Milestone 4 - Governance Platform
Phase 4.7 - Implement Governance Compliance

This package exposes the stable public contracts, policy engine,
permission management, authorization, audit, security, and compliance
components for the Governance Platform.

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
# Governance Permissions
# =============================================================================

from src.governance.governance_permissions import (
    GovernancePermission,
    GovernancePermissions,
)

# =============================================================================
# Governance Authorization
# =============================================================================

from src.governance.governance_authorization import (
    GovernanceAuthorization,
)

# =============================================================================
# Governance Audit
# =============================================================================

from src.governance.governance_audit import (
    GovernanceAudit,
    GovernanceAuditEntry,
)

# =============================================================================
# Governance Compliance
# =============================================================================

from src.governance.governance_compliance import (
    GovernanceCompliance,
    GovernanceComplianceError,
)

# =============================================================================
# Governance Security
# =============================================================================

from src.governance.governance_security import (
    GovernanceSecurity,
    GovernanceSecurityError,
)

# =============================================================================
# Governance Decision Boundary
# =============================================================================

from src.governance.governance_decision_boundary import (
    GovernanceDecisionBoundary,
    GovernanceDecisionBoundaryError,
)

# =============================================================================
# Stable Public Exports
# =============================================================================

__all__ = [
    "GovernanceDecision",
    "GovernanceRequest",
    "GovernancePolicyEngine",
    "GovernancePermission",
    "GovernancePermissions",
    "GovernanceAuthorization",
    "GovernanceAudit",
    "GovernanceAuditEntry",
    "GovernanceCompliance",
    "GovernanceComplianceError",
    "GovernanceSecurity",
    "GovernanceSecurityError",
    "GovernanceDecisionBoundary",
    "GovernanceDecisionBoundaryError",
]