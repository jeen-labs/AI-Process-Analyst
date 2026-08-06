"""
===============================================================================
Canonical Enricher
===============================================================================

Adds business intelligence to ontology-classified activities.

Author:
Jeen Labs
===============================================================================
"""

from __future__ import annotations

from typing import Dict

from .enrichment_rules import EnrichmentRules


class CanonicalEnricher:

    def enrich(
        self,
        ontology_result: Dict[str, str],
    ) -> Dict[str, object]:

        activity = ontology_result["activity"]

        enriched = dict(ontology_result)

        enriched["criticality"] = (
            EnrichmentRules.determine_criticality(activity).value
        )

        enriched["riskLevel"] = (
            EnrichmentRules.determine_risk(activity).value
        )

        enriched["automationCandidate"] = (
            EnrichmentRules.automation_candidate(activity)
        )

        return enriched