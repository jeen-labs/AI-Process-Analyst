"""
===============================================================================
AI Process Analyst
===============================================================================

Module:
    llm_client.py

Purpose:
    Provide a generic interface for interacting with Large Language Models (LLMs).

Responsibilities:
    - Send prompts to an LLM
    - Receive AI responses
    - Abstract the underlying AI provider
    - Provide a consistent interface for future integrations

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

from typing import Optional

# =============================================================================
# Third-Party Imports
# =============================================================================

# (None)
#
# Future:
#   openai
#   google-generativeai
#   anthropic
#   ollama

# =============================================================================
# Project Imports
# =============================================================================

# (None)

# =============================================================================
# Module Constants
# =============================================================================

DEFAULT_MODEL = "Not Configured"

# =============================================================================
# Classes
# =============================================================================


class LLMClient:
    """
    Generic client for communicating with Large Language Models.

    The implementation is provider-independent.
    """

    def __init__(self, model_name: Optional[str] = None) -> None:
        """
        Initialise the LLM client.

        Parameters
        ----------
        model_name : Optional[str]
            Name of the configured model.
        """

        self.model_name = model_name or DEFAULT_MODEL

    def generate_response(self, prompt: str) -> str:
        """
        Generate a response from the configured LLM.

        Parameters
        ----------
        prompt : str
            Prompt to send to the language model.

        Returns
        -------
        str
            AI-generated response.
        """

        if not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        #
        # Placeholder implementation.
        #
        # Future versions will:
        #
        # 1. Load configuration.
        # 2. Connect to the configured provider.
        # 3. Send the prompt.
        # 4. Return the generated response.
        #

        return (
            "LLM integration is not yet implemented.\n\n"
            f"Configured Model: {self.model_name}\n\n"
            "Prompt Received:\n"
            f"{prompt}"
        )


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":

    client = LLMClient()

    sample_prompt = (
        "Summarise the customer onboarding process."
    )

    response = client.generate_response(sample_prompt)

    print("=" * 70)
    print("LLM CLIENT TEST")
    print("=" * 70)
    print(response)