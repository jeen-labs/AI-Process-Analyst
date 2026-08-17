"""
Tests for the Unified Governance Decision Boundary.

Phase:
Milestone 4 - Governance Platform
Phase 4.8 - Unified Governance Decision Boundary
"""

import pytest

from src.governance.governance_audit import GovernanceAudit
from src.governance.governance_authorization import GovernanceAuthorization
from src.governance.governance_compliance import GovernanceCompliance
from src.governance.governance_contracts import GovernanceRequest
from src.governance.governance_decision_boundary import (
    GovernanceDecisionBoundary,
    GovernanceDecisionBoundaryError,
)
from src.governance.governance_permissions import (
    GovernancePermission,
    GovernancePermissions,
)
from src.governance.governance_policy_engine import GovernancePolicyEngine
from src.governance.governance_security import GovernanceSecurity


def create_request(
    action: str = "process_analysis",
    subject: str = "analyst",
    resource: str = "customer_onboarding",
) -> GovernanceRequest:
    return GovernanceRequest(
        action=action,
        subject=subject,
        resource=resource,
        context={},
    )


def create_boundary() -> GovernanceDecisionBoundary:
    policy_engine = GovernancePolicyEngine(
        allowed_actions={"process_analysis"}
    )

    permissions = GovernancePermissions()

    permissions.grant(
        GovernancePermission(
            subject="analyst",
            action="process_analysis",
            resource="customer_onboarding",
        )
    )

    authorization = GovernanceAuthorization(
        policy_engine=policy_engine,
        permissions=permissions,
    )

    return GovernanceDecisionBoundary(
        security=GovernanceSecurity(),
        compliance=GovernanceCompliance(),
        authorization=authorization,
        audit=GovernanceAudit(),
    )


def test_boundary_can_be_constructed() -> None:
    boundary = create_boundary()

    assert boundary is not None


def test_boundary_rejects_missing_security() -> None:
    with pytest.raises(GovernanceDecisionBoundaryError):
        GovernanceDecisionBoundary(
            security=None,
            compliance=GovernanceCompliance(),
            authorization=None,
            audit=GovernanceAudit(),
        )


def test_boundary_rejects_missing_compliance() -> None:
    with pytest.raises(GovernanceDecisionBoundaryError):
        GovernanceDecisionBoundary(
            security=GovernanceSecurity(),
            compliance=None,
            authorization=None,
            audit=GovernanceAudit(),
        )


def test_boundary_rejects_missing_authorization() -> None:
    with pytest.raises(GovernanceDecisionBoundaryError):
        GovernanceDecisionBoundary(
            security=GovernanceSecurity(),
            compliance=GovernanceCompliance(),
            authorization=None,
            audit=GovernanceAudit(),
        )


def test_boundary_rejects_missing_audit() -> None:
    with pytest.raises(GovernanceDecisionBoundaryError):
        GovernanceDecisionBoundary(
            security=GovernanceSecurity(),
            compliance=GovernanceCompliance(),
            authorization=None,
            audit=None,
        )


def test_valid_request_reaches_authorization() -> None:
    boundary = create_boundary()

    decision = boundary.evaluate(
        create_request()
    )

    assert decision["action"] == "process_analysis"
    assert decision["allowed"] is True


def test_denied_action_does_not_pass_governance_boundary() -> None:
    boundary = create_boundary()

    decision = boundary.evaluate(
        create_request(action="unknown_action")
    )

    assert decision["allowed"] is False


def test_denied_decision_is_audited() -> None:
    policy_engine = GovernancePolicyEngine(
        allowed_actions=set()
    )

    permissions = GovernancePermissions()

    authorization = GovernanceAuthorization(
        policy_engine=policy_engine,
        permissions=permissions,
    )

    audit = GovernanceAudit()

    boundary = GovernanceDecisionBoundary(
        security=GovernanceSecurity(),
        compliance=GovernanceCompliance(),
        authorization=authorization,
        audit=audit,
    )

    decision = boundary.evaluate(
        create_request()
    )

    assert decision["allowed"] is False
    assert len(audit.entries()) == 1


def test_allowed_decision_is_audited() -> None:
    boundary = create_boundary()

    decision = boundary.evaluate(
        create_request()
    )

    assert decision["allowed"] is True