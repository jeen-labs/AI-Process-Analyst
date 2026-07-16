"""
===============================================================================
AI Process Analyst
===============================================================================

Module:
    mock_provider.py

Purpose:
    Mock LLM provider used during development and testing.

Responsibilities:
    - Simulate an LLM response
    - Return enterprise process JSON
    - Allow the platform to run without an API key

Author:
    Jeen Labs

Version:
    0.1.0

Status:
    Development
===============================================================================
"""

# =============================================================================
# Project Imports
# =============================================================================

from providers.base_provider import BaseProvider
from mock_llm_response import generate_mock_response


# =============================================================================
# Classes
# =============================================================================


class MockProvider(BaseProvider):
    """
    Mock implementation of an LLM provider.

    This provider returns deterministic JSON without making
    any external API calls.
    """

    def __init__(self, configuration: dict) -> None:
        """
        Initialise the mock provider.
        """

        self.configuration = configuration

    # -------------------------------------------------------------------------

    def generate_response(
        self,
        prompt: str
    ) -> str:
        """
        Return a mock enterprise process.

        Parameters
        ----------
        prompt : str

        Returns
        -------
        str
        """

        if not prompt.strip():

            raise ValueError(
                "Prompt cannot be empty."
            )

        return generate_mock_response()