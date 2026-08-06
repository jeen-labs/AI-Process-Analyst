"""
===============================================================================
Graph Builder
===============================================================================

Builds an Enterprise Knowledge Graph from the canonical model.

Version 1

Creates graph nodes only.

Future versions will create:

Activity -> Participant
Activity -> System
Decision -> Rule
Activity -> Data Object
etc.

Author:
Jeen Labs
===============================================================================
"""

from __future__ import annotations

from typing import Any, Dict

from .enterprise_graph import EnterpriseGraph
from .graph_node import GraphNode


class GraphBuilder:

    def build(
        self,
        canonical_model: Dict[str, Any],
    ) -> EnterpriseGraph:

        graph = EnterpriseGraph()

        process = canonical_model.get("process", {})

        process_id = process.get("id", "process")

        graph.add_node(

            GraphNode(

                id=process_id,

                node_type="process",

                properties=process,
            )
        )

        for activity in canonical_model.get(
            "activities",
            [],
        ):

            graph.add_node(

                GraphNode(

                    id=activity["id"],

                    node_type="activity",

                    properties=activity,
                )
            )

        return graph