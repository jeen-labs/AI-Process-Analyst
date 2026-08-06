"""
===============================================================================
Enterprise Canonical Enricher
===============================================================================

Enriches the Enterprise Canonical Process Model.

This component augments every activity with additional metadata that can later
be consumed by:

• Rule Engine
• Analytics
• Automation Recommendation Engine
• Knowledge Graph
• AI Optimization Engine

Author:
Jeen Labs
===============================================================================
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict

from .enrichment_rules import EnrichmentRules


class CanonicalEnricher:
    """
    Adds enterprise enrichment to every activity.
    """

    def enrich(
        self,
        canonical_model: Dict[str, Any],
    ) -> Dict[str, Any]:

        model = deepcopy(canonical_model)

        activities = model.get("activities", [])

        for activity in activities:

            name = activity.get("name", "").lower()

            enrichment = {

                "riskLevel": "Medium",
                "automationCandidate": False,
                "ownerRole": "Unknown",
                "kpiCategory": "General",
            }

            RISK_PRIORITY = {
                "Low": 1,
                "Medium": 2,
                "High": 3,
            }

            for keyword, values in EnrichmentRules.RULES.items():

                if keyword not in name:
                    continue

                # ----------------------------
                # Highest risk always wins
                # ----------------------------

                if "riskLevel" in values:

                    current = enrichment["riskLevel"]
                    new = values["riskLevel"]

                    if RISK_PRIORITY[new] > RISK_PRIORITY[current]:
                        enrichment["riskLevel"] = new

                # ----------------------------
                # Automation
                # ----------------------------

                if values.get("automationCandidate", False):
                    enrichment["automationCandidate"] = True

                # ----------------------------
                # Owner
                # Prefer the more specific owner role.
                # ----------------------------

                if "ownerRole" in values:

                    current = enrichment["ownerRole"]
                    new = values["ownerRole"]

                    if current == "Unknown":
                        enrichment["ownerRole"] = new

                    elif len(new) > len(current):
                        enrichment["ownerRole"] = new

                # ----------------------------
                # KPI
                # ----------------------------

                if (
                    enrichment["kpiCategory"] == "General"
                    and "kpiCategory" in values
                ):
                    enrichment["kpiCategory"] = values["kpiCategory"]

            activity["enrichment"] = enrichment

        return model