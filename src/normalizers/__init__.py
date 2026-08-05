"""
===============================================================================
Normalizers Package
===============================================================================

Provider-specific adapters responsible for converting AI model output into the
Enterprise Canonical Process Model.

Each provider implements BaseProviderNormalizer.

Current Providers
-----------------
- Gemini

Planned Providers
-----------------
- OpenAI
- Anthropic
- Azure OpenAI
- Ollama
- Manual Import

===============================================================================
"""

from .base_normalizer import BaseProviderNormalizer
from .gemini_normalizer import GeminiNormalizer

__all__ = [
    "BaseProviderNormalizer",
    "GeminiNormalizer",
]