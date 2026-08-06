"""
===============================================================================
Enterprise Ontology Engine
===============================================================================

Adds business meaning to canonical process activities.

Author:
Jeen Labs
===============================================================================
"""

from __future__ import annotations

from typing import Dict

from .business_taxonomy import BusinessTaxonomy
from .ontology_types import (
    BusinessCategory,
    BusinessDomain,
)


class OntologyEngine:

    def classify_activity(
        self,
        activity_name: str,
    ) -> Dict[str, str]:

        text = activity_name.lower()

        domain = BusinessDomain.UNKNOWN
        category = BusinessCategory.UNKNOWN

        for keyword, value in BusinessTaxonomy.DOMAIN_KEYWORDS.items():

            if keyword in text:
                domain = value
                break

        for keyword, value in BusinessTaxonomy.CATEGORY_KEYWORDS.items():

            if keyword in text:
                category = value
                break

        return {

            "activity": activity_name,
            "businessDomain": domain.value,
            "businessCategory": category.value,
        }