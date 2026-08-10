"""
AI Process Analyst

Module:
tests.test_governance

Purpose:
Test the Governance component of the enterprise orchestration layer.

Phase:
Milestone 3 - Enterprise AI Orchestration Layer
Phase 3.8 - Governance / Policy Boundary
"""

import pytest
from src.orchestration.governance import Governance, GovernanceError


def test_governance_initialises_with_default_policy():
    """Governance should initialise with the default policy."""
    governance = Governance()
    assert governance.list_allowed_actions() == [
        "process_analysis"
    ]


def test_governance_initialises_with_custom_policy():
    """Governance should accept a custom list of allowed actions."""
    governance = Governance(
        allowed_actions=[
            "process_analysis",
            "document_analysis",
        ]
    )
    assert governance.list_allowed_actions() == [
        "document_analysis",
        "process_analysis",
    ]


def test_governance_allows_registered_action():
    """An allowed action should return True."""
    governance = Governance()
    assert governance.is_allowed("process_analysis") is True


def test_governance_denies_unknown_action():
    """An unknown action should return False."""
    governance = Governance()
    assert governance.is_allowed("unknown_action") is False


def test_governance_normalises_action_whitespace():
    """Leading and trailing whitespace should be ignored."""
    governance = Governance()
    assert governance.is_allowed("  process_analysis  ") is True


def test_governance_rejects_non_string_action():
    """Non-string actions should not be considered allowed."""
    governance = Governance()
    assert governance.is_allowed(None) is False


def test_governance_rejects_empty_action():
    """An empty action should not be considered allowed."""
    governance = Governance()
    assert governance.is_allowed("") is False


def test_governance_rejects_whitespace_action():
    """A whitespace-only action should not be considered allowed."""
    governance = Governance()
    assert governance.is_allowed("   ") is False


def test_governance_evaluates_allowed_action():
    """An allowed action should produce an allowed decision."""
    governance = Governance()
    result = governance.evaluate("process_analysis")
    assert result == {
        "action": "process_analysis",
        "allowed": True,
        "reason": "Action is permitted by the current policy.",
    }


def test_governance_evaluates_denied_action():
    """A disallowed action should produce a denied decision."""
    governance = Governance()
    result = governance.evaluate("unknown_action")
    assert result == {
        "action": "unknown_action",
        "allowed": False,
        "reason": "Action is not permitted by the current policy.",
    }


def test_governance_evaluate_normalises_action():
    """Evaluation should normalise surrounding whitespace."""
    governance = Governance()
    result = governance.evaluate("  process_analysis  ")
    assert result["action"] == "process_analysis"
    assert result["allowed"] is True


def test_governance_evaluate_rejects_non_string_action():
    """Evaluation should reject a non-string action."""
    governance = Governance()
    with pytest.raises(GovernanceError):
        governance.evaluate(None)


def test_governance_evaluate_rejects_empty_action():
    """Evaluation should reject an empty action."""
    governance = Governance()
    with pytest.raises(GovernanceError):
        governance.evaluate("")


def test_governance_evaluate_rejects_whitespace_action():
    """Evaluation should reject a whitespace-only action."""
    governance = Governance()
    with pytest.raises(GovernanceError):
        governance.evaluate("   ")


def test_governance_rejects_invalid_allowed_actions_type():
    """Governance should reject a non-list policy."""
    with pytest.raises(GovernanceError):
        Governance(allowed_actions="process_analysis")


def test_governance_rejects_non_string_allowed_action():
    """Governance should reject non-string action names."""
    with pytest.raises(GovernanceError):
        Governance(
            allowed_actions=[
                "process_analysis",
                None,
            ]
        )


def test_governance_rejects_empty_allowed_action():
    """Governance should reject an empty allowed action name."""
    with pytest.raises(GovernanceError):
        Governance(
            allowed_actions=[
                "process_analysis",
                "",
            ]
        )


def test_governance_rejects_whitespace_allowed_action():
    """Governance should reject whitespace-only action names."""
    with pytest.raises(GovernanceError):
        Governance(
            allowed_actions=[
                "process_analysis",
                "   ",
            ]
        )


def test_governance_removes_duplicate_actions():
    """Duplicate policy entries should be represented only once."""
    governance = Governance(
        allowed_actions=[
            "process_analysis",
            "process_analysis",
        ]
    )
    assert governance.list_allowed_actions() == [
        "process_analysis"
    ]


def test_governance_returns_copy_of_allowed_actions():
    """Listing actions should not expose the internal policy list."""
    governance = Governance()
    actions = governance.list_allowed_actions()
    actions.append("new_action")
    assert governance.list_allowed_actions() == [
        "process_analysis"
    ]


def test_governance_is_deterministic():
    """Repeated evaluations should return the same decision."""
    governance = Governance()
    first = governance.evaluate("process_analysis")
    second = governance.evaluate("process_analysis")
    assert first == second


def test_governance_supports_multiple_allowed_actions():
    """Governance should evaluate multiple configured actions."""
    governance = Governance(
        allowed_actions=[
            "process_analysis",
            "document_analysis",
            "report_generation",
        ]
    )
    assert governance.is_allowed("process_analysis") is True
    assert governance.is_allowed("document_analysis") is True
    assert governance.is_allowed("report_generation") is True
    assert governance.is_allowed("unknown_action") is False