"""
Tests for Enterprise Ontology Engine
"""

from src.ontology import OntologyEngine


def test_finance_approval():

    engine = OntologyEngine()

    model = {
        "activities": [
            {
                "name": "Approve Invoice"
            }
        ]
    }

    result = engine.classify(model)

    ontology = result["activities"][0]["ontology"]

    assert ontology["businessDomain"] == "finance"
    assert ontology["businessCategory"] == "approval"


def test_procurement_creation():

    engine = OntologyEngine()

    model = {
        "activities": [
            {
                "name": "Create Purchase Order"
            }
        ]
    }

    result = engine.classify(model)

    ontology = result["activities"][0]["ontology"]

    assert ontology["businessDomain"] == "procurement"


def test_unknown_activity():

    engine = OntologyEngine()

    model = {
        "activities": [
            {
                "name": "Do Something Random"
            }
        ]
    }

    result = engine.classify(model)

    ontology = result["activities"][0]["ontology"]

    assert ontology["businessDomain"] == "unknown"