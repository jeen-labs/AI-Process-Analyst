"""
===============================================================================
AI Process Analyst
===============================================================================

Module:
    tests/test_governance_release_validation.py

Purpose:
    Final release-validation tests for the Governance Platform.

These tests validate the stable public Governance Platform surface without
introducing assumptions about internal constructor signatures or implementation
details.

The detailed behaviour of individual governance components is covered by the
dedicated governance test suites.

Author:
    Jeen Labs

Status:
    Release Validation
===============================================================================
"""

from __future__ import annotations

import src.governance as governance


# =============================================================================
# Public API Availability
# =============================================================================


def test_governance_package_imports_successfully() -> None:
    """
    The public governance package must remain importable.
    """

    assert governance is not None


def test_governance_public_exports_are_defined() -> None:
    """
    Every symbol declared in __all__ must exist on the public package.
    """

    for symbol_name in governance.__all__:
        assert hasattr(
            governance,
            symbol_name,
        )


def test_governance_public_exports_are_not_empty() -> None:
    """
    The governance package must expose a non-empty stable public API.
    """

    assert governance.__all__
    assert len(governance.__all__) >= 1


# =============================================================================
# Public Contract Availability
# =============================================================================


def test_governance_request_is_public() -> None:
    """
    GovernanceRequest must remain publicly importable.
    """

    assert governance.GovernanceRequest is not None


def test_governance_decision_is_public() -> None:
    """
    GovernanceDecision must remain publicly importable.
    """

    assert governance.GovernanceDecision is not None


# =============================================================================
# Policy Engine
# =============================================================================


def test_governance_policy_engine_is_public() -> None:
    """
    GovernancePolicyEngine must remain publicly importable.
    """

    assert governance.GovernancePolicyEngine is not None


# =============================================================================
# Permissions
# =============================================================================


def test_governance_permission_is_public() -> None:
    """
    GovernancePermission must remain publicly importable.
    """

    assert governance.GovernancePermission is not None


def test_governance_permissions_is_public() -> None:
    """
    GovernancePermissions must remain publicly importable.
    """

    assert governance.GovernancePermissions is not None


# =============================================================================
# Authorization
# =============================================================================


def test_governance_authorization_is_public() -> None:
    """
    GovernanceAuthorization must remain publicly importable.
    """

    assert governance.GovernanceAuthorization is not None


# =============================================================================
# Audit
# =============================================================================


def test_governance_audit_is_public() -> None:
    """
    GovernanceAudit must remain publicly importable.
    """

    assert governance.GovernanceAudit is not None


def test_governance_audit_entry_is_public() -> None:
    """
    GovernanceAuditEntry must remain publicly importable.
    """

    assert governance.GovernanceAuditEntry is not None


# =============================================================================
# Compliance
# =============================================================================


def test_governance_compliance_is_public() -> None:
    """
    GovernanceCompliance must remain publicly importable.
    """

    assert governance.GovernanceCompliance is not None


def test_governance_compliance_error_is_public() -> None:
    """
    GovernanceComplianceError must remain publicly importable.
    """

    assert governance.GovernanceComplianceError is not None


# =============================================================================
# Security
# =============================================================================


def test_governance_security_is_public() -> None:
    """
    GovernanceSecurity must remain publicly importable.
    """

    assert governance.GovernanceSecurity is not None


def test_governance_security_error_is_public() -> None:
    """
    GovernanceSecurityError must remain publicly importable.
    """

    assert governance.GovernanceSecurityError is not None


# =============================================================================
# Decision Boundary
# =============================================================================


def test_governance_decision_boundary_is_public() -> None:
    """
    GovernanceDecisionBoundary must remain publicly importable.
    """

    assert governance.GovernanceDecisionBoundary is not None


def test_governance_decision_boundary_error_is_public() -> None:
    """
    GovernanceDecisionBoundaryError must remain publicly importable.
    """

    assert governance.GovernanceDecisionBoundaryError is not None


# =============================================================================
# Public API Consistency
# =============================================================================


def test_governance_all_contains_expected_public_components() -> None:
    """
    Verify the major governance components remain part of the stable API.
    """

    expected_symbols = {
        "GovernanceRequest",
        "GovernanceDecision",
        "GovernancePolicyEngine",
        "GovernancePermission",
        "GovernancePermissions",
        "GovernanceAuthorization",
        "GovernanceAudit",
        "GovernanceAuditEntry",
        "GovernanceCompliance",
        "GovernanceComplianceError",
        "GovernanceSecurity",
        "GovernanceSecurityError",
        "GovernanceDecisionBoundary",
        "GovernanceDecisionBoundaryError",
    }

    assert expected_symbols.issubset(
        set(governance.__all__)
    )


def test_governance_public_api_contains_no_missing_symbols() -> None:
    """
    Every declared public symbol must resolve successfully.
    """

    missing_symbols = [
        symbol_name
        for symbol_name in governance.__all__
        if not hasattr(governance, symbol_name)
    ]

    assert missing_symbols == []


def test_governance_public_api_is_stable_package_boundary() -> None:
    """
    The governance package must expose its API through src.governance rather
    than requiring callers to know internal implementation modules.
    """

    assert governance.__name__ == "src.governance"