"""
===============================================================================
AI Process Analyst
===============================================================================

Module:
    llm_factory.py

Purpose:
    Create the appropriate Large Language Model (LLM) provider based on the
    active configuration.

Responsibilities:
    - Read provider configuration
    - Instantiate the correct provider
    - Decouple the application from provider-specific implementations

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

from typing import Any

# =============================================================================
# Project Imports
# =============================================================================

from providers.base_provider import BaseProvider
from providers.mock_provider import MockProvider
from providers.openai_provider import OpenAIProvider
from providers.gemini_provider import GeminiProvider

#
# Future Providers
#
# from providers.gemini_provider import GeminiProvider
# from providers.ollama_provider import OllamaProvider
# from providers.azure_openai_provider import AzureOpenAIProvider
# from providers.anthropic_provider import AnthropicProvider


# =============================================================================
# Classes
# =============================================================================


class LLMFactory:
    """
    Factory responsible for constructing the configured
    Large Language Model provider.
    """

    @staticmethod
    def create_provider(
        configuration: dict[str, Any]
    ) -> BaseProvider:
        """
        Create an LLM provider.

        Parameters
        ----------
        configuration : dict

        Returns
        -------
        BaseProvider
        """

        provider = configuration.get(
            "provider",
            "mock"
        ).lower()

        # ---------------------------------------------------------------------
        # Gemini Provider
        # ---------------------------------------------------------------------

        if provider == "gemini":
            return GeminiProvider(configuration)

        # ---------------------------------------------------------------------
        # Mock Provider
        # ---------------------------------------------------------------------

        if provider == "mock":

            return MockProvider(configuration)

        # ---------------------------------------------------------------------
        # OpenAI Provider
        # ---------------------------------------------------------------------

        if provider == "openai":

            return OpenAIProvider(configuration)

        # ---------------------------------------------------------------------
        # Future Providers
        # ---------------------------------------------------------------------

        #
        # if provider == "gemini":
        #     return GeminiProvider(configuration)
        #
        # if provider == "ollama":
        #     return OllamaProvider(configuration)
        #
        # if provider == "azure":
        #     return AzureOpenAIProvider(configuration)
        #
        # if provider == "anthropic":
        #     return AnthropicProvider(configuration)
        #

        raise ValueError(
            f"Unsupported LLM provider: '{provider}'."
        )