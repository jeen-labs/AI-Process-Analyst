"""
===============================================================================
AI Process Analyst
===============================================================================

Module:
    base_provider.py

Purpose:
    Define the abstract interface implemented by every LLM provider.

Responsibilities:
    - Provide a common provider contract
    - Standardise AI interactions
    - Enable provider interchangeability
    - Support future multi-provider architecture

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

from abc import ABC
from abc import abstractmethod
from typing import Any


# =============================================================================
# Classes
# =============================================================================

class BaseProvider(ABC):
    """
    Abstract base class for every Large Language Model provider.

    Every provider (OpenAI, Gemini, Ollama, Azure OpenAI, Anthropic)
    must inherit from this class.
    """

    def __init__(
        self,
        configuration: dict[str, Any]
    ) -> None:
        """
        Initialise the provider.

        Parameters
        ----------
        configuration : dict
            Provider configuration loaded from llm_config.yaml.
        """

        self.configuration = configuration

    # -------------------------------------------------------------------------

    @abstractmethod
    def generate_response(
        self,
        prompt: str
    ) -> str:
        """
        Generate a response from the AI model.

        Parameters
        ----------
        prompt : str

        Returns
        -------
        str
            AI-generated response.
        """

        raise NotImplementedError

    # -------------------------------------------------------------------------

    @abstractmethod
    def health_check(self) -> bool:
        """
        Verify that the provider is available.

        Returns
        -------
        bool
        """

        raise NotImplementedError

    # -------------------------------------------------------------------------

    @abstractmethod
    def provider_name(self) -> str:
        """
        Return the provider name.

        Returns
        -------
        str
        """

        raise NotImplementedError