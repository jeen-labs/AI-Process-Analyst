"""
Tests for the Governance Platform End-to-End Boundary.

Phase:
Milestone 4 - Governance Platform
Phase 4.9 - Governance Integration Hardening

Purpose:
Verify that the Governance Platform components work together through
the public GovernanceDecisionBoundary without bypassing individual
governance responsibilities.

These tests specifically verify fail-closed pipeline behavior:

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

An earlier governance stage must prevent later stages from being
executed when that stage rejects the request.
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


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def policy_engine() -> GovernancePolicyEngine:
    """Create the governance policy engine used by integration tests."""

    return GovernancePolicyEngine(
        allowed_actions=[
            "process_analysis",
            "document_analysis",
            "report_generation",
        ]
    )


@pytest.fixture
def permissions() -> GovernancePermissions:
    """Create permissions for the approved integration action."""

    permissions = GovernancePermissions()

    permissions.grant(
        GovernancePermission(
            subject="test-user",
            action="process_analysis",
            resource="test-document",
        )
    )

    return permissions


@pytest.fixture
def authorization(
    policy_engine: GovernancePolicyEngine,
    permissions: GovernancePermissions,
) -> GovernanceAuthorization:
    """Create the authorization component."""

    return GovernanceAuthorization(
        policy_engine=policy_engine,
        permissions=permissions,
    )


@pytest.fixture
def audit() -> GovernanceAudit:
    """Create a fresh governance audit store."""

    return GovernanceAudit()


@pytest.fixture
def security() -> GovernanceSecurity:
    """Create a fresh governance security boundary."""

    return GovernanceSecurity()


@pytest.fixture
def compliance() -> GovernanceCompliance:
    """Create a fresh governance compliance boundary."""

    return GovernanceCompliance()


@pytest.fixture
def boundary(
    authorization: GovernanceAuthorization,
    audit: GovernanceAudit,
    security: GovernanceSecurity,
    compliance: GovernanceCompliance,
) -> GovernanceDecisionBoundary:
    """Create the complete unified governance boundary."""

    return GovernanceDecisionBoundary(
        authorization=authorization,
        audit=audit,
        security=security,
        compliance=compliance,
    )


# =============================================================================
# Helpers
# =============================================================================


def valid_request(
    *,
    subject: str = "test-user",
    action: str = "process_analysis",
    resource: str = "test-document",
) -> dict:
    """
    Return a structurally valid governance request.

    The context field is required by GovernanceSecurity.
    """

    return {
        "subject": subject,
        "action": action,
        "resource": resource,
        "context": {},
    }


# =============================================================================
# Public API
# =============================================================================


def test_governance_end_to_end_components_are_publicly_available() -> None:
    """
    The complete Governance Platform should expose the components required
    for end-to-end integration.
    """

    assert GovernancePolicyEngine is not None
    assert GovernancePermissions is not None
    assert GovernanceAuthorization is not None
    assert GovernanceAudit is not None
    assert GovernanceSecurity is not None
    assert GovernanceCompliance is not None
    assert GovernanceDecisionBoundary is not None


# =============================================================================
# Decision Boundary Construction
# =============================================================================


def test_governance_decision_boundary_can_be_constructed(
    authorization: GovernanceAuthorization,
    audit: GovernanceAudit,
    security: GovernanceSecurity,
    compliance: GovernanceCompliance,
) -> None:
    """
    The GovernanceDecisionBoundary should be constructible from the
    Governance Platform components.
    """

    boundary = GovernanceDecisionBoundary(
        authorization=authorization,
        audit=audit,
        security=security,
        compliance=compliance,
    )

    assert boundary is not None


# =============================================================================
# End-to-End Authorization
# =============================================================================


def test_governance_end_to_end_allows_authorized_action(
    boundary: GovernanceDecisionBoundary,
) -> None:
    """
    An action satisfying policy, permissions, security, compliance,
    and authorization requirements should produce an allowed decision.
    """

    decision = boundary.evaluate(
        valid_request()
    )

    assert decision["allowed"] is True


# =============================================================================
# End-to-End Rejection
# =============================================================================


def test_governance_end_to_end_denies_unauthorized_action(
    boundary: GovernanceDecisionBoundary,
) -> None:
    """
    An action that is not authorized must be rejected by the complete
    Governance Platform.
    """

    decision = boundary.evaluate(
        valid_request(
            action="unknown_action"
        )
    )

    assert decision["allowed"] is False


# =============================================================================
# Governance Boundary Integrity
# =============================================================================


def test_governance_end_to_end_does_not_bypass_authorization(
    boundary: GovernanceDecisionBoundary,
) -> None:
    """
    The end-to-end boundary must rely on GovernanceAuthorization rather
    than independently granting access.
    """

    decision = boundary.evaluate(
        valid_request(
            action="report_generation"
        )
    )

    assert decision["allowed"] is False


# =============================================================================
# Phase 4.9 - Integration Hardening
# =============================================================================


def test_security_rejection_stops_downstream_governance_stages(
    authorization: GovernanceAuthorization,
    audit: GovernanceAudit,
    compliance: GovernanceCompliance,
) -> None:
    """
    Security rejection must prevent compliance and authorization from
    being reached.
    """

    security = Mock(
        spec=GovernanceSecurity
    )

    security.evaluate.return_value = {
        "action": "process_analysis",
        "allowed": False,
        "reason": "security validation failed",
    }

    compliance.evaluate = Mock(
        wraps=compliance.evaluate
    )

    authorization.authorize = Mock(
        wraps=authorization.authorize
    )

    boundary = GovernanceDecisionBoundary(
        security=security,
        compliance=compliance,
        authorization=authorization,
        audit=audit,
    )

    request = valid_request()

    decision = boundary.evaluate(request)

    assert decision["allowed"] is False

    security.evaluate.assert_called_once_with(
        request
    )

    compliance.evaluate.assert_not_called()

    authorization.authorize.assert_not_called()

    assert len(audit.entries()) == 1


def test_compliance_rejection_stops_authorization(
    authorization: GovernanceAuthorization,
    audit: GovernanceAudit,
    security: GovernanceSecurity,
) -> None:
    """
    Compliance rejection must prevent authorization from being reached.
    """

    compliance = Mock(
        spec=GovernanceCompliance
    )

    compliance.evaluate.return_value = {
        "action": "process_analysis",
        "allowed": False,
        "reason": "compliance requirement failed",
    }

    authorization.authorize = Mock(
        wraps=authorization.authorize
    )

    boundary = GovernanceDecisionBoundary(
        security=security,
        compliance=compliance,
        authorization=authorization,
        audit=audit,
    )

    request = valid_request()

    decision = boundary.evaluate(request)

    assert decision["allowed"] is False

    compliance.evaluate.assert_called_once_with(
        request
    )

    authorization.authorize.assert_not_called()

    assert len(audit.entries()) == 1


def test_authorization_rejection_is_audited(
    audit: GovernanceAudit,
    security: GovernanceSecurity,
    compliance: GovernanceCompliance,
) -> None:
    """
    When security and compliance accept but authorization rejects,
    the rejection must be recorded in the audit store.
    """

    authorization = Mock(
        spec=GovernanceAuthorization
    )

    authorization.authorize.return_value = {
        "action": "process_analysis",
        "allowed": False,
        "reason": "permission denied",
    }

    boundary = GovernanceDecisionBoundary(
        security=security,
        compliance=compliance,
        authorization=authorization,
        audit=audit,
    )

    request = valid_request()

    decision = boundary.evaluate(request)

    assert decision["allowed"] is False

    authorization.authorize.assert_called_once_with(
        request
    )

    assert len(audit.entries()) == 1


def test_authorized_request_completes_full_governance_pipeline(
    authorization: GovernanceAuthorization,
    audit: GovernanceAudit,
    security: GovernanceSecurity,
    compliance: GovernanceCompliance,
) -> None:
    """
    A valid and authorized request must pass through security,
    compliance, authorization, and audit.
    """

    security.evaluate = Mock(
        wraps=security.evaluate
    )

    compliance.evaluate = Mock(
        wraps=compliance.evaluate
    )

    authorization.authorize = Mock(
        wraps=authorization.authorize
    )

    boundary = GovernanceDecisionBoundary(
        security=security,
        compliance=compliance,
        authorization=authorization,
        audit=audit,
    )

    request = valid_request()

    decision = boundary.evaluate(request)

    assert decision["allowed"] is True

    security.evaluate.assert_called_once_with(
        request
    )

    compliance.evaluate.assert_called_once_with(
        request
    )

    authorization.authorize.assert_called_once_with(
        request
    )

    assert len(audit.entries()) == 1