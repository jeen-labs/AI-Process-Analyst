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
    - Validate prompts
    - Abstract AI providers
    - Return AI responses
    - Use a mock provider during development

Author:
    Jeen Labs

Version:
    0.3.0

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
from mock_llm_response import generate_mock_response

# =============================================================================
# Classes
# =============================================================================


class LLMClient:
    """
    Generic Large Language Model client.

    This class acts as a provider adapter.

    It does not know anything about the enterprise process schema.
    During development it simply returns a mock response.
    Later versions will communicate with OpenAI, Gemini, Ollama,
    Azure OpenAI and other providers.
    """

    def __init__(self) -> None:
        """
        Initialise the configured LLM provider.
        """

        loader = ConfigLoader()

        configuration = loader.load_llm_config()

        self.provider = configuration.get("provider")

        self.model = configuration.get("model")

        self.temperature = configuration.get("temperature")

        self.max_tokens = configuration.get("max_tokens")

        self.timeout = configuration.get("timeout_seconds")

        self.response_format = configuration.get("response_format")

    # -------------------------------------------------------------------------

    def generate_response(self, prompt: str) -> str:
        """
        Generate a response from the configured provider.

        Parameters
        ----------
        prompt : str
            Prompt sent to the language model.

        Returns
        -------
        str
            JSON response.
        """

        if not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        #
        # Development Mode
        #
        # At the moment we always return a deterministic mock response.
        #
        # Future versions:
        #
        # if self.provider == "openai":
        #     return self._call_openai(prompt)
        #
        # elif self.provider == "gemini":
        #     return self._call_gemini(prompt)
        #
        # elif self.provider == "ollama":
        #     return self._call_ollama(prompt)
        #
        # else:
        #     raise ValueError(...)
        #

        return generate_mock_response()

    # -------------------------------------------------------------------------

    def get_configuration(self) -> dict[str, Any]:
        """
        Return the active LLM configuration.
        """

        return {
            "provider": self.provider,
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "timeout": self.timeout,
            "response_format": self.response_format,
        }


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

    prompt = "Summarise the Customer Onboarding process."

    response = client.generate_response(prompt)

    print("=" * 70)
    print("MOCK LLM RESPONSE")
    print("=" * 70)

    print(response)