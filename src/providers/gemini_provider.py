"""
===============================================================================
AI Process Analyst
===============================================================================

Module:
    gemini_provider.py

Purpose:
    Google Gemini implementation of the common LLM provider interface.

Responsibilities:
    - Connect to Google Gemini
    - Submit prompts
    - Return generated responses
    - Report provider health
    - Use the shared retry mechanism
    - Remain interchangeable with other LLM providers

Architecture
------------
Application
    |
    v
BaseProvider
    |
    +---- GeminiProvider
    +---- OpenAIProvider
    +---- MockProvider
    +---- Future providers
           |
           +---- AnthropicProvider
           +---- OllamaProvider
           +---- AzureOpenAIProvider
           +---- etc.

Provider-specific SDK behaviour remains isolated inside this class.

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
import time
from typing import Any

from google import genai

from src.providers.base_provider import BaseProvider
from src.utils.retry import retry


class GeminiProvider(BaseProvider):
    """
    Google Gemini implementation of the common BaseProvider contract.

    The rest of the application should interact with this class only through
    the BaseProvider interface.

    Gemini-specific SDK details are intentionally isolated here so that adding
    another provider does not require changes to downstream application logic.
    """

    PROVIDER_NAME = "gemini"
    DISPLAY_NAME = "Google Gemini"
    DEFAULT_MODEL = "gemini-flash-latest"
    DEFAULT_API_KEY_ENVIRONMENT_VARIABLE = "GOOGLE_API_KEY"

    def __init__(
        self,
        configuration: dict[str, Any],
    ) -> None:
        """
        Initialise the Gemini provider.

        Parameters
        ----------
        configuration:
            Provider configuration.

        Expected configuration keys
        ----------------------------
        api_key_environment_variable:
            Environment variable containing the Gemini API key.

        model:
            Gemini model identifier.

        retry_attempts:
            Number of retry attempts.

        retry_delay_seconds:
            Initial retry delay.

        retry_exponential_backoff:
            Whether retry delays should use exponential backoff.

        max_retry_delay_seconds:
            Maximum retry delay.

        log_response_time:
            Whether response time should be printed.
        """

        super().__init__(configuration)

        api_key_environment_variable = configuration.get(
            "api_key_environment_variable",
            self.DEFAULT_API_KEY_ENVIRONMENT_VARIABLE,
        )

        api_key = os.getenv(
            api_key_environment_variable,
        )

        if not api_key:
            raise RuntimeError(
                "Google Gemini API key not found. "
                f"Set the {api_key_environment_variable} environment variable."
            )

        self.client = genai.Client(
            api_key=api_key,
        )

        self.model = configuration.get(
            "model",
            self.DEFAULT_MODEL,
        )

    # -------------------------------------------------------------------------
    # Provider Identity
    # -------------------------------------------------------------------------

    def provider_name(self) -> str:
        """
        Return the stable provider identifier.

        This identifier is intended for configuration, routing and factory
        selection.
        """

        return self.PROVIDER_NAME

    # -------------------------------------------------------------------------

    def display_name(self) -> str:
        """
        Return the human-readable provider name.
        """

        return self.DISPLAY_NAME

    # -------------------------------------------------------------------------
    # Response Generation
    # -------------------------------------------------------------------------

    def generate_response(
        self,
        prompt: str,
    ) -> str:
        """
        Generate a response from Google Gemini.

        Provider-specific SDK calls remain isolated inside this method.

        Retries are handled by the shared ``utils.retry`` utility.
        """

        if not isinstance(prompt, str):
            raise TypeError(
                "prompt must be a string."
            )

        if not prompt.strip():
            raise ValueError(
                "Prompt cannot be empty."
            )

        start_time = time.perf_counter()

        def operation() -> str:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
            )

            response_text = getattr(
                response,
                "text",
                None,
            )

            if response_text is None:
                raise RuntimeError(
                    "Gemini returned an empty response."
                )

            response_text = str(
                response_text
            ).strip()

            if not response_text:
                raise RuntimeError(
                    "Gemini returned an empty response."
                )

            return response_text

        response_text = retry(
            operation=operation,
            retry_attempts=self.configuration.get(
                "retry_attempts",
                3,
            ),
            retry_delay_seconds=self.configuration.get(
                "retry_delay_seconds",
                2,
            ),
            exponential_backoff=self.configuration.get(
                "retry_exponential_backoff",
                True,
            ),
            max_retry_delay_seconds=self.configuration.get(
                "max_retry_delay_seconds",
                30,
            ),
        )

        elapsed = time.perf_counter() - start_time

        if self.configuration.get(
            "log_response_time",
            False,
        ):
            print(
                f"Response time: {elapsed:.2f} seconds"
            )

        return response_text

    # -------------------------------------------------------------------------
    # Health Check
    # -------------------------------------------------------------------------

    def health_check(self) -> bool:
        """
        Verify that Gemini is available.

        Returns
        -------
        bool
            True when the provider responds successfully, otherwise False.

        Notes
        -----
        Health checks deliberately do not raise provider-specific exceptions
        to callers. The common provider contract exposes availability as a
        boolean.
        """

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents="Respond with OK.",
            )

            response_text = getattr(
                response,
                "text",
                None,
            )

            return bool(
                response_text
                and str(response_text).strip()
            )

        except Exception:
            return False