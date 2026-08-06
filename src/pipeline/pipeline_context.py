"""
===============================================================================
Pipeline Context
===============================================================================

Carries runtime information across the pipeline.

Future additions:

- Correlation ID
- Execution ID
- Tenant
- User
- AI Provider
- Timing
- Logging
- Metrics

Author:
Jeen Labs
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class PipelineContext:

    provider: str

    source_name: Optional[str] = None

    source_type: Optional[str] = None