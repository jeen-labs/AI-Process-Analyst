"""
===============================================================================
AI Process Analyst
===============================================================================

Module:
    tests/test_llm_factory.py

Purpose:
    Automated tests for the Enterprise LLMFactory.

Phase:
    Milestone 3 - Enterprise AI Orchestration Layer
    Phase 3.4 - Refactor LLM Factory
===============================================================================
"""

# =============================================================================
# Imports
# =============================================================================

import pytest

from src.orchestration.llm_client import LLMClient
from src.orchestration.llm_factory import (
    LLMFactory,
    create_llm_client,
)


# =============================================================================
# Test Doubles
# =============================================================================


class FakeLLMClient:
    """Minimal fake underlying LLM client used for factory tests."""

    def generate(self, prompt: str):
        """Return a deterministic fake response."""
        return {"response": prompt}


# =============================================================================
# Factory Initialisation Tests
# =============================================================================


def test_llm_factory_initialises_with_client():
    """
    The factory should retain the supplied underlying client.
    """

    client = FakeLLMClient()

    factory = LLMFactory(client)

    assert factory.get_client() is client


def test_llm_factory_rejects_none_client():
    """
    The factory should reject a missing underlying client.
    """

    with pytest.raises(ValueError, match="client must not be None"):
        LLMFactory(None)


# =============================================================================
# Factory Creation Tests
# =============================================================================


def test_create_returns_llm_client():
    """
    create() should return the orchestration LLMClient abstraction.
    """

    client = FakeLLMClient()

    factory = LLMFactory(client)

    result = factory.create()

    assert isinstance(result, LLMClient)


def test_create_wraps_original_client():
    """
    The created LLMClient should contain the original underlying client.
    """

    client = FakeLLMClient()

    factory = LLMFactory(client)

    result = factory.create()

    assert result.get_client() is client


def test_create_returns_new_llm_client_instance():
    """
    Each create() call should produce a new orchestration wrapper.
    """

    client = FakeLLMClient()

    factory = LLMFactory(client)

    first = factory.create()
    second = factory.create()

    assert first is not second


def test_create_preserves_underlying_client():
    """
    Multiple orchestration clients should wrap the same underlying client.
    """

    client = FakeLLMClient()

    factory = LLMFactory(client)

    first = factory.create()
    second = factory.create()

    assert first.get_client() is client
    assert second.get_client() is client


# =============================================================================
# Convenience Function Tests
# =============================================================================


def test_create_llm_client_returns_llm_client():
    """
    The convenience function should return an orchestration LLMClient.
    """

    client = FakeLLMClient()

    result = create_llm_client(client)

    assert isinstance(result, LLMClient)


def test_create_llm_client_wraps_original_client():
    """
    The convenience function should preserve the supplied client.
    """

    client = FakeLLMClient()

    result = create_llm_client(client)

    assert result.get_client() is client


def test_create_llm_client_rejects_none_client():
    """
    The convenience function should reject a missing client.
    """

    with pytest.raises(ValueError, match="client must not be None"):
        create_llm_client(None)