"""
Tests for Governance Audit.

Phase:
Milestone 4 - Governance Platform
Phase 4.5 - Implement Governance Audit
"""

from src.governance.governance_audit import (
    GovernanceAudit,
    GovernanceAuditEntry,
)


def create_decision(
    action: str = "analyse_process",
    allowed: bool = True,
    reason: str = "Action is explicitly allowed by governance policy.",
) -> dict:
    """
    Create a test governance decision.
    """

    return {
        "action": action,
        "allowed": allowed,
        "reason": reason,
    }


def test_audit_records_governance_decision() -> None:
    audit = GovernanceAudit()

    entry = audit.record(
        create_decision(),
    )

    assert isinstance(entry, GovernanceAuditEntry)
    assert entry.action == "analyse_process"
    assert entry.allowed is True
    assert (
        entry.reason
        == "Action is explicitly allowed by governance policy."
    )


def test_audit_records_denied_decision() -> None:
    audit = GovernanceAudit()

    entry = audit.record(
        create_decision(
            action="delete_process",
            allowed=False,
            reason="Action is not allowed by governance policy.",
        ),
    )

    assert entry.action == "delete_process"
    assert entry.allowed is False
    assert (
        entry.reason
        == "Action is not allowed by governance policy."
    )


def test_audit_entries_preserve_insertion_order() -> None:
    audit = GovernanceAudit()

    audit.record(
        create_decision(
            action="first_action",
        ),
    )

    audit.record(
        create_decision(
            action="second_action",
        ),
    )

    entries = audit.entries()

    assert len(entries) == 2
    assert entries[0].action == "first_action"
    assert entries[1].action == "second_action"


def test_audit_entries_are_read_only_from_caller_perspective() -> None:
    audit = GovernanceAudit()

    audit.record(
        create_decision(),
    )

    entries = audit.entries()

    assert isinstance(entries, tuple)
    assert len(entries) == 1


def test_audit_count_returns_number_of_entries() -> None:
    audit = GovernanceAudit()

    assert audit.count() == 0

    audit.record(
        create_decision(),
    )

    assert audit.count() == 1

    audit.record(
        create_decision(
            action="another_action",
        ),
    )

    assert audit.count() == 2


def test_audit_clear_removes_all_entries() -> None:
    audit = GovernanceAudit()

    audit.record(
        create_decision(),
    )

    audit.record(
        create_decision(
            action="another_action",
        ),
    )

    assert audit.count() == 2

    audit.clear()

    assert audit.count() == 0
    assert audit.entries() == ()


def test_empty_audit_has_no_entries() -> None:
    audit = GovernanceAudit()

    assert audit.entries() == ()
    assert audit.count() == 0