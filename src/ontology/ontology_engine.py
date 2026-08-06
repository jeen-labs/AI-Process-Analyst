"""
===============================================================================
Enterprise Ontology Engine
===============================================================================

Classifies every activity in a canonical enterprise process model.

Author:
Jeen Labs
===============================================================================
"""

from __future__ import annotations

from typing import Any, Dict
from copy import deepcopy

from .business_taxonomy import BusinessTaxonomy
from .ontology_types import (
    BusinessCategory,
    BusinessDomain,
)


class OntologyEngine:
    """
    Adds ontology classifications to the canonical model.

    The model itself is returned after enrichment.
    """

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

    # ------------------------------------------------------------------

    def classify(
        self,
        canonical_model: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Adds ontology information to every activity in the canonical model.
        """

        model = deepcopy(canonical_model)

        activities = model.get("activities", [])

        for activity in activities:

            activity_name = activity.get("name", "")

            activity["ontology"] = self.classify_activity(activity_name)

        return model