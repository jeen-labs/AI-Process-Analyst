"""
===============================================================================
AI Process Analyst
===============================================================================

Module:
    mock_provider.py

Purpose:
    Deterministic local provider implementation used for development,
    testing, demonstrations, and environments where no external LLM
    connection is required.

The mock provider implements the same BaseProvider contract as real
providers such as OpenAI and Gemini.

It does NOT call an external AI service.

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

from providers.base_provider import BaseProvider
from mock_llm_response import generate_mock_response


class MockProvider(BaseProvider):
    """
    Deterministic local implementation of the provider interface.

    This provider exists so the application can execute the complete
    orchestration flow without requiring:

    - an API key
    - an internet connection
    - an external LLM
    - provider-specific infrastructure

    The mock provider follows the same interface as production providers.
    Therefore, application code does not need to know whether the active
    provider is real or simulated.
    """

    PROVIDER_NAME = "Mock"

    def __init__(
        self,
        configuration: dict[str, Any],
    ) -> None:
        """
        Initialise the mock provider.
        """

        super().__init__(configuration)

    # ------------------------------------------------------------------
    # Provider Contract
    # ------------------------------------------------------------------

    def generate_response(
        self,
        prompt: str,
    ) -> str:
        """
        Generate a deterministic mock response.

        Parameters
        ----------
        prompt:
            Prompt supplied by the orchestration layer.

        Returns
        -------
        str
            Deterministic mock response.

        Raises
        ------
        ValueError
            If the prompt is empty or contains only whitespace.
        """

        if not isinstance(prompt, str):
            raise ValueError(
                "Prompt must be a string."
            )

        if not prompt.strip():
            raise ValueError(
                "Prompt cannot be empty."
            )

        return generate_mock_response()

    # ------------------------------------------------------------------

    def health_check(self) -> bool:
        """
        Report that the local mock provider is available.

        Unlike external providers, the mock provider has no network
        dependency, so its health status is deterministic.
        """

        return True

    # ------------------------------------------------------------------

    def provider_name(self) -> str:
        """
        Return the human-readable provider name.
        """

        return self.PROVIDER_NAME