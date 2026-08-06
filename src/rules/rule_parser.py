"""
===============================================================================
Rule Parser
===============================================================================

Version 1 parser.

Future versions will support:

- YAML
- JSON
- DSL
- Natural Language
- AI generated rules

Author:
Jeen Labs
===============================================================================
"""

from __future__ import annotations

from typing import Dict


class RuleParser:

    @staticmethod
    def parse(rule: Dict) -> Dict:

        if "name" not in rule:
            raise ValueError("Rule requires a name.")

        if "when" not in rule:
            raise ValueError("Rule requires a 'when' section.")

        if "then" not in rule:
            raise ValueError("Rule requires a 'then' section.")

        return rule