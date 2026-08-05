"""
===============================================================================
Base Provider Normalizer
===============================================================================

Purpose
-------
Defines the abstract interface that every provider-specific normalizer must
implement.

Every supported provider (Gemini, OpenAI, Anthropic, Azure OpenAI, Ollama,
etc.) converts its native response into the Enterprise Canonical Process Model.

Author:
Jeen Labs
===============================================================================
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from copy import deepcopy
from typing import Any, Dict


class BaseProviderNormalizer(ABC):
    """
    Abstract base class for all provider normalizers.

    Every provider-specific implementation is responsible for translating
    provider-specific JSON into the Enterprise Canonical Process Model.
    """

    def __init__(self, provider_name: str) -> None:
        self.provider_name = provider_name

    @abstractmethod
    def normalize(
        self,
        provider_response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Convert a provider response into the canonical enterprise model.

        Parameters
        ----------
        provider_response
            Raw JSON returned by the provider.

        Returns
        -------
        Dict[str, Any]
            Canonical Enterprise Process Model.
        """
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Shared helper methods
    # ------------------------------------------------------------------

    def deep_copy(
        self,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a deep copy of provider data before transformation.
        """
        return deepcopy(data)

    def get_provider_name(self) -> str:
        """
        Returns the registered provider name.
        """
        return self.provider_name

    def normalize_string(self, value: Any) -> str:
        """
        Normalize any value into a trimmed string.
        """

        if value is None:
            return ""

        return str(value).strip()

    def normalize_list(self, value: Any) -> list:
        """
        Ensure the returned value is always a list.
        """

        if value is None:
            return []

        if isinstance(value, list):
            return value

        return [value]

    def normalize_dictionary(self, value: Any) -> Dict[str, Any]:
        """
        Ensure the returned value is always a dictionary.
        """

        if value is None:
            return {}

        if isinstance(value, dict):
            return value

        return {}

    def is_empty(self, value: Any) -> bool:
        """
        Returns True when the supplied value is considered empty.
        """

        if value is None:
            return True

        if isinstance(value, str):
            return value.strip() == ""

        if isinstance(value, (list, dict)):
            return len(value) == 0

        return False