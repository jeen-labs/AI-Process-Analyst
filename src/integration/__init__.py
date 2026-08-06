"""
Enterprise Integration Layer

Coordinates all enterprise engines into a single processing flow.

Pipeline

LLM Output
    ↓
Canonical Normalizer
    ↓
Schema Validator
    ↓
Ontology Engine
    ↓
Enrichment Engine
    ↓
Rule Engine
    ↓
Knowledge Graph
"""

from .integration_engine import IntegrationEngine
from .integration_result import IntegrationResult

__all__ = [
    "IntegrationEngine",
    "IntegrationResult",
]