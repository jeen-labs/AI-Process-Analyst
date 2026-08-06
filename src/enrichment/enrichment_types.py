"""
===============================================================================
Enrichment Types
===============================================================================

Common business intelligence enumerations.

Author:
Jeen Labs
===============================================================================
"""

from enum import Enum


class Criticality(str, Enum):

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskLevel(str, Enum):

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"