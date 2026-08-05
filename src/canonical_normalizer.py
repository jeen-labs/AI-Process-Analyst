"""
===============================================================================
Canonical Process Normalizer
===============================================================================

Purpose
-------
Converts provider-specific process extraction output into the Enterprise
Canonical Process Model.

All downstream components (validator, ontology, enrichment, BPMN generation,
analytics, AI recommendations, governance) consume ONLY the canonical model.

Supported Providers
-------------------
- OpenAI
- Gemini
- Anthropic
- Azure OpenAI
- Ollama
- Manual Import
- Future Providers

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
    Main orchestration engine.

    Provider Response
            │
            ▼
      Provider Adapter
            │
            ▼
    Canonical Enterprise Model
    """   

    def __init__(self) -> None:

        self._providers: Dict[str, BaseProviderNormalizer] = {}

        self._register_builtin_providers()

    # ------------------------------------------------------------------
    # Built-in Providers
    # ------------------------------------------------------------------

    def _register_builtin_providers(self) -> None:
        """
        Register all built-in provider normalizers.

        Future providers only need to be added here.
        """

        self.register_provider(
            "gemini",
            GeminiNormalizer(),
        )

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register_provider(
        self,
        provider_name: str,
        adapter: BaseProviderNormalizer,
    ) -> None:
        """
        Register a provider adapter.
        """

        self._providers[provider_name.lower()] = adapter

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def normalize(
        self,
        provider_name: str,
        provider_response: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Normalize any provider response into the canonical model.
        """

        provider_name = provider_name.lower()

        if provider_name not in self._providers:
            raise ValueError(
                f"No canonical normalizer registered for provider "
                f"'{provider_name}'."
            )

        adapter = self._providers[provider_name]

        canonical = adapter.normalize(deepcopy(provider_response))

        return canonical

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    @property
    def registered_providers(self) -> List[str]:
        """
        Returns registered provider names.
        """

        return sorted(self._providers.keys())