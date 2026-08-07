"""
===============================================================================
AI Process Analyst
===============================================================================

Module:
    tests/test_llm_client.py

Purpose:
    Automated tests for the Enterprise LLMClient.

Phase:
    Milestone 3 - Enterprise AI Orchestration Layer
    Phase 3.2 - Refactor LLM Client
===============================================================================
"""

import pytest

from src.orchestration.llm_client import LLMClient


# =============================================================================
# Test Doubles
# =============================================================================


class MockLLMClient:
    """Simple mock client used to verify orchestration behaviour."""

    def __init__(self) -> None:
        self.calls = []

    def generate(self, prompt: str) -> str:
        """Return a deterministic mock response."""

        self.calls.append(prompt)

        return "mock-llm-response"


# =============================================================================
# Initialisation Tests
# =============================================================================


def test_llm_client_initialises_with_client() -> None:
    """LLMClient should accept a valid underlying client."""

    mock_client = MockLLMClient()

    client = LLMClient(mock_client)

    assert client.get_client() is mock_client


def test_llm_client_rejects_none_client() -> None:
    """LLMClient should reject a missing underlying client."""

    with pytest.raises(ValueError, match="cannot be None"):
        LLMClient(None)


# =============================================================================
# Generation Tests
# =============================================================================


def test_generate_delegates_to_underlying_client() -> None:
    """LLMClient should delegate prompt execution to the underlying client."""

    mock_client = MockLLMClient()
    client = LLMClient(mock_client)

    response = client.generate(
        "Analyse this business process."
    )

    assert response == "mock-llm-response"
    assert mock_client.calls == [
        "Analyse this business process."
    ]


def test_generate_returns_raw_response() -> None:
    """LLMClient should return the provider response without modification."""

    mock_client = MockLLMClient()
    client = LLMClient(mock_client)

    response = client.generate("Test prompt")

    assert response == "mock-llm-response"


# =============================================================================
# Validation Tests
# =============================================================================


def test_generate_rejects_non_string_prompt() -> None:
    """LLMClient should reject prompts that are not strings."""

    mock_client = MockLLMClient()
    client = LLMClient(mock_client)

    with pytest.raises(TypeError, match="must be a string"):
        client.generate(123)


def test_generate_rejects_empty_prompt() -> None:
    """LLMClient should reject an empty prompt."""

    mock_client = MockLLMClient()
    client = LLMClient(mock_client)

    with pytest.raises(ValueError, match="cannot be empty"):
        client.generate("")


def test_generate_rejects_whitespace_prompt() -> None:
    """LLMClient should reject a whitespace-only prompt."""

    mock_client = MockLLMClient()
    client = LLMClient(mock_client)

    with pytest.raises(ValueError, match="cannot be empty"):
        client.generate("   ")


def test_generate_preserves_prompt() -> None:
    """LLMClient should pass the prompt to the underlying client unchanged."""

    mock_client = MockLLMClient()
    client = LLMClient(mock_client)

    prompt = "  Analyse this process.  "

    client.generate(prompt)

    assert mock_client.calls == [prompt]


# =============================================================================
# Integration Boundary Tests
# =============================================================================


def test_get_client_returns_underlying_client() -> None:
    """The underlying client should remain accessible for migration support."""

    mock_client = MockLLMClient()
    client = LLMClient(mock_client)

    assert client.get_client() is mock_client
