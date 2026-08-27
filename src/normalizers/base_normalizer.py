"""
===============================================================================
Base Provider Normalizer
===============================================================================

Purpose
-------
Defines the stable provider-normalization contract used by every AI/provider
adapter in the Enterprise Process Analyst.

Every provider-specific adapter is responsible for converting its native
response into the Enterprise Canonical Process Model.

Supported / Planned Providers
------------------------------
- Gemini
- OpenAI
- Anthropic / Claude
- Azure OpenAI
- Ollama
- Manual Import
- Future providers

Architecture
------------

Provider-native response
        |
        v
BaseProviderNormalizer contract
        |
        +---- GeminiNormalizer
        +---- OpenAINormalizer
        +---- AnthropicNormalizer
        +---- AzureOpenAINormalizer
        +---- OllamaNormalizer
        +---- ManualImportNormalizer
        +---- FutureProviderNormalizer
        |
        v
Enterprise Canonical Process Model

The downstream pipeline must never need to know which provider produced the
original response.

Design Principles
-----------------
1. Provider adapters share one stable contract.
2. Provider-specific parsing remains inside the adapter.
3. Downstream components consume only the canonical model.
4. Provider names are normalized consistently.
5. Provider input is never mutated in place by shared helpers.
6. Shared normalization helpers remain provider-neutral.
7. Future providers can be added without changing downstream pipeline logic.

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
    Abstract contract for all provider-specific normalizers.

    A provider normalizer translates provider-native output into the
    Enterprise Canonical Process Model.

    The base class deliberately contains no provider-specific parsing logic.
    """

    # =========================================================================
    # Construction
    # =========================================================================

    def __init__(
        self,
        provider_name: str,
    ) -> None:
        """
        Initialise a provider normalizer.

        Parameters
        ----------
        provider_name:
            Stable internal provider identifier.

        Raises
        ------
        ValueError
            If provider_name is not a non-empty string.
        """

        normalized_provider_name = self.normalize_provider_name(
            provider_name
        )

        if not normalized_provider_name:
            raise ValueError(
                "provider_name must not be empty."
            )

        self.provider_name = normalized_provider_name

    # =========================================================================
    # Required Provider Contract
    # =========================================================================

    @abstractmethod
    def normalize(
        self,
        provider_response: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Convert a provider-native response into the canonical model.

        Every concrete provider adapter must implement this method.

        Parameters
        ----------
        provider_response:
            Raw provider response represented as a dictionary.

        Returns
        -------
        Dict[str, Any]
            Enterprise Canonical Process Model.

        Notes
        -----
        Provider-specific interpretation belongs inside the concrete
        implementation.

        This base class intentionally does not assume any provider-specific
        response structure.
        """

        raise NotImplementedError

    # =========================================================================
    # Provider Identity
    # =========================================================================

    @staticmethod
    def normalize_provider_name(
        provider_name: Any,
    ) -> str:
        """
        Normalize a provider identifier.

        Provider identifiers are treated case-insensitively and surrounding
        whitespace is removed.

        Examples
        --------
        ``" Gemini "`` -> ``"gemini"``
        ``"OpenAI"``   -> ``"openai"``
        ``" Claude "`` -> ``"claude"``
        """

        if provider_name is None:
            return ""

        if not isinstance(provider_name, str):
            return ""

        return provider_name.strip().lower()

    def get_provider_name(
        self,
    ) -> str:
        """
        Return the normalized provider identifier.
        """

        return self.provider_name

    # =========================================================================
    # Provider Input Validation
    # =========================================================================

    def validate_provider_response(
        self,
        provider_response: Any,
    ) -> Dict[str, Any]:
        """
        Validate and safely copy a provider response.

        This helper establishes a common input boundary for concrete
        normalizers.

        The original provider response is never modified.

        Parameters
        ----------
        provider_response:
            Provider-native response.

        Returns
        -------
        Dict[str, Any]
            Deep-copied provider response.

        Raises
        ------
        ValueError
            If the response is not a dictionary.
        """

        if not isinstance(provider_response, dict):
            raise ValueError(
                "provider_response must be a dictionary."
            )

        return deepcopy(provider_response)

    # =========================================================================
    # Shared Copy Helper
    # =========================================================================

    def deep_copy(
        self,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Create a deep copy of provider data before transformation.

        Provider adapters should use this helper whenever they need to
        transform provider-native data without mutating the caller's object.
        """

        if not isinstance(data, dict):
            raise ValueError(
                "data must be a dictionary."
            )

        return deepcopy(data)

    # =========================================================================
    # Canonical Result Validation
    # =========================================================================

    def validate_canonical_model(
        self,
        canonical_model: Any,
    ) -> Dict[str, Any]:
        """
        Validate the basic type contract of a canonical model.

        This method deliberately performs only structural validation.

        Provider adapters must not be forced to share provider-specific
        assumptions here.

        The detailed canonical schema remains the responsibility of the
        canonical validator.

        Parameters
        ----------
        canonical_model:
            Provider adapter output.

        Returns
        -------
        Dict[str, Any]
            The canonical model.

        Raises
        ------
        ValueError
            If the adapter did not return a dictionary.
        """

        if not isinstance(canonical_model, dict):
            raise ValueError(
                "Provider normalizer must return a dictionary."
            )

        return canonical_model

    # =========================================================================
    # String Normalization
    # =========================================================================

    def normalize_string(
        self,
        value: Any,
    ) -> str:
        """
        Normalize a value into a trimmed string.

        ``None`` becomes an empty string.
        """

        if value is None:
            return ""

        return str(value).strip()

    # =========================================================================
    # List Normalization
    # =========================================================================

    def normalize_list(
        self,
        value: Any,
    ) -> list[Any]:
        """
        Ensure a value is represented as a list.

        ``None`` becomes an empty list.

        A non-list value is wrapped in a single-item list.

        Existing lists are copied so callers cannot accidentally mutate the
        original list through the returned value.
        """

        if value is None:
            return []

        if isinstance(value, list):
            return deepcopy(value)

        return [deepcopy(value)]

    # =========================================================================
    # Dictionary Normalization
    # =========================================================================

    def normalize_dictionary(
        self,
        value: Any,
    ) -> Dict[str, Any]:
        """
        Ensure a value is represented as a dictionary.

        ``None`` and non-dictionary values become an empty dictionary.

        Dictionaries are deep-copied before being returned.
        """

        if value is None:
            return {}

        if isinstance(value, dict):
            return deepcopy(value)

        return {}

    # =========================================================================
    # Empty-Value Detection
    # =========================================================================

    def is_empty(
        self,
        value: Any,
    ) -> bool:
        """
        Determine whether a supplied value is considered empty.

        Empty values include:

        - ``None``
        - empty / whitespace-only strings
        - empty lists
        - empty dictionaries

        Other scalar values are considered non-empty.
        """

        if value is None:
            return True

        if isinstance(value, str):
            return value.strip() == ""

        if isinstance(value, (list, dict)):
            return len(value) == 0

        return False