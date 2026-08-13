"""
Tests for the Governance Compliance Boundary.

Phase:
Milestone 4 - Governance Platform
Phase 4.7 - Implement Governance Compliance

These tests verify deterministic structural compliance validation.

The compliance boundary is intentionally tested separately from:

- policy evaluation
- permissions
- authorization
- security
- auditing
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

from src.governance.governance_compliance import GovernanceCompliance
from src.governance.governance_compliance import GovernanceComplianceError


# =============================================================================
# Test Helpers
# =============================================================================


def create_compliance() -> GovernanceCompliance:
    """
    Create a fresh GovernanceCompliance instance for a test.
    """

    return GovernanceCompliance()


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


def test_compliance_can_be_constructed():
    """
    GovernanceCompliance should be constructible without dependencies.
    """

    compliance = create_compliance()

    assert isinstance(
        compliance,
        GovernanceCompliance,
    )


def test_compliance_is_deterministic_stateless_component():
    """
    GovernanceCompliance should not require mutable configuration.
    """

    first = create_compliance()
    second = create_compliance()

    assert type(first) is type(second)


# =============================================================================
# Validation - Valid Requests
# =============================================================================


def test_validate_accepts_valid_request():
    """
    A structurally valid request should pass compliance validation.
    """

    compliance = create_compliance()

    request = make_valid_request()

    assert compliance.validate(request) is True


def test_validate_accepts_action_with_surrounding_whitespace():
    """
    Validation should accept a non-empty action with surrounding whitespace.
    """

    compliance = create_compliance()

    request = make_valid_request()
    request["action"] = "  process_analysis  "

    assert compliance.validate(request) is True


def test_validate_accepts_subject_with_surrounding_whitespace():
    """
    Validation should accept a non-empty subject with surrounding whitespace.
    """

    compliance = create_compliance()

    request = make_valid_request()
    request["subject"] = "  analyst  "

    assert compliance.validate(request) is True


def test_validate_accepts_resource_with_surrounding_whitespace():
    """
    Validation should accept a non-empty resource with surrounding whitespace.
    """

    compliance = create_compliance()

    request = make_valid_request()
    request["resource"] = "  customer_onboarding  "

    assert compliance.validate(request) is True


def test_validate_accepts_empty_context():
    """
    Empty context is valid.
    """

    compliance = create_compliance()

    request = make_valid_request()
    request["context"] = {}

    assert compliance.validate(request) is True


def test_validate_accepts_populated_context():
    """
    Context may contain arbitrary contextual information.
    """

    compliance = create_compliance()

    request = make_valid_request()

    request["context"] = {
        "source": "orchestration_engine",
        "environment": "test",
        "trace_id": "trace-001",
    }

    assert compliance.validate(request) is True


def test_validate_accepts_arbitrary_context_values():
    """
    Context values are intentionally treated as opaque data.
    """

    compliance = create_compliance()

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

    assert compliance.validate(request) is True


def test_validate_accepts_empty_string_context_values():
    """
    Empty context values do not invalidate the context structure.
    """

    compliance = create_compliance()

    request = make_valid_request()

    request["context"] = {
        "source": "",
    }

    assert compliance.validate(request) is True


def test_validate_returns_boolean_true():
    """
    validate() should return exactly True for valid requests.
    """

    compliance = create_compliance()

    result = compliance.validate(
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
    Compliance validation should reject non-dictionary requests.
    """

    compliance = create_compliance()

    with pytest.raises(
        GovernanceComplianceError,
        match="request must be a dictionary",
    ):
        compliance.validate(invalid_request)


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

    compliance = create_compliance()

    request = make_valid_request()

    del request[missing_field]

    with pytest.raises(
        GovernanceComplianceError,
        match=missing_field,
    ):
        compliance.validate(request)


def test_validate_rejects_multiple_missing_fields():
    """
    Multiple missing required fields should be reported.
    """

    compliance = create_compliance()

    request = {}

    with pytest.raises(
        GovernanceComplianceError,
        match="action",
    ):
        compliance.validate(request)


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

    compliance = create_compliance()

    request = make_valid_request()
    request["action"] = invalid_action

    with pytest.raises(
        GovernanceComplianceError,
        match="action must be a string",
    ):
        compliance.validate(request)


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

    compliance = create_compliance()

    request = make_valid_request()
    request["action"] = empty_action

    with pytest.raises(
        GovernanceComplianceError,
        match="action must not be empty",
    ):
        compliance.validate(request)


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

    compliance = create_compliance()

    request = make_valid_request()
    request["subject"] = invalid_subject

    with pytest.raises(
        GovernanceComplianceError,
        match="subject must be a string",
    ):
        compliance.validate(request)


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

    compliance = create_compliance()

    request = make_valid_request()
    request["subject"] = empty_subject

    with pytest.raises(
        GovernanceComplianceError,
        match="subject must not be empty",
    ):
        compliance.validate(request)


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

    compliance = create_compliance()

    request = make_valid_request()
    request["resource"] = invalid_resource

    with pytest.raises(
        GovernanceComplianceError,
        match="resource must be a string",
    ):
        compliance.validate(request)


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

    compliance = create_compliance()

    request = make_valid_request()
    request["resource"] = empty_resource

    with pytest.raises(
        GovernanceComplianceError,
        match="resource must not be empty",
    ):
        compliance.validate(request)


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

    compliance = create_compliance()

    request = make_valid_request()
    request["context"] = invalid_context

    with pytest.raises(
        GovernanceComplianceError,
        match="context must be a dictionary",
    ):
        compliance.validate(request)


# =============================================================================
# Evaluation
# =============================================================================


def test_evaluate_accepts_valid_request():
    """
    A valid request should produce a compliance decision.
    """

    compliance = create_compliance()

    request = make_valid_request()

    decision = compliance.evaluate(request)

    assert isinstance(decision, dict)

    assert set(decision.keys()) == {
        "action",
        "allowed",
        "reason",
    }

    assert isinstance(decision["action"], str)
    assert isinstance(decision["allowed"], bool)
    assert isinstance(decision["reason"], str)


def test_evaluate_returns_action():
    """
    Compliance decisions should identify the evaluated action.
    """

    compliance = create_compliance()

    request = make_valid_request()

    decision = compliance.evaluate(request)

    assert decision["action"] == "process_analysis"


def test_evaluate_normalizes_action_whitespace():
    """
    Evaluation should normalize surrounding action whitespace.
    """

    compliance = create_compliance()

    request = make_valid_request()
    request["action"] = "  process_analysis  "

    decision = compliance.evaluate(request)

    assert decision["action"] == "process_analysis"


def test_evaluate_returns_allowed_field():
    """
    Compliance decisions should contain an allowed boolean.
    """

    compliance = create_compliance()

    request = make_valid_request()

    decision = compliance.evaluate(request)

    assert decision["allowed"] is True
    assert isinstance(
        decision["allowed"],
        bool,
    )


def test_evaluate_returns_reason():
    """
    Compliance decisions should contain a human-readable reason.
    """

    compliance = create_compliance()

    request = make_valid_request()

    decision = compliance.evaluate(request)

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

    compliance = create_compliance()

    with pytest.raises(
        GovernanceComplianceError,
    ):
        compliance.evaluate(invalid_request)


def test_evaluate_rejects_missing_action():
    """
    Evaluation should reject requests without an action.
    """

    compliance = create_compliance()

    request = make_valid_request()

    del request["action"]

    with pytest.raises(
        GovernanceComplianceError,
        match="action",
    ):
        compliance.evaluate(request)


def test_evaluate_is_deterministic():
    """
    Repeated evaluation of the same request should produce the same result.
    """

    compliance = create_compliance()

    request = make_valid_request()

    first = compliance.evaluate(request)
    second = compliance.evaluate(request)

    assert first == second


def test_repeated_compliance_evaluation_is_stable():
    """
    Repeated compliance evaluations should remain stable.
    """

    compliance = create_compliance()

    request = make_valid_request()

    results = [
        compliance.evaluate(request)
        for _ in range(5)
    ]

    assert all(
        result == results[0]
        for result in results
    )


# =============================================================================
# Boolean Compliance Check
# =============================================================================


def test_is_compliant_returns_boolean():
    """
    is_compliant should return a boolean.
    """

    compliance = create_compliance()

    request = make_valid_request()

    result = compliance.is_compliant(request)

    assert isinstance(result, bool)


def test_is_compliant_accepts_valid_request():
    """
    A valid request should pass the compliance boundary.
    """

    compliance = create_compliance()

    request = make_valid_request()

    assert compliance.is_compliant(request) is True


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
def test_is_compliant_rejects_invalid_request(
    invalid_request: Any,
):
    """
    Invalid requests should not pass the compliance boundary.
    """

    compliance = create_compliance()

    assert compliance.is_compliant(invalid_request) is False


def test_is_compliant_does_not_raise_for_invalid_request():
    """
    is_compliant should provide a safe boolean boundary.
    """

    compliance = create_compliance()

    assert compliance.is_compliant(None) is False


# =============================================================================
# State Isolation
# =============================================================================


def test_compliance_does_not_store_request_state():
    """
    Evaluating one request must not affect a later request.
    """

    compliance = create_compliance()

    first_request = make_valid_request()

    second_request = make_valid_request()
    second_request["action"] = "document_analysis"

    first_result = compliance.evaluate(
        first_request
    )

    second_result = compliance.evaluate(
        second_request
    )

    assert first_result["action"] == "process_analysis"
    assert second_result["action"] == "document_analysis"


def test_compliance_instances_are_independent():
    """
    Separate compliance instances should behave independently.
    """

    first = create_compliance()
    second = create_compliance()

    request = make_valid_request()

    assert first.evaluate(request) == second.evaluate(request)


# =============================================================================
# Compliance Boundary Separation
# =============================================================================


def test_compliance_does_not_make_policy_decision():
    """
    Compliance should not determine whether an action is allowed by policy.

    A structurally compliant action should pass the compliance boundary even
    when the action name is not a known policy action.
    """

    compliance = create_compliance()

    request = make_valid_request()

    request["action"] = "unknown_action"

    assert compliance.is_compliant(request) is True

    decision = compliance.evaluate(request)

    assert decision["allowed"] is True


def test_compliance_does_not_require_permissions():
    """
    Compliance validation should not require a permission registry.
    """

    compliance = create_compliance()

    request = make_valid_request()

    assert compliance.is_compliant(request) is True


def test_compliance_does_not_require_authorization_dependencies():
    """
    GovernanceCompliance should be usable independently of authorization.
    """

    compliance = create_compliance()

    request = make_valid_request()

    decision = compliance.evaluate(request)

    assert decision["allowed"] is True


def test_compliance_does_not_require_security_dependency():
    """
    GovernanceCompliance should not depend on GovernanceSecurity.
    """

    compliance = create_compliance()

    request = make_valid_request()

    assert compliance.is_compliant(request) is True


def test_compliance_does_not_require_audit_dependency():
    """
    GovernanceCompliance should not depend on GovernanceAudit.
    """

    compliance = create_compliance()

    request = make_valid_request()

    decision = compliance.evaluate(request)

    assert decision["allowed"] is True


# =============================================================================
# Immutability of Decision Semantics
# =============================================================================


def test_evaluate_returns_only_governance_decision_fields():
    """
    Compliance evaluation should return the stable GovernanceDecision shape.
    """

    compliance = create_compliance()

    decision = compliance.evaluate(
        make_valid_request()
    )

    assert set(decision.keys()) == {
        "action",
        "allowed",
        "reason",
    }


def test_evaluate_reason_is_deterministic():
    """
    The compliance reason should remain stable for the same request.
    """

    compliance = create_compliance()

    request = make_valid_request()

    first = compliance.evaluate(request)
    second = compliance.evaluate(request)

    assert first["reason"] == second["reason"]


# =============================================================================
# Regression Tests
# =============================================================================


def test_valid_process_analysis_request_remains_compliant():
    """
    The existing orchestration action process_analysis should remain
    structurally compliant at the governance compliance boundary.
    """

    compliance = create_compliance()

    request = {
        "action": "process_analysis",
        "subject": "analyst",
        "resource": "customer_onboarding",
        "context": {},
    }

    assert compliance.is_compliant(request) is True


def test_compliance_boundary_is_not_an_execution_component():
    """
    GovernanceCompliance should expose only compliance concerns.

    The component must not expose an execute() method.
    """

    compliance = create_compliance()

    assert not hasattr(
        compliance,
        "execute",
    )


def test_compliance_boundary_is_not_a_policy_engine():
    """
    GovernanceCompliance should not expose policy configuration.
    """

    compliance = create_compliance()

    assert not hasattr(
        compliance,
        "allowed_actions",
    )


def test_compliance_boundary_has_no_permission_registry():
    """
    GovernanceCompliance should not own permissions.
    """

    compliance = create_compliance()

    assert not hasattr(
        compliance,
        "_permissions",
    )


# =============================================================================
# Final Determinism Check
# =============================================================================


def test_complete_compliance_flow_is_deterministic():
    """
    Validate -> evaluate -> is_compliant should remain deterministic.
    """

    compliance = create_compliance()

    request = make_valid_request()

    validation_results = [
        compliance.validate(request)
        for _ in range(3)
    ]

    decisions = [
        compliance.evaluate(request)
        for _ in range(3)
    ]

    compliant_results = [
        compliance.is_compliant(request)
        for _ in range(3)
    ]

    assert validation_results == [
        True,
        True,
        True,
    ]

    assert decisions[0] == decisions[1] == decisions[2]

    assert compliant_results == [
        True,
        True,
        True,
    ]