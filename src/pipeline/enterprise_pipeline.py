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

    def __init__(self) -> None:

        self.normalizer = CanonicalNormalizer()

        self.validator = SchemaValidator()

        self.ontology = OntologyEngine()

        self.enricher = CanonicalEnricher()

        self.rules = RuleEngine()

    def register_provider(
        self,
        provider_name: str,
        adapter,
    ) -> None:

        self.normalizer.register_provider(
            provider_name,
            adapter,
        )

    def process(
        self,
        context: PipelineContext,
        provider_response: Dict[str, Any],
    ) -> PipelineResult:

        canonical = self.normalizer.normalize(
            context.provider,
            provider_response,
        )

        self.validator.validate(canonical)

        return PipelineResult(
            canonical_model=canonical
        )