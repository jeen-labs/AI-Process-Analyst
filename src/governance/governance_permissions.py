"""
AI Process Analyst

Module:
governance.governance_permissions

Purpose:
Provide deterministic permission management for the Governance Platform.

Phase:
Milestone 4 - Governance Platform
Phase 4.3 - Implement Governance Permissions

This module determines whether a subject has an explicit permission
for a requested action on a resource.

It does not implement:

- policy evaluation
- authorization decisions
- auditing
- security controls
- compliance controls
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GovernancePermission:
    """
    Represent an explicit permission granted to a subject.

    Attributes
    ----------
    subject : str
        Identity receiving the permission.

    action : str
        Action the subject is permitted to perform.

    resource : str
        Resource on which the action is permitted.
    """

    subject: str
    action: str
    resource: str


class GovernancePermissions:
    """
    Deterministic permission registry for the Governance Platform.
    """

    def __init__(
        self,
        permissions: set[GovernancePermission] | None = None,
    ) -> None:
        self._permissions = set(permissions or set())

    def grant(
        self,
        permission: GovernancePermission,
    ) -> None:
        """
        Grant an explicit permission.
        """

        self._permissions.add(permission)

    def revoke(
        self,
        permission: GovernancePermission,
    ) -> None:
        """
        Revoke an explicit permission.
        """

        self._permissions.discard(permission)

    def has_permission(
        self,
        subject: str,
        action: str,
        resource: str,
    ) -> bool:
        """
        Return whether the subject has the requested permission.
        """

        return GovernancePermission(
            subject=subject,
            action=action,
            resource=resource,
        ) in self._permissions