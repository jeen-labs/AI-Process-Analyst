"""
AI Process Analyst

Module:
tests.test_orchestration_public_api

Purpose:
Define and protect the stable public API of the enterprise
orchestration engine and orchestration package.

Phase:
Milestone 3 - Enterprise AI Orchestration Layer
Phase 3.11.4 - Add Orchestration Package Exports

Public API:
OrchestrationEngine.orchestrate()
OrchestrationEngine.create_plan()
OrchestrationEngine.is_allowed()
OrchestrationEngine.has_agent()

Public Package Exports:
OrchestrationEngine
OrchestrationEngineError
OrchestrationResult

These tests intentionally verify the agreed public surface.

The purpose is backward-compatibility protection for future phases.
"""

import inspect

import src.orchestration as orchestration

from src.orchestration import (
    OrchestrationEngine,
    OrchestrationEngineError,
    OrchestrationResult,
)


# =============================================================================
# Stable Public API
# =============================================================================

def test_orchestration_engine_exposes_stable_public_api():
    """
    Verify that the orchestration engine exposes the agreed public methods.

    These methods constitute the stable public orchestration interface for
    Phase 3.11 and later phases.
    """
    expected_methods = {
        "orchestrate",
        "create_plan",
        "is_allowed",
        "has_agent",
    }

    for method_name in expected_methods:
        assert hasattr(
            OrchestrationEngine,
            method_name,
        ), (
            "OrchestrationEngine public API is missing: "
            f"{method_name}"
        )

        method = getattr(
            OrchestrationEngine,
            method_name,
        )

        assert callable(method), (
            "OrchestrationEngine public API member is not callable: "
            f"{method_name}"
        )


# =============================================================================
# Public API Signatures
# =============================================================================

def test_orchestration_engine_public_api_signatures_are_stable():
    """
    Verify the public method signatures.

    The signatures are deliberately checked because callers should be able
    to depend on these interfaces across subsequent orchestration phases.
    """
    orchestrate_signature = inspect.signature(
        OrchestrationEngine.orchestrate
    )

    assert list(
        orchestrate_signature.parameters
    ) == [
        "self",
        "request",
    ]

    create_plan_signature = inspect.signature(
        OrchestrationEngine.create_plan
    )

    assert list(
        create_plan_signature.parameters
    ) == [
        "self",
        "request",
    ]

    is_allowed_signature = inspect.signature(
        OrchestrationEngine.is_allowed
    )

    assert list(
        is_allowed_signature.parameters
    ) == [
        "self",
        "action",
    ]

    has_agent_signature = inspect.signature(
        OrchestrationEngine.has_agent
    )

    assert list(
        has_agent_signature.parameters
    ) == [
        "self",
        "action",
    ]


# =============================================================================
# Public Exception
# =============================================================================

def test_orchestration_engine_error_is_public():
    """
    Verify that the orchestration engine exposes its public exception type.
    """
    assert issubclass(
        OrchestrationEngineError,
        ValueError,
    )


# =============================================================================
# Phase 3.11.4 - Public Package Exports
# =============================================================================

def test_orchestration_engine_is_publicly_exported():
    """
    Verify that OrchestrationEngine is available from the orchestration
    package root.
    """
    assert OrchestrationEngine is orchestration.OrchestrationEngine


def test_orchestration_engine_error_is_publicly_exported():
    """
    Verify that OrchestrationEngineError is available from the orchestration
    package root.
    """
    assert OrchestrationEngineError is orchestration.OrchestrationEngineError


def test_orchestration_result_is_publicly_exported():
    """
    Verify that OrchestrationResult is available from the orchestration
    package root.
    """
    assert OrchestrationResult is orchestration.OrchestrationResult


def test_orchestration_public_exports_are_stable():
    """
    Verify the explicitly supported public package exports.

    __all__ defines the stable package-level public surface for the
    orchestration layer.
    """
    assert orchestration.__all__ == [
        "OrchestrationEngine",
        "OrchestrationEngineError",
        "OrchestrationResult",
    ]

# =============================================================================
# Phase 3.11.4 - Package Exports
# =============================================================================

def test_orchestration_engine_is_publicly_exported():
    from src.orchestration import OrchestrationEngine
    assert OrchestrationEngine is not None


def test_orchestration_engine_error_is_publicly_exported():
    from src.orchestration import OrchestrationEngineError
    assert OrchestrationEngineError is not None


def test_orchestration_result_is_publicly_exported():
    from src.orchestration import OrchestrationResult
    assert OrchestrationResult is not None


def test_orchestration_public_exports_are_stable():
    import src.orchestration as orchestration
    assert orchestration.__all__ == [
        "OrchestrationEngine",
        "OrchestrationEngineError",
        "OrchestrationResult",
    ]
