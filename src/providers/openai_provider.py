"""
===============================================================================
AI Process Analyst
===============================================================================

Module:
    openai_provider.py

Purpose:
    OpenAI implementation of the common LLM provider contract.

Responsibilities:
    - Connect to the OpenAI API
    - Submit prompts
    - Return generated responses
    - Report provider health
    - Isolate OpenAI-specific implementation details

The rest of the application must interact with this provider only through
BaseProvider.

Author:
    Jeen Labs

Version:
    0.3.0

Status:
    Development
===============================================================================
"""

from __future__ import annotations

import os
from typing import Any

from openai import OpenAI

from src.providers.base_provider import BaseProvider


class OpenAIProvider(BaseProvider):
    """
    OpenAI implementation of the common provider contract.

    Provider-specific API behaviour is intentionally isolated inside this
    class so that the orchestration layer remains provider-independent.
    """

    PROVIDER_NAME = "OpenAI"

    DEFAULT_API_KEY_ENVIRONMENT_VARIABLE = "OPENAI_API_KEY"

    def __init__(
        self,
        configuration: dict[str, Any],
    ) -> None:
        """
        Initialise the OpenAI provider.

        Parameters
        ----------
        configuration:
            Provider-specific configuration.

        Raises
        ------
        RuntimeError
            If the required API key cannot be found.
        """

        super().__init__(configuration)

        api_key_environment_variable = configuration.get(
            "api_key_environment_variable",
            self.DEFAULT_API_KEY_ENVIRONMENT_VARIABLE,
        )

        api_key = os.getenv(
            api_key_environment_variable
        )

        if not api_key:
            raise RuntimeError(
                "OpenAI API key not found. "
                f"Set the {api_key_environment_variable} "
                "environment variable."
            )

        self.client = OpenAI(
            api_key=api_key
        )

        self.model = configuration.get(
            "model",
            "gpt-4o-mini",
        )

    # ------------------------------------------------------------------
    # Provider Contract
    # ------------------------------------------------------------------

    def provider_name(self) -> str:
        """
        Return the human-readable provider name.
        """

        return self.PROVIDER_NAME

    # ------------------------------------------------------------------

    def health_check(self) -> bool:
        """
        Verify that the OpenAI service is available.

        Returns
        -------
        bool
            True when the provider responds successfully, otherwise False.
        """

        try:
            self.client.models.list()

            return True

        except Exception:
            return False

    # ------------------------------------------------------------------

    def generate_response(
        self,
        prompt: str,
    ) -> str:
        """
        Generate a response using OpenAI.

        Parameters
        ----------
        prompt:
            Prompt supplied by the orchestration layer.

        Returns
        -------
        str
            Generated response.

        Raises
        ------
        ValueError
            If the prompt is empty.
        RuntimeError
            If OpenAI returns no usable text.
        """

        if not isinstance(prompt, str):
            raise ValueError(
                "Prompt must be a string."
            )

        if not prompt.strip():
            raise ValueError(
                "Prompt cannot be empty."
            )

        response = self.client.responses.create(
            model=self.model,
            input=prompt,
        )

        response_text = response.output_text

        if response_text is None:
            raise RuntimeError(
                "OpenAI returned an empty response."
            )

        response_text = response_text.strip()

        if not response_text:
            raise RuntimeError(
                "OpenAI returned an empty response."
            )

        return response_text