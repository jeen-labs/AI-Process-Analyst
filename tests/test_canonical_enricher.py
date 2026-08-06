"""
===============================================================================
Tests for Enterprise Canonical Enricher
===============================================================================
"""

from src.enrichment import CanonicalEnricher


def test_invoice_approval():

    model = {
        "activities": [
            {
                "id": "A1",
                "name": "Approve Invoice",
            }
        ]
    }

    enriched = CanonicalEnricher().enrich(model)

    activity = enriched["activities"][0]

    assert activity["enrichment"]["riskLevel"] == "High"
    assert activity["enrichment"]["automationCandidate"] is True
    assert activity["enrichment"]["ownerRole"] == "Finance Manager"


def test_report_generation():

    model = {
        "activities": [
            {
                "id": "A1",
                "name": "Generate Monthly Report",
            }
        ]
    }

    enriched = CanonicalEnricher().enrich(model)

    activity = enriched["activities"][0]

    assert activity["enrichment"]["automationCandidate"] is True
    assert activity["enrichment"]["kpiCategory"] == "Reporting"


def test_payment():

    model = {
        "activities": [
            {
                "id": "A1",
                "name": "Process Vendor Payment",
            }
        ]
    }

    enriched = CanonicalEnricher().enrich(model)

    activity = enriched["activities"][0]

    assert activity["enrichment"]["riskLevel"] == "High"
    assert activity["enrichment"]["ownerRole"] == "Finance"