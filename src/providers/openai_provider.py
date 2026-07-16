"""
===============================================================================
AI Process Analyst
===============================================================================

Module:
    openai_provider.py

Purpose:
    OpenAI implementation of the provider interface.

Responsibilities:
    - Connect to the OpenAI API
    - Submit prompts
    - Return structured responses
    - Report provider health

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
from typing import Any

# =============================================================================
# Third-Party Imports
# =============================================================================

from openai import OpenAI

# =============================================================================
# Project Imports
# =============================================================================

from providers.base_provider import BaseProvider


# =============================================================================
# Classes
# =============================================================================

class OpenAIProvider(BaseProvider):
    """
    OpenAI provider implementation.
    """

    def __init__(
        self,
        configuration: dict[str, Any]
    ) -> None:

        super().__init__(configuration)

        api_key = os.getenv(
            configuration["api_key_environment_variable"]
        )

        if not api_key:
            raise RuntimeError(
                "OpenAI API key not found. "
                "Set the OPENAI_API_KEY environment variable."
            )

        self.client = OpenAI(api_key=api_key)

    # -------------------------------------------------------------------------

    def provider_name(self) -> str:
        """
        Return the provider name.
        """

        return "OpenAI"

    # -------------------------------------------------------------------------

    def health_check(self) -> bool:
        """
        Verify that the provider is available.
        """

        try:

            self.client.models.list()

            return True

        except Exception:

            return False

    # -------------------------------------------------------------------------

    def generate_response(
        self,
        prompt: str
    ) -> str:
        """
        Generate a response from OpenAI.
        """

        response = self.client.responses.create(

            model=self.configuration["model"],

            input=prompt

        )

        return response.output_text