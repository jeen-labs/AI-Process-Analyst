"""
===============================================================================
Canonical Process Normalizer
===============================================================================

Purpose
-------
Converts provider-specific process extraction output into the Enterprise
Canonical Process Model.

All downstream components consume ONLY the canonical model.

Provider Architecture
---------------------
Provider-specific behaviour is isolated behind the
BaseProviderNormalizer contract.

Supported providers are registered through the provider registry and are
identified only by a normalized provider name.

Current built-in provider:
- Gemini

Future providers can be added without changing downstream pipeline
components:

- OpenAI / ChatGPT
- Anthropic / Claude
- Azure OpenAI
- Ollama
- AWS Bedrock
- Google Vertex AI
- Manual Import
- Future providers

Architecture
------------

Provider Response
        |
        v
Provider Adapter Registry
        |
        +----> GeminiNormalizer
        +----> OpenAINormalizer
        +----> AnthropicNormalizer
        +----> OllamaNormalizer
        +----> ...
        |
        v
BaseProviderNormalizer
        |
        v
Enterprise Canonical Process Model
        |
        +----> Validator
        +----> Ontology
        +----> Enrichment
        +----> Rules
        +----> Analytics
        +----> Automation
        +----> Governance
        +----> Orchestration

The CanonicalNormalizer deliberately does not contain provider-specific
transformation logic.

Author:
Jeen Labs
===============================================================================
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List

from src.normalizers.base_normalizer import BaseProviderNormalizer
from src.normalizers.gemini_normalizer import GeminiNormalizer


class CanonicalNormalizer:
    """
    Provider-neutral canonical normalization boundary.

    The CanonicalNormalizer owns the provider adapter registry but does not
    implement provider-specific parsing itself.

    A provider adapter is responsible for converting its native provider
    response into the Enterprise Canonical Process Model.

    Existing callers can continue to use:

        normalizer = CanonicalNormalizer()

        normalizer.normalize(
            "gemini",
            provider_response,
        )

    Additional providers can be registered dynamically:

        normalizer.register_provider(
            "openai",
            OpenAINormalizer(),
        )

    This keeps downstream components independent of provider-specific APIs.
    """

    # =========================================================================
    # Construction
    # =========================================================================

    def __init__(self) -> None:
        """
        Initialise the canonical normalizer.

        The built-in Gemini adapter is registered for backward compatibility
        with the existing public behaviour of the repository.

        Other providers can be registered dynamically through
        register_provider().
        """

        self._providers: Dict[str, BaseProviderNormalizer] = {}

        self._register_builtin_providers()

    # =========================================================================
    # Built-in Providers
    # =========================================================================

    def _register_builtin_providers(self) -> None:
        """
        Register providers that are currently implemented by the repository.

        This method intentionally registers only adapters that actually exist.

        Future providers should be added as independent adapters rather than
        adding provider-specific transformation logic to this class.
        """

        self.register_provider(
            "gemini",
            GeminiNormalizer(),
        )

    # =========================================================================
    # Provider Name Normalization
    # =========================================================================

    @staticmethod
    def _normalize_provider_name(
        provider_name: str,
    ) -> str:
        """
        Normalize a provider identifier.

        Provider names are treated as case-insensitive and surrounding
        whitespace is ignored.

        Examples
        --------
        "Gemini" -> "gemini"
        " GEMINI " -> "gemini"
        "OpenAI" -> "openai"
        """

        if not isinstance(provider_name, str):
            raise ValueError(
                "provider_name must be a string."
            )

        normalized = provider_name.strip().lower()

        if not normalized:
            raise ValueError(
                "provider_name must not be empty."
            )

        return normalized

    # =========================================================================
    # Registration
    # =========================================================================

    def register_provider(
        self,
        provider_name: str,
        adapter: BaseProviderNormalizer,
    ) -> None:
        """
        Register a provider adapter.

        Parameters
        ----------
        provider_name:
            Provider identifier used by callers.

        adapter:
            Provider-specific normalizer implementing
            BaseProviderNormalizer.

        Notes
        -----
        Registration is intentionally generic.

        This allows future providers such as OpenAI, Anthropic, Ollama,
        Azure OpenAI, Bedrock, or other providers to be added without
        changing the canonical normalization API.
        """

        normalized_name = self._normalize_provider_name(
            provider_name
        )

        if not isinstance(
            adapter,
            BaseProviderNormalizer,
        ):
            raise TypeError(
                "adapter must be an instance of "
                "BaseProviderNormalizer."
            )

        self._providers[normalized_name] = adapter

    # =========================================================================
    # Unregistration
    # =========================================================================

    def unregister_provider(
        self,
        provider_name: str,
    ) -> bool:
        """
        Remove a provider adapter from the registry.

        Returns
        -------
        bool
            True when a provider was removed.

        Notes
        -----
        Removing a provider does not affect any other registered provider.
        """

        normalized_name = self._normalize_provider_name(
            provider_name
        )

        return self._providers.pop(
            normalized_name,
            None,
        ) is not None

    # =========================================================================
    # Provider Lookup
    # =========================================================================

    def get_provider(
        self,
        provider_name: str,
    ) -> BaseProviderNormalizer:
        """
        Return the registered adapter for a provider.

        Raises
        ------
        ValueError
            If no adapter is registered for the provider.
        """

        normalized_name = self._normalize_provider_name(
            provider_name
        )

        if normalized_name not in self._providers:
            raise ValueError(
                "No canonical normalizer registered for provider "
                f"'{normalized_name}'."
            )

        return self._providers[normalized_name]

    # =========================================================================
    # Public Normalization API
    # =========================================================================

    def normalize(
        self,
        provider_name: str,
        provider_response: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Normalize any registered provider response.

        Parameters
        ----------
        provider_name:
            Provider identifier.

        provider_response:
            Raw response produced by the provider adapter's upstream service.

        Returns
        -------
        Dict[str, Any]
            Enterprise Canonical Process Model.

        Notes
        -----
        The provider response is deep-copied before being handed to the
        provider adapter.

        Therefore, provider adapters cannot accidentally mutate the original
        caller-owned response through this boundary.
        """

        if not isinstance(
            provider_response,
            dict,
        ):
            raise ValueError(
                "provider_response must be a dictionary."
            )

        adapter = self.get_provider(
            provider_name
        )

        canonical = adapter.normalize(
            deepcopy(provider_response)
        )

        if not isinstance(
            canonical,
            dict,
        ):
            raise ValueError(
                "Provider normalizer must return a dictionary."
            )

        return canonical

    # =========================================================================
    # Provider Registry Inspection
    # =========================================================================

    @property
    def registered_providers(self) -> List[str]:
        """
        Return registered provider identifiers.

        Provider names are returned in deterministic alphabetical order.
        """

        return sorted(
            self._providers.keys()
        )

    # =========================================================================
    # Provider Existence
    # =========================================================================

    def has_provider(
        self,
        provider_name: str,
    ) -> bool:
        """
        Return True when a provider adapter is registered.
        """

        normalized_name = self._normalize_provider_name(
            provider_name
        )

        return normalized_name in self._providers


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":

    normalizer = CanonicalNormalizer()

    print("=" * 80)
    print("CANONICAL NORMALIZER PROVIDER REGISTRY")
    print("=" * 80)

    print(
        "Registered providers:",
        normalizer.registered_providers,
    )