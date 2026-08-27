"""
===============================================================================
Gemini Provider Normalizer
===============================================================================

Purpose
-------
Transforms Gemini-specific extraction output into the Enterprise Canonical
Process Model.

This adapter is intentionally isolated from the rest of the pipeline.

The downstream architecture must not depend on Gemini-specific response
structures. Gemini-specific interpretation belongs exclusively inside this
adapter.

Provider Architecture
---------------------

Gemini response
        |
        v
GeminiNormalizer
        |
        v
Enterprise Canonical Process Model
        |
        +---- Validator
        +---- Ontology
        +---- Enrichment
        +---- Rules
        +---- Analytics
        +---- Automation
        +---- Governance

The same BaseProviderNormalizer contract can later be implemented by:

- OpenAI
- Anthropic / Claude
- Azure OpenAI
- Ollama
- Manual Import
- Future providers

Author:
Jeen Labs
===============================================================================
"""

from __future__ import annotations

from typing import Any, Dict

from src.normalizers.base_normalizer import BaseProviderNormalizer


class GeminiNormalizer(BaseProviderNormalizer):
    """
    Provider adapter for Gemini.

    This class is responsible only for translating Gemini-native output into
    the Enterprise Canonical Process Model.

    No downstream business logic belongs here.
    """

    PROVIDER_NAME = "gemini"

    SCHEMA_VERSION = "1.0.0"
    MODEL_VERSION = "1.0.0"

    # =========================================================================
    # Construction
    # =========================================================================

    def __init__(self) -> None:
        """
        Initialise the Gemini provider adapter.
        """

        super().__init__(
            self.PROVIDER_NAME
        )

    # =========================================================================
    # Public API
    # =========================================================================

    def normalize(
        self,
        provider_response: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Convert a Gemini response into the Enterprise Canonical Process Model.

        Parameters
        ----------
        provider_response:
            Gemini provider response.

        Returns
        -------
        Dict[str, Any]
            Enterprise Canonical Process Model.

        Raises
        ------
        ValueError
            If provider_response is not a dictionary.

        Notes
        -----
        The provider response is copied before any transformation occurs.

        The adapter validates the final canonical result at the basic
        BaseProviderNormalizer contract level. Detailed schema validation
        remains the responsibility of SchemaValidator.
        """

        response = self.validate_provider_response(
            provider_response
        )

        canonical_model = {
            "schemaVersion": self.SCHEMA_VERSION,
            "modelVersion": self.MODEL_VERSION,

            "metadata": self._normalize_metadata(
                response
            ),

            "process": self._normalize_process(
                response
            ),

            "participants": self._normalize_participants(
                response
            ),

            "activities": self._normalize_activities(
                response
            ),

            "decisions": self._normalize_decisions(
                response
            ),

            "businessRules": self._normalize_business_rules(
                response
            ),

            "dataObjects": self._normalize_data_objects(
                response
            ),

            "systems": self._normalize_systems(
                response
            ),

            "relationships": self._normalize_relationships(
                response
            ),

            "governance": self._normalize_governance(
                response
            ),

            "analytics": self._normalize_analytics(
                response
            ),

            "automation": self._normalize_automation(
                response
            ),

            "extensions": {},
        }

        return self.validate_canonical_model(
            canonical_model
        )

    # =========================================================================
    # Section Normalizers
    # =========================================================================
    #
    # These methods deliberately remain isolated.
    #
    # When Gemini response extraction is expanded, each section can be
    # implemented independently without changing:
    #
    #     BaseProviderNormalizer
    #     CanonicalNormalizer
    #     EnterprisePipeline
    #
    # This isolation is important for future provider adapters.
    # =========================================================================

    def _normalize_metadata(
        self,
        response: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Normalize Gemini metadata.

        Currently returns an empty metadata section.

        Provider-specific metadata mapping can be introduced here without
        affecting the canonical pipeline.
        """

        return {}

    # -------------------------------------------------------------------------

    def _normalize_process(
        self,
        response: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Normalize the Gemini process section.
        """

        return {}

    # -------------------------------------------------------------------------

    def _normalize_participants(
        self,
        response: Dict[str, Any],
    ) -> list[Any]:
        """
        Normalize Gemini participants.
        """

        return []

    # -------------------------------------------------------------------------

    def _normalize_activities(
        self,
        response: Dict[str, Any],
    ) -> list[Any]:
        """
        Normalize Gemini activities.
        """

        return []

    # -------------------------------------------------------------------------

    def _normalize_decisions(
        self,
        response: Dict[str, Any],
    ) -> list[Any]:
        """
        Normalize Gemini decisions.
        """

        return []

    # -------------------------------------------------------------------------

    def _normalize_business_rules(
        self,
        response: Dict[str, Any],
    ) -> list[Any]:
        """
        Normalize Gemini business rules.
        """

        return []

    # -------------------------------------------------------------------------

    def _normalize_data_objects(
        self,
        response: Dict[str, Any],
    ) -> list[Any]:
        """
        Normalize Gemini data objects.
        """

        return []

    # -------------------------------------------------------------------------

    def _normalize_systems(
        self,
        response: Dict[str, Any],
    ) -> list[Any]:
        """
        Normalize Gemini systems.
        """

        return []

    # -------------------------------------------------------------------------

    def _normalize_relationships(
        self,
        response: Dict[str, Any],
    ) -> list[Any]:
        """
        Normalize Gemini relationships.
        """

        return []

    # -------------------------------------------------------------------------

    def _normalize_governance(
        self,
        response: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Normalize Gemini governance metadata.
        """

        return {}

    # -------------------------------------------------------------------------

    def _normalize_analytics(
        self,
        response: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Normalize Gemini analytics metadata.
        """

        return {}

    # -------------------------------------------------------------------------

    def _normalize_automation(
        self,
        response: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Normalize Gemini automation metadata.
        """

        return {}