"""
===============================================================================
AI Process Analyst
===============================================================================

Module:
    gemini_provider.py

Purpose:
    Gemini Large Language Model provider implementation.

Responsibilities:
    - Connect to Google Gemini
    - Submit prompts
    - Return generated responses
    - Report provider health
    - Delegate retry handling to the shared retry utility

Author:
    Jeen Labs

Version:
    0.2.0

Status:
    Development
===============================================================================
"""

# =============================================================================
# Standard Library Imports
# =============================================================================

import os
import time
from typing import Any

# =============================================================================
# Third-Party Imports
# =============================================================================

from google import genai

# =============================================================================
# Project Imports
# =============================================================================

from providers.base_provider import BaseProvider
from utils.retry import retry


# =============================================================================
# Classes
# =============================================================================

class GeminiProvider(BaseProvider):
    """
    Google Gemini provider.
    """

    def __init__(
        self,
        configuration: dict[str, Any]
    ) -> None:

        super().__init__(configuration)

        api_key = os.getenv(
            configuration.get(
                "api_key_environment_variable",
                "GOOGLE_API_KEY"
            )
        )

        if not api_key:

            raise RuntimeError(
                "Google API key not found. "
                "Set the GOOGLE_API_KEY environment variable."
            )

        self.client = genai.Client(api_key=api_key)

        self.model = configuration.get(
            "model",
            "gemini-flash-latest"
        )

    # -------------------------------------------------------------------------

    def generate_response(
        self,
        prompt: str
    ) -> str:
        """
        Generate a response from Gemini.

        Retries are handled by utils.retry.
        """

        start_time = time.perf_counter()

        def operation() -> str:

            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
            )

            if response.text is None:

                raise RuntimeError(
                    "Gemini returned an empty response."
                )

            return response.text

        response_text = retry(

            operation=operation,

            retry_attempts=self.configuration.get(
                "retry_attempts",
                3
            ),

            retry_delay_seconds=self.configuration.get(
                "retry_delay_seconds",
                2
            ),

            exponential_backoff=self.configuration.get(
                "retry_exponential_backoff",
                True
            ),

            max_retry_delay_seconds=self.configuration.get(
                "max_retry_delay_seconds",
                30
            )

        )

        elapsed = time.perf_counter() - start_time

        if self.configuration.get(
            "log_response_time",
            False
        ):

            print(
                f"Response time: {elapsed:.2f} seconds"
            )

        return response_text

    # -------------------------------------------------------------------------

    def health_check(self) -> bool:
        """
        Verify provider availability.
        """

        try:

            self.client.models.generate_content(
                model=self.model,
                contents="Respond with OK."
            )

            return True

        except Exception:

            return False

    # -------------------------------------------------------------------------

    def provider_name(self) -> str:
        """
        Return provider name.
        """

        return "Google Gemini"