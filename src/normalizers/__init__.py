"""
===============================================================================
Provider Normalizers Package
===============================================================================

Purpose
-------
Public interface for provider-specific adapters that transform native
AI/provider responses into the Enterprise Canonical Process Model.

Architecture
------------

Provider-specific response
            |
            v
    BaseProviderNormalizer
            |
            +-------------------+
            |                   |
         Gemini              Future
            |              Providers
            |                   |
            +---------+---------+
                      |
                      v
          Enterprise Canonical Model

The package deliberately exposes the provider-neutral base contract together
with the currently implemented providers.

Current Providers
-----------------
- Gemini

Future Providers
----------------
The architecture is intentionally designed to support additional providers
without changing downstream pipeline components.

Examples include:

- OpenAI
- Anthropic / Claude
- Azure OpenAI
- Ollama
- Local/self-hosted models
- Manual import
- Future AI providers

Important
---------
Adding a provider should require implementing BaseProviderNormalizer and
registering the adapter with CanonicalNormalizer.

Downstream components must not contain provider-specific logic.

Author:
Jeen Labs
===============================================================================
"""

from .base_normalizer import BaseProviderNormalizer
from .gemini_normalizer import GeminiNormalizer


# =============================================================================
# Public Provider Names
# =============================================================================
#
# These constants provide a stable place for provider identifiers without
# forcing the rest of the application to depend on provider implementation
# classes.
#
# New providers can be added here when their adapters are actually
# implemented.
# =============================================================================

PROVIDER_GEMINI = "gemini"


# =============================================================================
# Public Exports
# =============================================================================

__all__ = [
    "BaseProviderNormalizer",
    "GeminiNormalizer",
    "PROVIDER_GEMINI",
]