"""
===============================================================================
AI Process Analyst
===============================================================================

Module:
    orchestration.llm_client

Purpose:
    Provide the enterprise orchestration layer with a stable interface for
    Large Language Model (LLM) execution.

Responsibilities:
    - Accept a fully constructed prompt
    - Delegate LLM execution to the configured LLM client
    - Return the raw LLM response
    - Keep orchestration concerns separate from provider implementation
    - Provide basic input validation
    - Preserve a provider-independent orchestration interface

Architecture:
    Enterprise AI Orchestration Layer

This component does NOT:
    - Implement a specific LLM provider
    - Manage provider-specific configuration
    - Build prompts
    - Parse LLM responses
    - Normalize LLM responses
    - Perform enterprise process enrichment
    - Execute business rules

Provider-specific behavior remains in the provider layer and will be
refactored separately in subsequent phases.

Phase:
    Milestone 3 - Enterprise AI Orchestration Layer
    Phase 3.2 - Refactor LLM Client

Author:
    Jeen Labs

Version:
    0.1.0

Status:
    Development
===============================================================================
"""

# =============================================================================
# Standard Library Imports
# =============================================================================

from typing import Any


# =============================================================================
# Classes
# =============================================================================


class LLMClient:
    """
    Enterprise orchestration interface for LLM execution.

    The orchestration layer should depend on this interface rather than
    directly depending on a specific LLM provider.

    Parameters
    ----------
    client : Any
        Underlying LLM client responsible for performing the actual model
        invocation.
    """

    def __init__(self, client: Any) -> None:
        """
        Initialise the enterprise LLM client.

        Parameters
        ----------
        client : Any
            Underlying LLM execution client.

        Raises
        ------
        ValueError
            If no client is provided.
        """

        if client is None:
            raise ValueError(
                "LLM client cannot be None."
            )

        self._client = client

    # =========================================================================
    # Public API
    # =========================================================================

    def generate(self, prompt: str) -> Any:
        """
        Execute an LLM request using the supplied prompt.

        Parameters
        ----------
        prompt : str
            Fully constructed prompt.

        Returns
        -------
        Any
            Raw response returned by the underlying LLM client.

        Raises
        ------
        TypeError
            If prompt is not a string.

        ValueError
            If prompt is empty or contains only whitespace.
        """

        if not isinstance(prompt, str):
            raise TypeError(
                "Prompt must be a string."
            )

        if not prompt.strip():
            raise ValueError(
                "Prompt cannot be empty."
            )

        return self._client.generate(prompt)

    def get_client(self) -> Any:
        """
        Return the underlying LLM client.

        This method is intentionally provided for controlled integration
        during the migration from the legacy architecture.

        Returns
        -------
        Any
            Underlying LLM client.
        """

        return self._client


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":

    class ExampleClient:
        """Simple example client used for manual testing."""

        def generate(self, prompt: str) -> str:
            """Return a simple mock response."""

            return f"LLM response for: {prompt}"


    client = LLMClient(
        ExampleClient()
    )

    response = client.generate(
        "Analyse the following business process."
    )

    print("=" * 80)
    print("LLM CLIENT PREVIEW")
    print("=" * 80)
    print(response)
