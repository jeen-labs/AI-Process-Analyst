"""
AI Process Analyst

Module:
tests.test_orchestration_public_api

Purpose:
Define and protect the stable public API of the enterprise
orchestration engine.

Phase:
Milestone 3 - Enterprise AI Orchestration Layer
Phase 3.11.1 - Define Stable Orchestration Public API

Public API:
    OrchestrationEngine.orchestrate()
    OrchestrationEngine.create_plan()
    OrchestrationEngine.is_allowed()
    OrchestrationEngine.has_agent()

This test intentionally verifies the existing public surface without
changing the implementation.

The purpose is backward-compatibility protection for future phases.
"""

import inspect

from src.orchestration.orchestration_engine import (
    OrchestrationEngine,
    OrchestrationEngineError,
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