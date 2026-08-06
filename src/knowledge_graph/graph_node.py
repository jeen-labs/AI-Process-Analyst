"""
===============================================================================
Graph Node
===============================================================================

Represents one entity in the Enterprise Knowledge Graph.

Examples

Activity
Participant
Decision
Business Rule
System
Data Object

Author:
Jeen Labs
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class GraphNode:

    id: str

    node_type: str

    properties: Dict[str, Any] = field(default_factory=dict)