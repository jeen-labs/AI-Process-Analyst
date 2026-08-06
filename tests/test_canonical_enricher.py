"""
===============================================================================
Tests - Canonical Enricher
===============================================================================
"""

from src.enrichment import CanonicalEnricher


def test_invoice_approval():

    enricher = CanonicalEnricher()

    result = enricher.enrich({

        "activity": "Approve Invoice",
        "businessDomain": "finance",
        "businessCategory": "approval",
    })

    assert result["criticality"] == "high"
    assert result["riskLevel"] == "medium"
    assert result["automationCandidate"] is False


def test_report_generation():

    enricher = CanonicalEnricher()

    result = enricher.enrich({

        "activity": "Generate Monthly Report",
        "businessDomain": "finance",
        "businessCategory": "reporting",
    })

    assert result["automationCandidate"] is True


def test_payment():

    enricher = CanonicalEnricher()

    result = enricher.enrich({

        "activity": "Process Payment",
        "businessDomain": "finance",
        "businessCategory": "payment",
    })

    assert result["criticality"] == "critical"
    assert result["riskLevel"] == "high"