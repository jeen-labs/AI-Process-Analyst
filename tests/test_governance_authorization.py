"""
Tests for Governance Authorization.

Phase:
Milestone 4 - Governance Platform
Phase 4.4 - Implement Governance Authorization
"""

from src.governance.governance_authorization import (
    GovernanceAuthorization,
)
from src.governance.governance_permissions import (
    GovernancePermission,
    GovernancePermissions,
)
from src.governance.governance_policy_engine import (
    GovernancePolicyEngine,
)


def create_request(
    action: str = "analyse_process",
    subject: str = "analyst",
    resource: str = "process-001",
) -> dict:
    return {
        "action": action,
        "subject": subject,
        "resource": resource,
        "context": {},
    }


def test_authorization_allows_policy_and_permission() -> None:
    policy_engine = GovernancePolicyEngine(
        allowed_actions={"analyse_process"},
    )

    permissions = GovernancePermissions()

    permissions.grant(
        GovernancePermission(
            subject="analyst",
            action="analyse_process",
            resource="process-001",
        )
    )

    authorization = GovernanceAuthorization(
        policy_engine=policy_engine,
        permissions=permissions,
    )

    decision = authorization.authorize(
        create_request(),
    )

    assert decision["action"] == "analyse_process"
    assert decision["allowed"] is True
    assert (
        decision["reason"]
        == "Action is authorized by governance policy and permissions."
    )


def test_authorization_denies_when_policy_denies() -> None:
    policy_engine = GovernancePolicyEngine(
        allowed_actions=set(),
    )

    permissions = GovernancePermissions()

    permissions.grant(
        GovernancePermission(
            subject="analyst",
            action="analyse_process",
            resource="process-001",
        )
    )

    authorization = GovernanceAuthorization(
        policy_engine=policy_engine,
        permissions=permissions,
    )

    decision = authorization.authorize(
        create_request(),
    )

    assert decision["allowed"] is False
    assert (
        decision["reason"]
        == "Action is denied by governance policy."
    )


def test_authorization_denies_when_permission_is_missing() -> None:
    policy_engine = GovernancePolicyEngine(
        allowed_actions={"analyse_process"},
    )

    permissions = GovernancePermissions()

    authorization = GovernanceAuthorization(
        policy_engine=policy_engine,
        permissions=permissions,
    )

    decision = authorization.authorize(
        create_request(),
    )

    assert decision["allowed"] is False
    assert (
        decision["reason"]
        == "Subject does not have the required permission."
    )


def test_authorization_respects_subject_specific_permissions() -> None:
    policy_engine = GovernancePolicyEngine(
        allowed_actions={"analyse_process"},
    )

    permissions = GovernancePermissions()

    permissions.grant(
        GovernancePermission(
            subject="administrator",
            action="analyse_process",
            resource="process-001",
        )
    )

    authorization = GovernanceAuthorization(
        policy_engine=policy_engine,
        permissions=permissions,
    )

    decision = authorization.authorize(
        create_request(subject="analyst"),
    )

    assert decision["allowed"] is False


def test_authorization_respects_resource_specific_permissions() -> None:
    policy_engine = GovernancePolicyEngine(
        allowed_actions={"analyse_process"},
    )

    permissions = GovernancePermissions()

    permissions.grant(
        GovernancePermission(
            subject="analyst",
            action="analyse_process",
            resource="process-001",
        )
    )

    authorization = GovernanceAuthorization(
        policy_engine=policy_engine,
        permissions=permissions,
    )

    decision = authorization.authorize(
        create_request(resource="process-002"),
    )

    assert decision["allowed"] is False


def test_authorization_respects_action_specific_policy() -> None:
    policy_engine = GovernancePolicyEngine(
        allowed_actions={"analyse_process"},
    )

    permissions = GovernancePermissions()

    permissions.grant(
        GovernancePermission(
            subject="analyst",
            action="delete_process",
            resource="process-001",
        )
    )

    authorization = GovernanceAuthorization(
        policy_engine=policy_engine,
        permissions=permissions,
    )

    decision = authorization.authorize(
        create_request(action="delete_process"),
    )

    assert decision["allowed"] is False


def test_is_authorized_returns_true_for_authorized_request() -> None:
    policy_engine = GovernancePolicyEngine(
        allowed_actions={"analyse_process"},
    )

    permissions = GovernancePermissions()

    permissions.grant(
        GovernancePermission(
            subject="analyst",
            action="analyse_process",
            resource="process-001",
        )
    )

    authorization = GovernanceAuthorization(
        policy_engine=policy_engine,
        permissions=permissions,
    )

    assert (
        authorization.is_authorized(
            create_request(),
        )
        is True
    )


def test_is_authorized_returns_false_for_denied_request() -> None:
    policy_engine = GovernancePolicyEngine(
        allowed_actions=set(),
    )

    permissions = GovernancePermissions()

    authorization = GovernanceAuthorization(
        policy_engine=policy_engine,
        permissions=permissions,
    )

    assert (
        authorization.is_authorized(
            create_request(),
        )
        is False
    )