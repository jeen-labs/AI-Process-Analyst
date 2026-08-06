"""
===============================================================================
Enterprise Graph
===============================================================================

Stores enterprise graph nodes and edges.

Author:
Jeen Labs
===============================================================================
"""

from __future__ import annotations

from typing import Dict, List

from .graph_edge import GraphEdge
from .graph_node import GraphNode


class EnterpriseGraph:

    def __init__(self) -> None:

        self.nodes: Dict[str, GraphNode] = {}

        self.edges: List[GraphEdge] = []

    def add_node(self, node: GraphNode) -> None:

        self.nodes[node.id] = node

    def add_edge(self, edge: GraphEdge) -> None:

        self.edges.append(edge)

    def get_node(self, node_id: str):

        return self.nodes.get(node_id)

    def node_count(self) -> int:

        return len(self.nodes)

    def edge_count(self) -> int:

        return len(self.edges)