"""
===============================================================================
AI Process Analyst
===============================================================================

Package:
    providers

Purpose:
    Public interface for the Enterprise LLM Provider Layer.

The provider package defines a provider-independent abstraction so that the
platform can work with multiple current and future AI service providers without
changing the orchestration layer.

Supported providers
-------------------
- Mock
- OpenAI
- Gemini

Planned / extensible providers
------------------------------
- Anthropic / Claude
- Ollama
- Azure OpenAI
- Local / self-hosted models
- Future providers

Architecture
------------

                    Application
                         │
                         ▼
                    LLM Factory
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
       OpenAI          Gemini          Mock
          │              │              │
          └──────────────┼──────────────┘
                         ▼
                  BaseProvider
                         │
                         ▼
                 Common Provider
                    Contract

Provider-specific implementation must remain isolated inside this package.

Author:
    Jeen Labs
===============================================================================
"""

from .base_provider import BaseProvider
from .gemini_provider import GeminiProvider
from .mock_provider import MockProvider
from .openai_provider import OpenAIProvider


# =============================================================================
# Stable Provider Identifiers
# =============================================================================

PROVIDER_MOCK = "mock"
PROVIDER_OPENAI = "openai"
PROVIDER_GEMINI = "gemini"


# =============================================================================
# Public Package Interface
# =============================================================================

__all__ = [
    # Base contract
    "BaseProvider",

    # Current providers
    "MockProvider",
    "OpenAIProvider",
    "GeminiProvider",

    # Stable provider identifiers
    "PROVIDER_MOCK",
    "PROVIDER_OPENAI",
    "PROVIDER_GEMINI",
]