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
    - Prepare requests
    - Abstract AI providers
    - Return generated responses

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

from config_loader import ConfigLoader

# =============================================================================
# Classes
# =============================================================================


class LLMClient:
    """
    Generic Large Language Model client.

    Configuration is loaded from config/llm_config.yaml.
    """

    def __init__(self) -> None:
        """
        Initialise the LLM client.
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
        Generate a response from the configured LLM.

        During development this method returns a mock JSON response.
        Future versions will call the configured AI provider.

        Parameters
        ----------
        prompt : str

        Returns
        -------
        str
            JSON string representing the extracted process.
        """

        if not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        #
        # Mock response
        #
        # This simulates the JSON that will eventually be returned
        # by OpenAI or Gemini.
        #

        return """
{
    "process_name": "Customer Onboarding",

    "process_description": "End-to-end onboarding of a new customer.",

    "process_owner": "Customer Operations",

    "activities": [

        {
            "id": "ACT-001",
            "name": "Receive Customer Application",
            "actor": "Customer",
            "type": "Start"
        },

        {
            "id": "ACT-002",
            "name": "Verify Submitted Documents",
            "actor": "Operations Officer",
            "type": "Task"
        },

        {
            "id": "ACT-003",
            "name": "Approve Customer",
            "actor": "Operations Manager",
            "type": "Approval"
        },

        {
            "id": "ACT-004",
            "name": "Create Customer Account",
            "actor": "CRM System",
            "type": "System Task"
        },

        {
            "id": "ACT-005",
            "name": "Send Welcome Email",
            "actor": "CRM System",
            "type": "End"
        }

    ],

    "business_rules": [

        "Customer identity must be verified.",

        "Mandatory documents must be submitted.",

        "Manager approval is required before account creation."

    ]
}
"""

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

    prompt = (
        "Summarise the Customer Onboarding process."
    )

    response = client.generate_response(prompt)

    print("=" * 70)
    print("LLM RESPONSE")
    print("=" * 70)

    print(response)