"""
===============================================================================
AI Process Analyst
===============================================================================

Module:
    orchestration.llm_client

Purpose:
    Provide the enterprise orchestration layer with a stable, provider-
    independent interface for Large Language Model execution.

Responsibilities:
    - Accept a fully constructed prompt
    - Delegate execution to a configured LLM provider/client
    - Preserve the stable orchestration ``generate()`` API
    - Support the enterprise BaseProvider contract
    - Maintain backward compatibility with legacy clients exposing ``generate``
    - Return the raw provider response
    - Keep provider-specific implementation details outside orchestration

Architecture
------------

                    Orchestration Layer
                           |
                           v
                       LLMClient
                           |
              +------------+------------+
              |                         |
              v                         v
        BaseProvider             Legacy Client
              |                  / Test Double
       +------+------+                  |
       |      |      |                  |
    OpenAI Gemini  Mock             generate()
       |      |      |
       +------+------+
              |
      generate_response()

The orchestration layer depends on this stable interface rather than directly
depending on a specific AI service provider.

Provider-specific behavior remains inside the provider layer.

Phase:
    Milestone 3 - Enterprise AI Orchestration Layer
    Phase 3.2 - Refactor LLM Client

Author:
    Jeen Labs

Version:
    0.2.0

Status:
    Development
===============================================================================
"""

from __future__ import annotations

from typing import Any


class LLMClient:
    """
    Stable enterprise orchestration interface for LLM execution.

    The underlying object may be:

    1. A new enterprise provider implementing::

           generate_response(prompt)

    2. A legacy/test client implementing::

           generate(prompt)

    Supporting both forms allows the provider architecture to evolve without
    breaking existing orchestration components or tests.

    Parameters
    ----------
    client:
        Configured underlying provider/client.
    """

    def __init__(self, client: Any) -> None:
        """
        Initialise the enterprise LLM client.

        Parameters
        ----------
        client:
            Underlying LLM provider/client.

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

    def generate(
        self,
        prompt: str,
    ) -> Any:
        """
        Execute an LLM request using the supplied prompt.

        The preferred enterprise provider contract is:

            generate_response(prompt)

        For backward compatibility, an underlying client exposing:

            generate(prompt)

        is also supported.

        Parameters
        ----------
        prompt:
            Fully constructed prompt.

        Returns
        -------
        Any
            Raw response returned by the underlying provider/client.

        Raises
        ------
        TypeError
            If prompt is not a string.

        ValueError
            If prompt is empty or contains only whitespace.

        AttributeError
            If the underlying object implements neither supported execution
            method.
        """

        if not isinstance(prompt, str):
            raise TypeError(
                "Prompt must be a string."
            )

        if not prompt.strip():
            raise ValueError(
                "Prompt cannot be empty."
            )

        # ---------------------------------------------------------------------
        # Preferred enterprise provider contract
        # ---------------------------------------------------------------------

        generate_response = getattr(
            self._client,
            "generate_response",
            None,
        )

        if callable(generate_response):

            return generate_response(prompt)

        # ---------------------------------------------------------------------
        # Legacy compatibility contract
        # ---------------------------------------------------------------------

        generate = getattr(
            self._client,
            "generate",
            None,
        )

        if callable(generate):

            return generate(prompt)

        # ---------------------------------------------------------------------
        # Invalid underlying client
        # ---------------------------------------------------------------------

        raise AttributeError(
            "Underlying LLM client must implement either "
            "'generate_response(prompt)' or 'generate(prompt)'."
        )

    # =========================================================================
    # Accessor
    # =========================================================================

    def get_client(self) -> Any:
        """
        Return the underlying provider/client.

        This remains available during the migration from the legacy
        architecture and for controlled dependency-injection scenarios.

        Returns
        -------
        Any
            The original underlying provider/client.
        """

        return self._client


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":

    class ExampleProvider:
        """
        Minimal provider example using the new enterprise contract.
        """

        def generate_response(
            self,
            prompt: str,
        ) -> str:
            """
            Return a deterministic example response.
            """

            return f"LLM response for: {prompt}"

    client = LLMClient(
        ExampleProvider()
    )

    response = client.generate(
        "Analyse the following business process."
    )

    print("=" * 80)
    print("LLM CLIENT PREVIEW")
    print("=" * 80)
    print(response)
