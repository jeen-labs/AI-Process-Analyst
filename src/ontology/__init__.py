"""
===============================================================================
Enterprise Business Ontology
===============================================================================

Public interface for the ontology package.

Author:
Jeen Labs
===============================================================================
"""

from .ontology_engine import OntologyEngine
from .ontology_types import (
    BusinessCategory,
    BusinessDomain,
)
from .business_taxonomy import BusinessTaxonomy

__all__ = [
    "OntologyEngine",
    "BusinessCategory",
    "BusinessDomain",
    "BusinessTaxonomy",
]