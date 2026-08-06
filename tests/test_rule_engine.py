"""
===============================================================================
Tests - Enterprise Rule Engine
===============================================================================
"""

from src.rules import RuleEngine


def test_rule_execution():

    engine = RuleEngine()

    engine.register_rule({

        "name": "Finance Approval",

        "when": {

            "businessDomain": "finance",
            "businessCategory": "approval",
        },

        "then": {

            "criticality": "high",
        },
    })

    result = engine.execute({

        "businessDomain": "finance",
        "businessCategory": "approval",
    })

    assert result["criticality"] == "high"


def test_rule_not_triggered():

    engine = RuleEngine()

    engine.register_rule({

        "name": "Finance Approval",

        "when": {

            "businessDomain": "finance",
        },

        "then": {

            "criticality": "high",
        },
    })

    result = engine.execute({

        "businessDomain": "hr",
    })

    assert "criticality" not in result


def test_multiple_rules():

    engine = RuleEngine()

    engine.register_rule({

        "name": "Rule1",

        "when": {

            "businessDomain": "finance",
        },

        "then": {

            "risk": "medium",
        },
    })

    engine.register_rule({

        "name": "Rule2",

        "when": {

            "risk": "medium",
        },

        "then": {

            "requiresApproval": True,
        },
    })

    result = engine.execute({

        "businessDomain": "finance",
    })

    assert result["risk"] == "medium"

    assert result["requiresApproval"] is True