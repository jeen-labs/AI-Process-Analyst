"""
Integration Result

Represents the complete output of the enterprise processing pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(slots=True)
class IntegrationResult:
    """
    Final integration output.
    """

    canonical_model: Dict[str, Any]

    knowledge_graph: Any | None = None

    ontology: Dict[str, Any] = field(default_factory=dict)

    validation_passed: bool = True

    processing_time_ms: float = 0.0