"""
Tests for the Governance Policy Engine.

Phase:
Milestone 4 - Governance Platform
Phase 4.2 - Implement Governance Policy Engine
"""

from src.governance.governance_policy_engine import (
    GovernancePolicyEngine,
)


def create_request(action: str) -> dict:
    return {
        "action": action,
        "subject": "test-user",
        "resource": "test-resource",
        "context": {},
    }


def test_allowed_action_returns_allowed_decision() -> None:
    engine = GovernancePolicyEngine(
        allowed_actions={"analyse_process"},
    )

    decision = engine.evaluate(
        create_request("analyse_process"),
    )

    assert decision["action"] == "analyse_process"
    assert decision["allowed"] is True
    assert (
        decision["reason"]
        == "Action is explicitly allowed by governance policy."
    )


def test_disallowed_action_returns_denied_decision() -> None:
    engine = GovernancePolicyEngine(
        allowed_actions={"analyse_process"},
    )

    decision = engine.evaluate(
        create_request("delete_process"),
    )

    assert decision["action"] == "delete_process"
    assert decision["allowed"] is False
    assert (
        decision["reason"]
        == "Action is not allowed by governance policy."
    )


def test_is_allowed_returns_true_for_allowed_action() -> None:
    engine = GovernancePolicyEngine(
        allowed_actions={"analyse_process"},
    )

    assert (
        engine.is_allowed(
            create_request("analyse_process"),
        )
        is True
    )


def test_is_allowed_returns_false_for_disallowed_action() -> None:
    engine = GovernancePolicyEngine(
        allowed_actions={"analyse_process"},
    )

    assert (
        engine.is_allowed(
            create_request("delete_process"),
        )
        is False
    )


def test_empty_policy_denies_action() -> None:
    engine = GovernancePolicyEngine()

    decision = engine.evaluate(
        create_request("analyse_process"),
    )

    assert decision["allowed"] is False

def test_governance_policy_engine_is_publicly_importable():
    """Verify the Governance Policy Engine is exposed from the package root."""
    from src.governance import GovernancePolicyEngine

    assert GovernancePolicyEngine is not None