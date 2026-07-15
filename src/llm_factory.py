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
    0.1.0

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
from providers.openai_provider import OpenAIProvider

# Future imports
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
    Factory responsible for creating the configured LLM provider.
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
            ""
        ).lower()

        if provider == "openai":
            return OpenAIProvider(configuration)

        #
        # Future providers
        #
        # elif provider == "gemini":
        #     return GeminiProvider(configuration)
        #
        # elif provider == "ollama":
        #     return OllamaProvider(configuration)
        #
        # elif provider == "azure":
        #     return AzureOpenAIProvider(configuration)
        #
        # elif provider == "anthropic":
        #     return AnthropicProvider(configuration)
        #

        raise ValueError(
            f"Unsupported LLM provider: {provider}"
        )