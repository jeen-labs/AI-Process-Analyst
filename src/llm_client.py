"""
===============================================================================
AI Process Analyst
===============================================================================

Module:
    llm_client.py

Purpose:
    Provide a provider-independent interface for interacting with
    Large Language Models (LLMs).

Responsibilities:
    - Load LLM configuration
    - Instantiate the configured provider
    - Delegate AI requests
    - Expose provider configuration

Author:
    Jeen Labs

Version:
    0.4.0

Status:
    Development
===============================================================================
"""

# =============================================================================
# Standard Library Imports
# =============================================================================

from typing import Any

# =============================================================================
# Project Imports
# =============================================================================

from config_loader import ConfigLoader
from llm_factory import LLMFactory


# =============================================================================
# Classes
# =============================================================================

class LLMClient:
    """
    Provider-independent LLM client.

    This class acts as a façade over the underlying provider implementation.
    """

    def __init__(self) -> None:
        """
        Initialise the LLM client.
        """

        loader = ConfigLoader()

        self.configuration = loader.load_llm_config()

        self.provider = LLMFactory.create_provider(
            self.configuration
        )

    # -------------------------------------------------------------------------

    def generate_response(
        self,
        prompt: str
    ) -> str:
        """
        Generate an AI response.

        Parameters
        ----------
        prompt : str

        Returns
        -------
        str
        """

        return self.provider.generate_response(prompt)

    # -------------------------------------------------------------------------

    def health_check(self) -> bool:
        """
        Verify provider availability.

        Returns
        -------
        bool
        """

        return self.provider.health_check()

    # -------------------------------------------------------------------------

    def get_configuration(self) -> dict[str, Any]:
        """
        Return the active LLM configuration.

        Returns
        -------
        dict
        """

        return self.configuration


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":

    client = LLMClient()

    print("=" * 70)
    print("ACTIVE LLM CONFIGURATION")
    print("=" * 70)

    configuration = client.get_configuration()

    for key, value in configuration.items():

        print(f"{key:<20} : {value}")

    print()

    print(
        "Provider Health :",
        "OK" if client.health_check() else "FAILED"
    )

    print()

    prompt = (
        "Summarise the Customer Onboarding process."
    )

    response = client.generate_response(prompt)

    print("=" * 70)
    print("LLM RESPONSE")
    print("=" * 70)

    print(response)