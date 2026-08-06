"""
===============================================================================
Business Rule Executor
===============================================================================

Executes business rules against an input model.

Author:
Jeen Labs
===============================================================================
"""

from __future__ import annotations

from typing import Dict


class BusinessRuleExecutor:

    @staticmethod
    def execute(rule: Dict, data: Dict) -> Dict:

        conditions = rule["when"]

        for key, value in conditions.items():

            if data.get(key) != value:
                return data

        updated = dict(data)

        updated.update(rule["then"])

        return updated