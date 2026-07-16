"""
===============================================================================
AI Process Analyst
===============================================================================

Module:
    llm_client.py

Purpose:
    High-level interface for interacting with the configured Large Language
    Model (LLM).

Responsibilities:
    - Load LLM configuration
    - Create the configured provider
    - Submit prompts
    - Log provider execution
    - Hide provider implementation details

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

import time

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
    Client responsible for interacting with the configured LLM provider.
    """

    def __init__(self) -> None:
        """
        Initialise the configured provider.
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
        Generate a response from the configured provider.

        Parameters
        ----------
        prompt : str

        Returns
        -------
        str
        """

        print()

        print(
            f"Provider : {self.provider.provider_name()}"
        )

        print(
            f"Model    : {self.configuration.get('model', 'Unknown')}"
        )

        start_time = time.perf_counter()

        response = self.provider.generate_response(
            prompt
        )

        elapsed = time.perf_counter() - start_time

        if self.configuration.get(
            "log_response_time",
            False
        ):

            print(
                f"Total response time : "
                f"{elapsed:.2f} seconds"
            )

        return response

    # -------------------------------------------------------------------------

    def health_check(self) -> bool:
        """
        Verify provider connectivity.
        """

        return self.provider.health_check()

    # -------------------------------------------------------------------------

    def provider_name(self) -> str:
        """
        Return active provider name.
        """

        return self.provider.provider_name()

    # -------------------------------------------------------------------------

    def configuration_summary(self) -> dict:
        """
        Return active configuration.
        """

        return self.configuration
    
    def get_configuration(self) -> dict:
        """
        Return the active configuration.
        """

        return self.configuration