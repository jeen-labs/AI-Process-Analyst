"""
Enterprise Integration Engine

Coordinates all enterprise engines.

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
Ontology Engine
        │
        ▼
Enrichment Engine
        │
        ▼
Business Rule Engine
        │
        ▼
Knowledge Graph Builder
"""

from __future__ import annotations

import time
from typing import Any, Dict

from src.canonical_normalizer import CanonicalNormalizer
from src.enrichment import CanonicalEnricher
from src.knowledge_graph import GraphBuilder
from src.ontology import OntologyEngine
from src.rules import RuleEngine
from src.validator import SchemaValidator

from .integration_result import IntegrationResult


class IntegrationEngine:
    """
    Coordinates all enterprise components.
    """

    def __init__(
        self,
        normalizer: CanonicalNormalizer,
        validator: SchemaValidator,
        ontology: OntologyEngine,
        enricher: CanonicalEnricher,
        rules: RuleEngine,
        graph_builder: GraphBuilder,
    ) -> None:

        self.normalizer = normalizer
        self.validator = validator
        self.ontology = ontology
        self.enricher = enricher
        self.rules = rules
        self.graph_builder = graph_builder

    def process(
        self,
        provider: str,
        provider_response: Dict[str, Any],
    ) -> IntegrationResult:
        """
        Execute the complete enterprise pipeline.
        """

        start = time.perf_counter()

        canonical = self.normalizer.normalize(
            provider,
            provider_response,
        )

        self.validator.validate(canonical)

        # ---------------------------------------------------------
        # Classify every activity in the canonical model
        # ---------------------------------------------------------

        ontology_result = []

        activities = canonical.get("activities", [])

        for activity in activities:

            activity_name = activity.get("name", "")

            ontology_result.append(
                self.ontology.classify_activity(activity_name)
            )

        enriched = self.enricher.enrich(canonical)

        self.rules.execute(enriched)

        graph = self.graph_builder.build(enriched)

        elapsed = (time.perf_counter() - start) * 1000

        return IntegrationResult(
            canonical_model=enriched,
            knowledge_graph=graph,
            ontology=ontology_result,
            validation_passed=True,
            processing_time_ms=elapsed,
        )