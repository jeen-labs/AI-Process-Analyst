"""
===============================================================================
Tests for Canonical Normalizer
===============================================================================

These tests verify that the canonical normalization framework correctly
registers provider adapters and converts provider responses into the
Enterprise Canonical Process Model.

Run:

    pytest

===============================================================================
"""

from src.canonical_normalizer import CanonicalNormalizer
from src.normalizers.gemini_normalizer import GeminiNormalizer


def test_register_provider():
    """
    Ensure providers can be registered.
    """

    normalizer = CanonicalNormalizer()

    normalizer.register_provider(
        "gemini",
        GeminiNormalizer()
    )

    assert "gemini" in normalizer.registered_providers


def test_registered_providers_sorted():
    """
    Providers should be returned alphabetically.
    """

    normalizer = CanonicalNormalizer()

    normalizer.register_provider(
        "gemini",
        GeminiNormalizer()
    )

    assert normalizer.registered_providers == [
        "gemini"
    ]


def test_gemini_normalization_returns_dictionary():
    """
    Gemini normalizer should return a dictionary.
    """

    normalizer = CanonicalNormalizer()

    normalizer.register_provider(
        "gemini",
        GeminiNormalizer()
    )

    provider_response = {
        "process": {
            "name": "Invoice Approval"
        }
    }

    canonical = normalizer.normalize(
        "gemini",
        provider_response
    )

    assert isinstance(canonical, dict)


def test_unknown_provider_raises_error():
    """
    Unknown providers should raise an exception.
    """

    normalizer = CanonicalNormalizer()

    try:
        normalizer.normalize(
            "unknown",
            {}
        )

        assert False

    except ValueError:
        assert True