"""
===============================================================================
Enterprise Enrichment Rules
===============================================================================

Central enrichment catalogue used by the Canonical Enricher.

Author:
Jeen Labs
===============================================================================
"""

from __future__ import annotations


class EnrichmentRules:
    """
    Keyword-based enrichment catalogue.

    Each keyword contributes enrichment metadata to the activity.
    """

    RULES = {

        "approve": {
            "riskLevel": "High",
            "automationCandidate": False,
            "ownerRole": "Finance Manager",
            "kpiCategory": "Approval",
        },

        "invoice": {
            "riskLevel": "Medium",
            "automationCandidate": True,
            "ownerRole": "Finance",
            "kpiCategory": "Finance",
        },

        "payment": {
            "riskLevel": "High",
            "automationCandidate": True,
            "ownerRole": "Finance",
            "kpiCategory": "Finance",
        },

        "report": {
            "riskLevel": "Low",
            "automationCandidate": True,
            "ownerRole": "Reporting",
            "kpiCategory": "Reporting",
        },

        "purchase": {
            "riskLevel": "Medium",
            "automationCandidate": True,
            "ownerRole": "Procurement",
            "kpiCategory": "Procurement",
        },

        "vendor": {
            "riskLevel": "Medium",
            "automationCandidate": False,
            "ownerRole": "Finance",
            "kpiCategory": "Vendor",
        },

        "contract": {
            "riskLevel": "High",
            "automationCandidate": False,
            "ownerRole": "Legal",
            "kpiCategory": "Compliance",
        },
    }