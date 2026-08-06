"""
===============================================================================
Tests - Enterprise Ontology Engine
===============================================================================
"""

from src.ontology import OntologyEngine


def test_finance_approval():

    engine = OntologyEngine()

    result = engine.classify_activity(
        "Approve Invoice"
    )

    assert result["businessDomain"] == "finance"
    assert result["businessCategory"] == "approval"


def test_procurement_creation():

    engine = OntologyEngine()

    result = engine.classify_activity(
        "Create Purchase Order"
    )

    assert result["businessDomain"] == "procurement"
    assert result["businessCategory"] == "creation"


def test_unknown_activity():

    engine = OntologyEngine()

    result = engine.classify_activity(
        "Do Something"
    )

    assert result["businessDomain"] == "unknown"
    assert result["businessCategory"] == "unknown"