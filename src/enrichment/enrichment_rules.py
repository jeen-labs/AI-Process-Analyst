"""
===============================================================================
Enrichment Rules
===============================================================================

Simple business rules for enriching activities.

Version 1:
Keyword-based rules.

Future versions will include:

- AI reasoning
- Knowledge Graph lookups
- Organization-specific rules
- Governance policies

Author:
Jeen Labs
===============================================================================
"""

from __future__ import annotations

from .enrichment_types import (
    Criticality,
    RiskLevel,
)


class EnrichmentRules:

    @staticmethod
    def determine_criticality(activity_name: str) -> Criticality:

        text = activity_name.lower()

        if "approve" in text:
            return Criticality.HIGH

        if "payment" in text:
            return Criticality.CRITICAL

        if "review" in text:
            return Criticality.MEDIUM

        return Criticality.LOW

    @staticmethod
    def determine_risk(activity_name: str) -> RiskLevel:

        text = activity_name.lower()

        if "payment" in text:
            return RiskLevel.HIGH

        if "approve" in text:
            return RiskLevel.MEDIUM

        return RiskLevel.LOW

    @staticmethod
    def automation_candidate(activity_name: str) -> bool:

        text = activity_name.lower()

        keywords = [
            "validate",
            "verify",
            "generate",
            "notify",
            "email",
            "report",
        ]

        return any(keyword in text for keyword in keywords)