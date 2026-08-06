"""
===============================================================================
Graph Edge
===============================================================================

Represents a relationship between two graph nodes.

Examples

performed_by
uses
reads
writes
controls
depends_on

Author:
Jeen Labs
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class GraphEdge:

    source: str

    target: str

    relationship: str