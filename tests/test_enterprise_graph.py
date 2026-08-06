"""
===============================================================================
Tests - Enterprise Knowledge Graph
===============================================================================
"""

from src.knowledge_graph import GraphBuilder


def test_build_graph():

    canonical = {

        "process": {

            "id": "P1",

            "name": "Invoice Approval",
        },

        "activities": [

            {

                "id": "A1",

                "name": "Approve Invoice",
            },

            {

                "id": "A2",

                "name": "Send Payment",
            },
        ],
    }

    builder = GraphBuilder()

    graph = builder.build(canonical)

    assert graph.node_count() == 3

    assert graph.edge_count() == 0

    assert graph.get_node("P1") is not None

    assert graph.get_node("A1") is not None

    assert graph.get_node("A2") is not None