"""
===============================================================================
Pipeline Result
===============================================================================

Final output returned by the Enterprise Pipeline.

Author:
Jeen Labs
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class PipelineResult:

    canonical_model: Dict[str, Any]

    warnings: List[str] = field(default_factory=list)

    success: bool = True