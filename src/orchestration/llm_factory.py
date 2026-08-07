"""
===============================================================================
AI Process Analyst
===============================================================================

Module:
    orchestration.llm_factory

Purpose:
    Provide the enterprise orchestration layer with a provider-independent
    factory for creating LLM clients.

Responsibilities:
    - Accept a configured provider/client
    - Create an orchestration LLMClient
    - Keep provider construction separate from orchestration logic
    - Provide a stable factory interface
    - Validate factory inputs

Architecture:
    Enterprise AI Orchestration Layer

This component does NOT:

    - Execute LLM requests directly
    - Build prompts
    - Parse LLM responses
    - Contain provider-specific business logic
    - Implement retry logic

The factory is intentionally lightweight. Its purpose is to establish a
stable seam between provider configuration and the orchestration layer.
===============================================================================
"""

# =============================================================================
# Imports
# =============================================================================

from typing import Any

from src.orchestration.llm_client import LLMClient


# =============================================================================
# LLM Factory
# =============================================================================


class LLMFactory:
    """
    Factory for creating provider-independent orchestration LLM clients.

    The factory receives an already-configured provider/client and wraps it
    with the enterprise orchestration LLMClient abstraction.

    Provider-specific configuration remains outside this class.
    """

    def __init__(self, client: Any) -> None:
        """
        Initialise the LLM factory.

        Args:
            client:
                Configured underlying LLM client/provider.

        Raises:
            ValueError:
                If client is None.
        """

        if client is None:
            raise ValueError("client must not be None")

        self._client = client

    # =========================================================================
    # Factory Methods
    # =========================================================================

    def create(self) -> LLMClient:
        """
        Create an orchestration LLMClient.

        Returns:
            LLMClient:
                A provider-independent orchestration client wrapping the
                configured underlying client.
        """

        return LLMClient(self._client)

    # =========================================================================
    # Accessor
    # =========================================================================

    def get_client(self) -> Any:
        """
        Return the configured underlying client.

        Returns:
            Any:
                The original provider/client supplied to the factory.
        """

        return self._client


# =============================================================================
# Convenience Function
# =============================================================================


def create_llm_client(client: Any) -> LLMClient:
    """
    Create an orchestration LLMClient from an underlying provider/client.

    This convenience function provides a simple functional entry point while
    keeping the factory implementation available for dependency injection
    and future provider-selection logic.

    Args:
        client:
            Configured underlying LLM client/provider.

    Returns:
        LLMClient:
            Provider-independent orchestration client.

    Raises:
        ValueError:
            If client is None.
    """

    factory = LLMFactory(client)
    return factory.create()