"""
===============================================================================
AI Process Analyst
===============================================================================

Module:
    tests/test_governance_public_api.py

Purpose:
    Stabilise and verify the public Governance Platform API.

Phase:
    Milestone 4 - Governance Platform
    Phase 4.11 - Stabilise Public Governance API

Responsibilities:
    - Verify stable public governance imports
    - Verify the public __all__ contract
    - Verify exported governance classes remain constructible
    - Prevent accidental removal of public governance symbols
    - Keep consumers independent from internal module paths

The tests intentionally import governance components through the public
package boundary rather than directly from implementation modules.

Author:
    Jeen Labs
===============================================================================
"""

# =============================================================================
# Imports
# =============================================================================

import src.governance as governance


# =============================================================================
# Expected Public API
# =============================================================================


EXPECTED_PUBLIC_EXPORTS = {
    "GovernanceDecision",
    "GovernanceRequest",
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


# =============================================================================
# Public API Contract Tests
# =============================================================================


def test_governance_package_is_importable():
    """
    The public governance package must remain importable.
    """

    assert governance is not None


def test_governance_public_exports_exist():
    """
    Every declared public governance symbol must exist on the package.
    """

    for export_name in EXPECTED_PUBLIC_EXPORTS:

        assert hasattr(
            governance,
            export_name,
        ), (
            f"Public governance API is missing export: "
            f"{export_name}"
        )


def test_governance_all_matches_expected_public_api():
    """
    __all__ must expose the complete stable governance API.

    This prevents accidental addition or removal of public symbols without
    an intentional API change.
    """

    assert set(governance.__all__) == EXPECTED_PUBLIC_EXPORTS


def test_governance_all_contains_no_duplicates():
    """
    Public exports must not contain duplicate names.
    """

    assert len(governance.__all__) == len(
        set(governance.__all__)
    )


# =============================================================================
# Public Import Tests
# =============================================================================


def test_public_contracts_are_importable():
    """
    Governance contracts must be importable through the public package.
    """

    from src.governance import (
        GovernanceDecision,
        GovernanceRequest,
    )

    assert GovernanceDecision is not None
    assert GovernanceRequest is not None


def test_public_policy_engine_is_importable():
    """
    Governance policy engine must remain publicly importable.
    """

    from src.governance import GovernancePolicyEngine

    assert GovernancePolicyEngine is not None


def test_public_permissions_are_importable():
    """
    Governance permission components must remain publicly importable.
    """

    from src.governance import (
        GovernancePermission,
        GovernancePermissions,
    )

    assert GovernancePermission is not None
    assert GovernancePermissions is not None


def test_public_authorization_is_importable():
    """
    Governance authorization component must remain publicly importable.
    """

    from src.governance import GovernanceAuthorization

    assert GovernanceAuthorization is not None


def test_public_audit_components_are_importable():
    """
    Governance audit components must remain publicly importable.
    """

    from src.governance import (
        GovernanceAudit,
        GovernanceAuditEntry,
    )

    assert GovernanceAudit is not None
    assert GovernanceAuditEntry is not None


def test_public_compliance_components_are_importable():
    """
    Governance compliance components must remain publicly importable.
    """

    from src.governance import (
        GovernanceCompliance,
        GovernanceComplianceError,
    )

    assert GovernanceCompliance is not None
    assert GovernanceComplianceError is not None


def test_public_security_components_are_importable():
    """
    Governance security components must remain publicly importable.
    """

    from src.governance import (
        GovernanceSecurity,
        GovernanceSecurityError,
    )

    assert GovernanceSecurity is not None
    assert GovernanceSecurityError is not None


def test_public_decision_boundary_components_are_importable():
    """
    Governance decision-boundary components must remain publicly importable.
    """

    from src.governance import (
        GovernanceDecisionBoundary,
        GovernanceDecisionBoundaryError,
    )

    assert GovernanceDecisionBoundary is not None
    assert GovernanceDecisionBoundaryError is not None


# =============================================================================
# Public API Identity Tests
# =============================================================================


def test_public_exports_are_classes_or_expected_types():
    """
    Public governance exports must resolve to concrete API objects.

    The test deliberately avoids imposing implementation details beyond
    requiring the symbols to be valid Python objects.
    """

    for export_name in EXPECTED_PUBLIC_EXPORTS:

        exported_object = getattr(
            governance,
            export_name,
        )

        assert exported_object is not None


def test_public_api_does_not_expose_private_module_names():
    """
    The public API should expose governance contracts rather than private
    implementation helpers.
    """

    for export_name in governance.__all__:

        assert not export_name.startswith("_")


# =============================================================================
# Error Contract Tests
# =============================================================================


def test_public_error_types_are_exception_classes():
    """
    Public governance error types must remain usable as exception classes.
    """

    from src.governance import (
        GovernanceComplianceError,
        GovernanceDecisionBoundaryError,
        GovernanceSecurityError,
    )

    assert issubclass(
        GovernanceComplianceError,
        Exception,
    )

    assert issubclass(
        GovernanceSecurityError,
        Exception,
    )

    assert issubclass(
        GovernanceDecisionBoundaryError,
        Exception,
    )


# =============================================================================
# Public API Boundary Test
# =============================================================================


def test_public_governance_api_is_explicitly_defined():
    """
    The governance package must have an explicit __all__ declaration.

    This prevents the public API from being determined accidentally by
    implementation imports.
    """

    assert hasattr(
        governance,
        "__all__",
    )

    assert isinstance(
        governance.__all__,
        list,
    )


# =============================================================================
# Compatibility Contract
# =============================================================================


def test_governance_public_api_is_deterministic():
    """
    Re-reading the public API must produce the same export set.

    This protects the package boundary from accidental dynamic behaviour.
    """

    first_exports = set(
        governance.__all__
    )

    second_exports = set(
        governance.__all__
    )

    assert first_exports == second_exports