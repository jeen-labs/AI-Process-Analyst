"""
===============================================================================
Rule Registry
===============================================================================

Stores all registered business rules.

Author:
Jeen Labs
===============================================================================
"""

from __future__ import annotations

from typing import Dict, List


class RuleRegistry:

    def __init__(self) -> None:

        self._rules: List[Dict] = []

    def register(self, rule: Dict) -> None:

        self._rules.append(rule)

    @property
    def rules(self) -> List[Dict]:

        return list(self._rules)

    def clear(self) -> None:

        self._rules.clear()