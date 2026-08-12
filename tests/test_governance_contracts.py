"""
AI Process Analyst

Module:
tests.test_governance_contracts

Purpose:
Test the structural contracts of the Governance Platform.

Phase:
Milestone 4 - Governance Platform
Phase 4.1 - Define Governance Platform Contracts
"""

from typing import get_type_hints

from src.governance import (
    GovernanceDecision,
    GovernanceRequest,
)


# =============================================================================
# Governance Decision Contract
# =============================================================================

def test_governance_decision_is_publicly_exported():
    """GovernanceDecision should be available from the package root."""
    assert GovernanceDecision is not None


def test_governance_decision_has_expected_fields():
    """GovernanceDecision should expose the stable expected fields."""
    assert list(
        get_type_hints(GovernanceDecision)
    ) == [
        "action",
        "allowed",
        "reason",
    ]


def test_governance_decision_accepts_expected_structure():
    """GovernanceDecision should accept the expected structural contract."""
    decision: GovernanceDecision = {
        "action": "process_analysis",
        "allowed": True,
        "reason": "Action is permitted.",
    }

    assert decision["action"] == "process_analysis"
    assert decision["allowed"] is True
    assert decision["reason"] == "Action is permitted."


# =============================================================================
# Governance Request Contract
# =============================================================================

def test_governance_request_is_publicly_exported():
    """GovernanceRequest should be available from the package root."""
    assert GovernanceRequest is not None


def test_governance_request_has_expected_fields():
    """GovernanceRequest should expose the stable expected fields."""
    assert list(
        get_type_hints(GovernanceRequest)
    ) == [
        "action",
        "subject",
        "resource",
        "context",
    ]


def test_governance_request_accepts_expected_structure():
    """GovernanceRequest should accept the expected structural contract."""
    request: GovernanceRequest = {
        "action": "process_analysis",
        "subject": "process_analyst",
        "resource": "customer_onboarding",
        "context": {
            "source": "enterprise_process_repository",
        },
    }

    assert request["action"] == "process_analysis"
    assert request["subject"] == "process_analyst"
    assert request["resource"] == "customer_onboarding"
    assert request["context"]["source"] == (
        "enterprise_process_repository"
    )


# =============================================================================
# Public API
# =============================================================================

def test_governance_public_exports_are_stable():
    """Verify the explicitly supported Governance Platform exports."""
    import src.governance as governance

    assert governance.__all__ == [
        "GovernanceDecision",
        "GovernanceRequest",
    ]