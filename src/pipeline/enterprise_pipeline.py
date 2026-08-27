"""
===============================================================================
Enterprise Pipeline
===============================================================================

Coordinates the complete enterprise processing flow.

Pipeline

Provider Response
        │
        ▼
Canonical Normalizer
        │
        ▼
Schema Validator
        │
        ▼
Ontology
        │
        ▼
Enrichment
        │
        ▼
Rules
        │
        ▼
Pipeline Result

Author:
Jeen Labs
===============================================================================
"""

from __future__ import annotations

from typing import Any, Dict

from src.canonical_normalizer import CanonicalNormalizer
from src.enrichment import CanonicalEnricher
from src.ontology import OntologyEngine
from src.pipeline.pipeline_context import PipelineContext
from src.pipeline.pipeline_result import PipelineResult
from src.rules import RuleEngine
from src.validator import SchemaValidator


class EnterprisePipeline:
    """
    Coordinates the complete enterprise processing pipeline.

    The pipeline deliberately delegates each processing responsibility
    to its dedicated component:

        1. Canonical normalization
        2. Schema validation
        3. Ontology classification
        4. Canonical enrichment
        5. Rule execution

    The pipeline itself is an orchestration component. It does not
    duplicate the implementation of any of these stages.
    """

    def __init__(self) -> None:
        """
        Initialise all enterprise pipeline components.
        """

        self.normalizer = CanonicalNormalizer()

        self.validator = SchemaValidator()

        self.ontology = OntologyEngine()

        self.enricher = CanonicalEnricher()

        self.rules = RuleEngine()

    # =========================================================================
    # Provider Registration
    # =========================================================================

    def register_provider(
        self,
        provider_name: str,
        adapter: Any,
    ) -> None:
        """
        Register a provider normalizer/adapter.

        Parameters
        ----------
        provider_name:
            Name of the provider.

        adapter:
            Provider-specific normalizer/adapter.
        """

        self.normalizer.register_provider(
            provider_name,
            adapter,
        )

    # =========================================================================
    # Pipeline Processing
    # =========================================================================

    def process(
        self,
        context: PipelineContext,
        provider_response: Dict[str, Any],
    ) -> PipelineResult:
        """
        Execute the complete enterprise processing pipeline.

        Processing order:

            Provider Response
                ↓
            Canonical Normalizer
                ↓
            Schema Validator
                ↓
            Ontology
                ↓
            Enrichment
                ↓
            Rules
                ↓
            Pipeline Result

        Parameters
        ----------
        context:
            Pipeline execution context.

        provider_response:
            Raw response received from the registered provider.

        Returns
        -------
        PipelineResult
            Result containing the fully processed canonical model.
        """

        # ---------------------------------------------------------------------
        # Phase 1 - Canonical Normalization
        # ---------------------------------------------------------------------

        canonical = self.normalizer.normalize(
            context.provider,
            provider_response,
        )

        # ---------------------------------------------------------------------
        # Phase 2 - Schema Validation
        # ---------------------------------------------------------------------

        self.validator.validate(
            canonical,
        )

        # ---------------------------------------------------------------------
        # Phase 3 - Ontology Classification
        # ---------------------------------------------------------------------
        #
        # OntologyEngine.classify() returns a new model containing ontology
        # information for every activity.
        # ---------------------------------------------------------------------

        canonical = self.ontology.classify(
            canonical,
        )

        # ---------------------------------------------------------------------
        # Phase 4 - Canonical Enrichment
        # ---------------------------------------------------------------------
        #
        # CanonicalEnricher.enrich() adds enrichment metadata to every
        # activity.
        # ---------------------------------------------------------------------

        canonical = self.enricher.enrich(
            canonical,
        )

        # ---------------------------------------------------------------------
        # Phase 5 - Rule Execution
        # ---------------------------------------------------------------------
        #
        # RuleEngine.execute() applies all registered business rules to the
        # processed canonical model.
        # ---------------------------------------------------------------------

        canonical = self.rules.execute(
            canonical,
        )

        # ---------------------------------------------------------------------
        # Phase 6 - Final Pipeline Result
        # ---------------------------------------------------------------------

        return PipelineResult(
            canonical_model=canonical,
        )