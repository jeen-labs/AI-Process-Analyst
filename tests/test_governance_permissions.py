"""
Tests for Governance Permissions.

Phase:
Milestone 4 - Governance Platform
Phase 4.3 - Implement Governance Permissions
"""

from src.governance.governance_permissions import (
    GovernancePermission,
    GovernancePermissions,
)


def test_explicit_permission_is_granted() -> None:
    permission = GovernancePermission(
        subject="analyst",
        action="analyse_process",
        resource="process-001",
    )

    permissions = GovernancePermissions()
    permissions.grant(permission)

    assert (
        permissions.has_permission(
            subject="analyst",
            action="analyse_process",
            resource="process-001",
        )
        is True
    )


def test_missing_permission_is_denied() -> None:
    permissions = GovernancePermissions()

    assert (
        permissions.has_permission(
            subject="analyst",
            action="analyse_process",
            resource="process-001",
        )
        is False
    )


def test_permission_is_resource_specific() -> None:
    permission = GovernancePermission(
        subject="analyst",
        action="analyse_process",
        resource="process-001",
    )

    permissions = GovernancePermissions()
    permissions.grant(permission)

    assert (
        permissions.has_permission(
            subject="analyst",
            action="analyse_process",
            resource="process-002",
        )
        is False
    )


def test_permission_is_subject_specific() -> None:
    permission = GovernancePermission(
        subject="analyst",
        action="analyse_process",
        resource="process-001",
    )

    permissions = GovernancePermissions()
    permissions.grant(permission)

    assert (
        permissions.has_permission(
            subject="administrator",
            action="analyse_process",
            resource="process-001",
        )
        is False
    )


def test_permission_is_action_specific() -> None:
    permission = GovernancePermission(
        subject="analyst",
        action="analyse_process",
        resource="process-001",
    )

    permissions = GovernancePermissions()
    permissions.grant(permission)

    assert (
        permissions.has_permission(
            subject="analyst",
            action="delete_process",
            resource="process-001",
        )
        is False
    )


def test_permission_can_be_revoked() -> None:
    permission = GovernancePermission(
        subject="analyst",
        action="analyse_process",
        resource="process-001",
    )

    permissions = GovernancePermissions()
    permissions.grant(permission)

    permissions.revoke(permission)

    assert (
        permissions.has_permission(
            subject="analyst",
            action="analyse_process",
            resource="process-001",
        )
        is False
    )


def test_revoking_missing_permission_is_safe() -> None:
    permission = GovernancePermission(
        subject="analyst",
        action="analyse_process",
        resource="process-001",
    )

    permissions = GovernancePermissions()

    permissions.revoke(permission)

    assert (
        permissions.has_permission(
            subject="analyst",
            action="analyse_process",
            resource="process-001",
        )
        is False
    )


def test_multiple_permissions_can_be_stored() -> None:
    permissions = GovernancePermissions()

    permissions.grant(
        GovernancePermission(
            subject="analyst",
            action="analyse_process",
            resource="process-001",
        )
    )

    permissions.grant(
        GovernancePermission(
            subject="administrator",
            action="delete_process",
            resource="process-001",
        )
    )

    assert (
        permissions.has_permission(
            subject="analyst",
            action="analyse_process",
            resource="process-001",
        )
        is True
    )

    assert (
        permissions.has_permission(
            subject="administrator",
            action="delete_process",
            resource="process-001",
        )
        is True
    )