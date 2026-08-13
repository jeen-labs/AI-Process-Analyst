"""
AI Process Analyst

Module:
governance.governance_audit

Purpose:
Provide deterministic audit recording for the Governance Platform.

Phase:
Milestone 4 - Governance Platform
Phase 4.5 - Implement Governance Audit

This module records governance decisions in an in-memory audit trail.

It does not implement:

- persistent audit storage
- database integration
- external logging
- authentication
- security controls
- compliance controls
"""

from __future__ import annotations

from dataclasses import dataclass

from src.governance.governance_contracts import GovernanceDecision


@dataclass(frozen=True)
class GovernanceAuditEntry:
    """
    Represent one recorded governance decision.

    Attributes
    ----------
    action : str
        Action evaluated by the governance platform.

    allowed : bool
        Whether the action was permitted.

    reason : str
        Explanation associated with the governance decision.
    """

    action: str
    allowed: bool
    reason: str


class GovernanceAudit:
    """
    Deterministic in-memory audit trail for governance decisions.
    """

    def __init__(self) -> None:
        self._entries: list[GovernanceAuditEntry] = []

    def record(
        self,
        decision: GovernanceDecision,
    ) -> GovernanceAuditEntry:
        """
        Record a governance decision and return the created audit entry.
        """

        entry = GovernanceAuditEntry(
            action=decision["action"],
            allowed=decision["allowed"],
            reason=decision["reason"],
        )

        self._entries.append(entry)

        return entry

    def entries(self) -> tuple[GovernanceAuditEntry, ...]:
        """
        Return all recorded audit entries in insertion order.

        A tuple is returned so callers cannot modify the internal
        audit collection directly.
        """

        return tuple(self._entries)

    def count(self) -> int:
        """
        Return the number of recorded audit entries.
        """

        return len(self._entries)

    def clear(self) -> None:
        """
        Remove all recorded audit entries.
        """

        self._entries.clear()