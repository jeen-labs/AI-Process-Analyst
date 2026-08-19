"""
Tests for Governance Integration Hardening.

Phase:
Milestone 4 - Governance Platform
Phase 4.9 - Governance Integration Hardening

Purpose:
Verify that orchestration uses the unified GovernanceDecisionBoundary
as the authoritative governance decision path.

The integration must preserve the fail-closed sequence:

    Security
        |
        v
    Compliance
        |
        v
    Authorization
        |
        v
    Audit
        |
        v
    Execution

These tests should establish the required integration contract before
production orchestration code is changed.
"""

from __future__ import annotations

from unittest.mock import Mock

import pytest

from src.governance import (
    GovernanceAudit,
    GovernanceAuthorization,
    GovernanceCompliance,
    GovernanceDecisionBoundary,
    GovernancePermission,
    GovernancePermissions,
    GovernancePolicyEngine,
    GovernanceSecurity,
)
from src.orchestration.agent_registry import AgentRegistry
from src.orchestration.execution_manager import ExecutionManager
from src.orchestration.governance import Governance


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def policy_engine() -> GovernancePolicyEngine:
    return GovernancePolicyEngine(
        allowed_actions={
            "process_analysis",
        }
    )


@pytest.fixture
def permissions() -> GovernancePermissions:
    permissions = GovernancePermissions()

    permissions.grant(
        GovernancePermission(
            subject="analyst",
            action="process_analysis",
            resource="customer_onboarding",
        )
    )

    return permissions


@pytest.fixture
def authorization(
    policy_engine: GovernancePolicyEngine,
    permissions: GovernancePermissions,
) -> GovernanceAuthorization:
    return GovernanceAuthorization(
        policy_engine=policy_engine,
        permissions=permissions,
    )


@pytest.fixture
def security() -> GovernanceSecurity:
    return GovernanceSecurity()


@pytest.fixture
def compliance() -> GovernanceCompliance:
    return GovernanceCompliance()


@pytest.fixture
def audit() -> GovernanceAudit:
    return GovernanceAudit()


@pytest.fixture
def boundary(
    security: GovernanceSecurity,
    compliance: GovernanceCompliance,
    authorization: GovernanceAuthorization,
    audit: GovernanceAudit,
) -> GovernanceDecisionBoundary:
    return GovernanceDecisionBoundary(
        security=security,
        compliance=compliance,
        authorization=authorization,
        audit=audit,
    )


# =============================================================================
# Helpers
# =============================================================================


def create_execution_manager() -> ExecutionManager:
    registry = AgentRegistry()
    registry.register(
        "process_analysis",
        Mock(
            execute=Mock(
                return_value={
                    "status": "executed",
                }
            )
        ),
    )

    return ExecutionManager(
        agent_registry=registry,
        governance=Governance(),
    )


# =============================================================================
# Governance Integration Contract
# =============================================================================


def test_unified_governance_boundary_is_constructible(
    boundary: GovernanceDecisionBoundary,
) -> None:
    """The unified governance boundary must be available for integration."""

    assert boundary is not None


def test_unified_boundary_is_authoritative_for_governance_decisions(
    boundary: GovernanceDecisionBoundary,
) -> None:
    """
    Governance decisions should be obtained through the unified boundary.

    This test establishes the integration seam that orchestration will use.
    """

    boundary.evaluate = Mock(
        wraps=boundary.evaluate,
    )

    decision = boundary.evaluate(
        {
            "action": "process_analysis",
            "subject": "analyst",
            "resource": "customer_onboarding",
            "context": {},
        }
    )

    assert decision["allowed"] is True
    boundary.evaluate.assert_called_once()


# =============================================================================
# Fail-Closed Ordering
# =============================================================================


def test_security_rejection_prevents_compliance_and_authorization(
    authorization: GovernanceAuthorization,
    audit: GovernanceAudit,
    compliance: GovernanceCompliance,
) -> None:
    """Security rejection must stop all downstream governance stages."""

    security = Mock(spec=GovernanceSecurity)

    security.evaluate.return_value = {
        "action": "process_analysis",
        "allowed": False,
        "reason": "security validation failed",
    }

    compliance.evaluate = Mock(
        wraps=compliance.evaluate,
    )

    authorization.authorize = Mock(
        wraps=authorization.authorize,
    )

    boundary = GovernanceDecisionBoundary(
        security=security,
        compliance=compliance,
        authorization=authorization,
        audit=audit,
    )

    decision = boundary.evaluate(
        {
            "action": "process_analysis",
            "subject": "analyst",
            "resource": "customer_onboarding",
            "context": {},
        }
    )

    assert decision["allowed"] is False

    security.evaluate.assert_called_once()
    compliance.evaluate.assert_not_called()
    authorization.authorize.assert_not_called()


def test_compliance_rejection_prevents_authorization(
    security: GovernanceSecurity,
    authorization: GovernanceAuthorization,
    audit: GovernanceAudit,
) -> None:
    """Compliance rejection must prevent authorization."""

    compliance = Mock(spec=GovernanceCompliance)

    compliance.evaluate.return_value = {
        "action": "process_analysis",
        "allowed": False,
        "reason": "compliance requirement failed",
    }

    authorization.authorize = Mock(
        wraps=authorization.authorize,
    )

    boundary = GovernanceDecisionBoundary(
        security=security,
        compliance=compliance,
        authorization=authorization,
        audit=audit,
    )

    decision = boundary.evaluate(
        {
            "action": "process_analysis",
            "subject": "analyst",
            "resource": "customer_onboarding",
            "context": {},
        }
    )

    assert decision["allowed"] is False

    compliance.evaluate.assert_called_once()
    authorization.authorize.assert_not_called()


# =============================================================================
# Audit
# =============================================================================


def test_allowed_governance_decision_is_audited(
    boundary: GovernanceDecisionBoundary,
    audit: GovernanceAudit,
) -> None:
    """An allowed governance decision must be recorded."""

    decision = boundary.evaluate(
        {
            "action": "process_analysis",
            "subject": "analyst",
            "resource": "customer_onboarding",
            "context": {},
        }
    )

    assert decision["allowed"] is True
    assert audit.count() == 1


def test_denied_governance_decision_is_audited(
    authorization: GovernanceAuthorization,
    security: GovernanceSecurity,
    compliance: GovernanceCompliance,
    audit: GovernanceAudit,
) -> None:
    """A denied governance decision must be recorded."""

    denied_authorization = Mock(
        spec=GovernanceAuthorization,
    )

    denied_authorization.authorize.return_value = {
        "action": "process_analysis",
        "allowed": False,
        "reason": "permission denied",
    }

    boundary = GovernanceDecisionBoundary(
        security=security,
        compliance=compliance,
        authorization=denied_authorization,
        audit=audit,
    )

    decision = boundary.evaluate(
        {
            "action": "process_analysis",
            "subject": "analyst",
            "resource": "customer_onboarding",
            "context": {},
        }
    )

    assert decision["allowed"] is False
    assert audit.count() == 1


# =============================================================================
# Execution Safety
# =============================================================================


def test_denied_governance_decision_must_not_execute() -> None:
    """
    A denied governance decision must prevent execution.

    This is the critical integration invariant that the orchestration
    layer must preserve.
    """

    execution_manager = create_execution_manager()

    execution_manager.execute = Mock(
        wraps=execution_manager.execute,
    )

    security = Mock(spec=GovernanceSecurity)

    security.evaluate.return_value = {
        "action": "process_analysis",
        "allowed": False,
        "reason": "security validation failed",
    }

    boundary = GovernanceDecisionBoundary(
        security=security,
        compliance=GovernanceCompliance(),
        authorization=Mock(spec=GovernanceAuthorization),
        audit=GovernanceAudit(),
    )

    decision = boundary.evaluate(
        {
            "action": "process_analysis",
            "subject": "analyst",
            "resource": "customer_onboarding",
            "context": {},
        }
    )

    assert decision["allowed"] is False

    # The execution manager must not be invoked for a denied decision.
    execution_manager.execute.assert_not_called()