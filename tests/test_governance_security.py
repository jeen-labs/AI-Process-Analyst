"""
Tests for the Governance Security Boundary.

Phase:
Milestone 4 - Governance Platform
Phase 4.7 - Governance Security Boundary

These tests verify deterministic structural security validation.

The security boundary is intentionally tested separately from:

- policy evaluation
- permissions
- authorization
- auditing
- compliance
"""

# =============================================================================
# Standard Library Imports
# =============================================================================

from typing import Any


# =============================================================================
# Pytest
# =============================================================================

import pytest


# =============================================================================
# Local Imports
# =============================================================================

from src.governance.governance_contracts import GovernanceDecision
from src.governance.governance_security import GovernanceSecurity
from src.governance.governance_security import GovernanceSecurityError


# =============================================================================
# Test Helpers
# =============================================================================


def create_security() -> GovernanceSecurity:
    """
    Create a fresh GovernanceSecurity instance for a test.
    """

    return GovernanceSecurity()


def make_valid_request() -> dict[str, Any]:
    """
    Return a structurally valid governance request.
    """

    return {
        "action": "process_analysis",
        "subject": "analyst",
        "resource": "customer_onboarding",
        "context": {},
    }


# =============================================================================
# Construction
# =============================================================================


def test_security_can_be_constructed():
    """
    GovernanceSecurity should be constructible without dependencies.
    """

    security = create_security()

    assert isinstance(
        security,
        GovernanceSecurity,
    )


def test_security_is_deterministic_stateless_component():
    """
    GovernanceSecurity should not require mutable configuration.
    """

    first = create_security()
    second = create_security()

    assert type(first) is type(second)


# =============================================================================
# Validation - Valid Requests
# =============================================================================


def test_validate_accepts_valid_request():
    """
    A structurally valid request should pass validation.
    """

    security = create_security()

    request = make_valid_request()

    assert security.validate(request) is True


def test_validate_accepts_action_with_surrounding_whitespace():
    """
    Validation should accept a non-empty action with surrounding whitespace.
    """

    security = create_security()

    request = make_valid_request()
    request["action"] = "  process_analysis  "

    assert security.validate(request) is True


def test_validate_accepts_subject_with_surrounding_whitespace():
    """
    Validation should accept a non-empty subject with surrounding whitespace.
    """

    security = create_security()

    request = make_valid_request()
    request["subject"] = "  analyst  "

    assert security.validate(request) is True


def test_validate_accepts_resource_with_surrounding_whitespace():
    """
    Validation should accept a non-empty resource with surrounding whitespace.
    """

    security = create_security()

    request = make_valid_request()
    request["resource"] = "  customer_onboarding  "

    assert security.validate(request) is True


def test_validate_accepts_empty_context():
    """
    Empty context is valid.
    """

    security = create_security()

    request = make_valid_request()

    request["context"] = {}

    assert security.validate(request) is True


def test_validate_accepts_populated_context():
    """
    Context may contain additional security-related information.
    """

    security = create_security()

    request = make_valid_request()

    request["context"] = {
        "source": "orchestration_engine",
        "environment": "test",
        "trace_id": "trace-001",
    }

    assert security.validate(request) is True


def test_validate_returns_boolean_true():
    """
    validate() should return exactly True for valid requests.
    """

    security = create_security()

    result = security.validate(
        make_valid_request()
    )

    assert result is True
    assert isinstance(result, bool)


# =============================================================================
# Validation - Request Type
# =============================================================================


@pytest.mark.parametrize(
    "invalid_request",
    [
        None,
        "",
        "request",
        123,
        1.5,
        [],
        (),
        set(),
        object(),
    ],
)
def test_validate_rejects_non_dictionary_request(
    invalid_request: Any,
):
    """
    Security validation should reject non-dictionary requests.
    """

    security = create_security()

    with pytest.raises(
        GovernanceSecurityError,
        match="request must be a dictionary",
    ):
        security.validate(invalid_request)


# =============================================================================
# Validation - Required Fields
# =============================================================================


@pytest.mark.parametrize(
    "missing_field",
    [
        "action",
        "subject",
        "resource",
        "context",
    ],
)
def test_validate_rejects_missing_required_field(
    missing_field: str,
):
    """
    Every governance request must contain all required fields.
    """

    security = create_security()

    request = make_valid_request()

    del request[missing_field]

    with pytest.raises(
        GovernanceSecurityError,
        match=missing_field,
    ):
        security.validate(request)


def test_validate_rejects_multiple_missing_fields():
    """
    Multiple missing required fields should be reported.
    """

    security = create_security()

    request = {}

    with pytest.raises(
        GovernanceSecurityError,
        match="action",
    ):
        security.validate(request)


# =============================================================================
# Validation - Action
# =============================================================================


@pytest.mark.parametrize(
    "invalid_action",
    [
        None,
        123,
        [],
        {},
        object(),
    ],
)
def test_validate_rejects_invalid_action_type(
    invalid_action: Any,
):
    """
    Action must be a string.
    """

    security = create_security()

    request = make_valid_request()
    request["action"] = invalid_action

    with pytest.raises(
        GovernanceSecurityError,
        match="action must be a string",
    ):
        security.validate(request)


@pytest.mark.parametrize(
    "empty_action",
    [
        "",
        " ",
        "   ",
        "\t",
        "\n",
    ],
)
def test_validate_rejects_empty_action(
    empty_action: str,
):
    """
    Action must contain non-whitespace content.
    """

    security = create_security()

    request = make_valid_request()
    request["action"] = empty_action

    with pytest.raises(
        GovernanceSecurityError,
        match="action must not be empty",
    ):
        security.validate(request)


# =============================================================================
# Validation - Subject
# =============================================================================


@pytest.mark.parametrize(
    "invalid_subject",
    [
        None,
        123,
        [],
        {},
        object(),
    ],
)
def test_validate_rejects_invalid_subject_type(
    invalid_subject: Any,
):
    """
    Subject must be a string.
    """

    security = create_security()

    request = make_valid_request()
    request["subject"] = invalid_subject

    with pytest.raises(
        GovernanceSecurityError,
        match="subject must be a string",
    ):
        security.validate(request)


@pytest.mark.parametrize(
    "empty_subject",
    [
        "",
        " ",
        "   ",
        "\t",
        "\n",
    ],
)
def test_validate_rejects_empty_subject(
    empty_subject: str,
):
    """
    Subject must contain non-whitespace content.
    """

    security = create_security()

    request = make_valid_request()
    request["subject"] = empty_subject

    with pytest.raises(
        GovernanceSecurityError,
        match="subject must not be empty",
    ):
        security.validate(request)


# =============================================================================
# Validation - Resource
# =============================================================================


@pytest.mark.parametrize(
    "invalid_resource",
    [
        None,
        123,
        [],
        {},
        object(),
    ],
)
def test_validate_rejects_invalid_resource_type(
    invalid_resource: Any,
):
    """
    Resource must be a string.
    """

    security = create_security()

    request = make_valid_request()
    request["resource"] = invalid_resource

    with pytest.raises(
        GovernanceSecurityError,
        match="resource must be a string",
    ):
        security.validate(request)


@pytest.mark.parametrize(
    "empty_resource",
    [
        "",
        " ",
        "   ",
        "\t",
        "\n",
    ],
)
def test_validate_rejects_empty_resource(
    empty_resource: str,
):
    """
    Resource must contain non-whitespace content.
    """

    security = create_security()

    request = make_valid_request()
    request["resource"] = empty_resource

    with pytest.raises(
        GovernanceSecurityError,
        match="resource must not be empty",
    ):
        security.validate(request)


# =============================================================================
# Validation - Context
# =============================================================================


@pytest.mark.parametrize(
    "invalid_context",
    [
        None,
        "",
        "context",
        123,
        1.5,
        [],
        (),
        set(),
        object(),
    ],
)
def test_validate_rejects_invalid_context_type(
    invalid_context: Any,
):
    """
    Context must be a dictionary.
    """

    security = create_security()

    request = make_valid_request()
    request["context"] = invalid_context

    with pytest.raises(
        GovernanceSecurityError,
        match="context must be a dictionary",
    ):
        security.validate(request)


# =============================================================================
# Evaluation
# =============================================================================


def test_evaluate_accepts_valid_request():
    """
    A valid request should produce a security decision.

    GovernanceDecision is a TypedDict, so it cannot be checked with
    isinstance(). Instead, verify the required structural fields.
    """

    security = create_security()

    request = make_valid_request()

    decision = security.evaluate(request)

    assert isinstance(
        decision,
        dict,
    )

    assert set(decision.keys()) == {
        "action",
        "allowed",
        "reason",
    }


def test_evaluate_returns_action():
    """
    Security decisions should identify the evaluated action.
    """

    security = create_security()

    request = make_valid_request()

    decision = security.evaluate(request)

    assert decision["action"] == "process_analysis"


def test_evaluate_normalizes_action_whitespace():
    """
    Evaluation should normalize surrounding action whitespace.
    """

    security = create_security()

    request = make_valid_request()
    request["action"] = "  process_analysis  "

    decision = security.evaluate(request)

    assert decision["action"] == "process_analysis"


def test_evaluate_returns_allowed_field():
    """
    Security decisions should contain an allowed boolean.
    """

    security = create_security()

    request = make_valid_request()

    decision = security.evaluate(request)

    assert decision["allowed"] is True
    assert isinstance(
        decision["allowed"],
        bool,
    )


def test_evaluate_returns_reason():
    """
    Security decisions should contain a human-readable reason.
    """

    security = create_security()

    request = make_valid_request()

    decision = security.evaluate(request)

    assert isinstance(
        decision["reason"],
        str,
    )

    assert decision["reason"]


@pytest.mark.parametrize(
    "invalid_request",
    [
        None,
        "",
        123,
        [],
        (),
    ],
)
def test_evaluate_rejects_invalid_request(
    invalid_request: Any,
):
    """
    Evaluation should reject structurally invalid requests.
    """

    security = create_security()

    with pytest.raises(
        GovernanceSecurityError,
    ):
        security.evaluate(invalid_request)


def test_evaluate_rejects_missing_action():
    """
    Evaluation should reject requests without an action.
    """

    security = create_security()

    request = make_valid_request()

    del request["action"]

    with pytest.raises(
        GovernanceSecurityError,
        match="action",
    ):
        security.evaluate(request)


def test_evaluate_is_deterministic():
    """
    Repeated evaluation of the same request should produce the same result.
    """

    security = create_security()

    request = make_valid_request()

    first = security.evaluate(request)
    second = security.evaluate(request)

    assert first == second


def test_repeated_security_evaluation_is_stable():
    """
    Repeated security evaluations should remain stable.
    """

    security = create_security()

    request = make_valid_request()

    results = [
        security.evaluate(request)
        for _ in range(5)
    ]

    assert all(
        result == results[0]
        for result in results
    )


# =============================================================================
# Boolean Security Check
# =============================================================================


def test_is_secure_returns_boolean():
    """
    is_secure should return a boolean.
    """

    security = create_security()

    request = make_valid_request()

    result = security.is_secure(request)

    assert isinstance(result, bool)


def test_is_secure_accepts_valid_request():
    """
    A valid request should pass the security boundary.
    """

    security = create_security()

    request = make_valid_request()

    assert security.is_secure(request) is True


@pytest.mark.parametrize(
    "invalid_request",
    [
        None,
        "",
        123,
        [],
        (),
        object(),
    ],
)
def test_is_secure_rejects_invalid_request(
    invalid_request: Any,
):
    """
    Invalid requests should not pass the security boundary.
    """

    security = create_security()

    assert security.is_secure(invalid_request) is False


def test_is_secure_does_not_raise_for_invalid_request():
    """
    is_secure should provide a safe boolean boundary.
    """

    security = create_security()

    assert security.is_secure(None) is False


# =============================================================================
# State Isolation
# =============================================================================


def test_security_does_not_store_request_state():
    """
    Evaluating one request must not affect a later request.
    """

    security = create_security()

    first_request = make_valid_request()

    second_request = make_valid_request()
    second_request["action"] = "document_analysis"

    first_result = security.evaluate(
        first_request
    )

    second_result = security.evaluate(
        second_request
    )

    assert first_result["action"] == "process_analysis"
    assert second_result["action"] == "document_analysis"


def test_security_instances_are_independent():
    """
    Separate security instances should behave independently.
    """

    first = create_security()
    second = create_security()

    request = make_valid_request()

    assert first.evaluate(request) == second.evaluate(request)


# =============================================================================
# Security Boundary Separation
# =============================================================================


def test_security_does_not_make_policy_decision():
    """
    Security validation should not determine whether an action is allowed
    by governance policy.

    A structurally valid action is accepted by the security boundary even
    when the action name is not a known policy action.
    """

    security = create_security()

    request = make_valid_request()

    request["action"] = "unknown_action"

    assert security.is_secure(request) is True

    decision = security.evaluate(request)

    assert decision["allowed"] is True


def test_security_does_not_require_permissions():
    """
    Security validation should not require a permission registry.
    """

    security = create_security()

    request = make_valid_request()

    assert security.is_secure(request) is True


def test_security_does_not_require_authorization_dependencies():
    """
    GovernanceSecurity should be usable independently of authorization.
    """

    security = create_security()

    request = make_valid_request()

    decision = security.evaluate(request)

    assert decision["allowed"] is True


# =============================================================================
# Context Isolation
# =============================================================================


def test_security_accepts_arbitrary_context_values():
    """
    Context values are intentionally treated as opaque contextual data.

    The security boundary validates that context is a dictionary but does
    not impose application-specific policy on its contents.
    """

    security = create_security()

    request = make_valid_request()

    request["context"] = {
        "number": 123,
        "boolean": True,
        "nested": {
            "value": "example",
        },
        "items": [
            1,
            2,
            3,
        ],
    }

    assert security.is_secure(request) is True


def test_security_accepts_empty_string_context_values():
    """
    Empty context values do not invalidate the context structure.
    """

    security = create_security()

    request = make_valid_request()

    request["context"] = {
        "source": "",
    }

    assert security.is_secure(request) is True


# =============================================================================
# Immutability of Decision Semantics
# =============================================================================


def test_evaluate_returns_only_governance_decision_fields():
    """
    Security evaluation should return the stable GovernanceDecision shape.
    """

    security = create_security()

    decision = security.evaluate(
        make_valid_request()
    )

    assert set(decision.keys()) == {
        "action",
        "allowed",
        "reason",
    }


def test_evaluate_reason_is_deterministic():
    """
    The security reason should remain stable for the same request.
    """

    security = create_security()

    request = make_valid_request()

    first = security.evaluate(request)
    second = security.evaluate(request)

    assert first["reason"] == second["reason"]


# =============================================================================
# Regression Tests
# =============================================================================


def test_valid_process_analysis_request_remains_secure():
    """
    The existing orchestration action process_analysis should remain
    structurally valid at the security boundary.
    """

    security = create_security()

    request = {
        "action": "process_analysis",
        "subject": "analyst",
        "resource": "customer_onboarding",
        "context": {},
    }

    assert security.is_secure(request) is True


def test_security_boundary_is_not_an_execution_component():
    """
    GovernanceSecurity should expose only validation/evaluation concerns.

    The component must not expose an execute() method.
    """

    security = create_security()

    assert not hasattr(
        security,
        "execute",
    )


def test_security_boundary_is_not_a_policy_engine():
    """
    GovernanceSecurity should not expose policy configuration.
    """

    security = create_security()

    assert not hasattr(
        security,
        "allowed_actions",
    )


def test_security_boundary_has_no_permission_registry():
    """
    GovernanceSecurity should not own permissions.
    """

    security = create_security()

    assert not hasattr(
        security,
        "_permissions",
    )


# =============================================================================
# Final Determinism Check
# =============================================================================


def test_complete_security_flow_is_deterministic():
    """
    Validate -> evaluate -> is_secure should remain deterministic.
    """

    security = create_security()

    request = make_valid_request()

    validation_results = [
        security.validate(request)
        for _ in range(3)
    ]

    decisions = [
        security.evaluate(request)
        for _ in range(3)
    ]

    secure_results = [
        security.is_secure(request)
        for _ in range(3)
    ]

    assert validation_results == [
        True,
        True,
        True,
    ]

    assert decisions[0] == decisions[1] == decisions[2]

    assert secure_results == [
        True,
        True,
        True,
    ]