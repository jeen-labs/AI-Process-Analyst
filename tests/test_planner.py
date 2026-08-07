"""
===============================================================================
AI Process Analyst
===============================================================================

Module:
    tests/test_planner.py

Purpose:
    Automated tests for the Enterprise Planner.

Phase:
    Milestone 3 - Enterprise AI Orchestration Layer
    Phase 3.6 - Add Planner
===============================================================================
"""

# =============================================================================
# Imports
# =============================================================================

import pytest

from src.orchestration.planner import Planner, PlannerError


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def planner() -> Planner:
    """
    Provide a Planner instance for tests.
    """

    return Planner()


# =============================================================================
# Initialisation Tests
# =============================================================================


def test_planner_initialises(planner):
    """
    Planner should initialise successfully.
    """

    assert isinstance(planner, Planner)


# =============================================================================
# Request Validation Tests
# =============================================================================


def test_plan_rejects_non_string_request(planner):
    """
    Planner should reject non-string requests.
    """

    with pytest.raises(PlannerError):
        planner.plan(None)


def test_plan_rejects_empty_request(planner):
    """
    Planner should reject empty requests.
    """

    with pytest.raises(PlannerError):
        planner.plan("")


def test_plan_rejects_whitespace_request(planner):
    """
    Planner should reject whitespace-only requests.
    """

    with pytest.raises(PlannerError):
        planner.plan("   ")


def test_is_valid_request_returns_true_for_valid_request(planner):
    """
    Valid non-empty requests should be accepted.
    """

    assert planner.is_valid_request(
        "Analyse the customer onboarding process."
    ) is True


def test_is_valid_request_returns_false_for_empty_request(planner):
    """
    Empty requests should be rejected.
    """

    assert planner.is_valid_request("") is False


def test_is_valid_request_returns_false_for_whitespace_request(planner):
    """
    Whitespace-only requests should be rejected.
    """

    assert planner.is_valid_request("   ") is False


def test_is_valid_request_returns_false_for_non_string(planner):
    """
    Non-string requests should be rejected.
    """

    assert planner.is_valid_request(None) is False


# =============================================================================
# Planning Tests
# =============================================================================


def test_plan_returns_dictionary(planner):
    """
    Planner should return a dictionary.
    """

    result = planner.plan(
        "Analyse the customer onboarding process."
    )

    assert isinstance(result, dict)


def test_plan_preserves_request(planner):
    """
    Planner should preserve the supplied request after trimming whitespace.
    """

    result = planner.plan(
        "  Analyse the customer onboarding process.  "
    )

    assert result["request"] == (
        "Analyse the customer onboarding process."
    )


def test_plan_contains_plan_type(planner):
    """
    Planner should identify the type of plan produced.
    """

    result = planner.plan(
        "Analyse the customer onboarding process."
    )

    assert result["plan_type"] == "process_analysis"


def test_plan_contains_steps(planner):
    """
    Planner should produce an ordered list of execution steps.
    """

    result = planner.plan(
        "Analyse the customer onboarding process."
    )

    assert isinstance(result["steps"], list)
    assert len(result["steps"]) == 3


def test_plan_steps_are_ordered(planner):
    """
    Planner steps should have deterministic ordering.
    """

    result = planner.plan(
        "Analyse the customer onboarding process."
    )

    assert [step["step"] for step in result["steps"]] == [
        1,
        2,
        3,
    ]


def test_plan_contains_expected_step_names(planner):
    """
    Planner should produce the expected orchestration steps.
    """

    result = planner.plan(
        "Analyse the customer onboarding process."
    )

    assert [step["name"] for step in result["steps"]] == [
        "build_prompt",
        "execute_llm",
        "parse_response",
    ]


def test_plan_contains_step_descriptions(planner):
    """
    Each planned step should contain a description.
    """

    result = planner.plan(
        "Analyse the customer onboarding process."
    )

    for step in result["steps"]:
        assert "description" in step
        assert isinstance(step["description"], str)
        assert step["description"].strip()


# =============================================================================
# Determinism Tests
# =============================================================================


def test_plan_is_deterministic(planner):
    """
    The same request should produce the same execution plan.
    """

    request = "Analyse the customer onboarding process."

    first_plan = planner.plan(request)
    second_plan = planner.plan(request)

    assert first_plan == second_plan
