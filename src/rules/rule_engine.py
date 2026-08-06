"""
===============================================================================
Enterprise Rule Engine
===============================================================================

Coordinates parsing, registration and execution.

Author:
Jeen Labs
===============================================================================
"""

from __future__ import annotations

from typing import Dict

from .business_rule_executor import BusinessRuleExecutor
from .rule_parser import RuleParser
from .rule_registry import RuleRegistry


class RuleEngine:

    def __init__(self) -> None:

        self.registry = RuleRegistry()

    def register_rule(self, rule: Dict) -> None:

        parsed = RuleParser.parse(rule)

        self.registry.register(parsed)

    def execute(self, data: Dict) -> Dict:

        result = dict(data)

        for rule in self.registry.rules:

            result = BusinessRuleExecutor.execute(
                rule,
                result,
            )

        return result