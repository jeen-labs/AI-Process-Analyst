"""
===============================================================================
AI Process Analyst
===============================================================================

Module:
    base_provider.py

Purpose:
    Define the provider-independent contract implemented by every LLM
    service provider.

Responsibilities:
    - Provide a stable common provider contract
    - Enable provider interchangeability
    - Keep orchestration independent from vendor-specific SDKs
    - Support current and future providers
    - Provide common provider configuration handling

Supported / Planned Providers
-----------------------------
- Mock
- OpenAI
- Gemini
- Anthropic / Claude
- Ollama
- Azure OpenAI
- Local / self-hosted models
- Future providers

Architecture
------------

                    Application
                         |
                         v
                 Provider-independent
                    orchestration
                         |
                         v
                   BaseProvider
                         |
          +--------------+--------------+
          |              |              |
          v              v              v
       OpenAI          Gemini          Mock
          |
          +--------------------+
          |                    |
          v                    v
      Claude/Anthropic      Ollama
      Azure OpenAI          Future providers

Provider-specific SDK and API behaviour must remain isolated inside each
provider implementation.

Author:
    Jeen Labs

Version:
    0.3.0

Status:
    Development
===============================================================================
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseProvider(ABC):
    """
    Abstract base class for every Large Language Model provider.

    This class deliberately contains no provider-specific SDK logic.

    Every provider implementation must expose the same small contract:

        generate_response(prompt)
        health_check()
        provider_name()

    This allows the rest of the application to work with OpenAI, Gemini,
    Anthropic, Ollama, Azure OpenAI, local models, or future providers
    without changing the orchestration layer.
    """

    def __init__(
        self,
        configuration: dict[str, Any],
    ) -> None:
        """
        Initialise the provider with its provider-specific configuration.

        Parameters
        ----------
        configuration:
            Configuration supplied by the application configuration layer.

        Notes
        -----
        The base class intentionally does not interpret provider-specific
        configuration values such as API keys, model names, endpoints, or
        SDK settings. Those remain the responsibility of the concrete
        provider implementation.
        """

        if configuration is None:
            raise ValueError(
                "Provider configuration cannot be None."
            )

        if not isinstance(configuration, dict):
            raise TypeError(
                "Provider configuration must be a dictionary."
            )

        self.configuration = configuration

    # =========================================================================
    # Provider Contract
    # =========================================================================

    @abstractmethod
    def generate_response(
        self,
        prompt: str,
    ) -> str:
        """
        Generate an LLM response for the supplied prompt.

        Parameters
        ----------
        prompt:
            Fully constructed prompt supplied by the orchestration layer.

        Returns
        -------
        str
            Provider-generated response.

        Raises
        ------
        ValueError
            If the prompt is invalid or empty.

        RuntimeError
            If the provider cannot generate a usable response.

        Notes
        -----
        The concrete provider is responsible for translating this common
        operation into its native SDK/API call.
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
            True when the provider is available and usable; otherwise False.

        Notes
        -----
        The implementation is provider-specific. For example, a cloud
        provider may perform an API request while a local provider may check
        whether its local service is reachable.
        """

        raise NotImplementedError

    # -------------------------------------------------------------------------

    @abstractmethod
    def provider_name(self) -> str:
        """
        Return the human-readable provider name.

        Returns
        -------
        str
            Human-readable provider name.

        Examples
        --------
        "OpenAI"
        "Google Gemini"
        "Anthropic Claude"
        "Ollama"
        """

        raise NotImplementedError

    # =========================================================================
    # Common Provider Metadata / Configuration Helpers
    # =========================================================================

    def get_configuration(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Retrieve a provider configuration value.

        This helper provides a consistent way for provider implementations
        to read optional configuration values while keeping the actual
        interpretation inside the concrete provider.

        Parameters
        ----------
        key:
            Configuration key.

        default:
            Value returned when the key is not present.

        Returns
        -------
        Any
            Configured value or the supplied default.
        """

        return self.configuration.get(
            key,
            default,
        )

    # -------------------------------------------------------------------------

    def get_provider_identifier(self) -> str:
        """
        Return a stable machine-readable provider identifier.

        By default this is derived from provider_name().

        Concrete providers may override this method if their stable
        identifier differs from their human-readable name.

        Returns
        -------
        str
            Normalised provider identifier.

        Examples
        --------
        "openai"
        "gemini"
        "anthropic"
        "ollama"
        """

        return self.provider_name().strip().lower()

    # -------------------------------------------------------------------------

    def is_configuration_empty(self) -> bool:
        """
        Return True when no provider configuration has been supplied.

        Returns
        -------
        bool
            True when configuration is empty, otherwise False.
        """

        return len(self.configuration) == 0