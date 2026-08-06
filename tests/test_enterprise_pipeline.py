"""
===============================================================================
Tests - Enterprise Pipeline
===============================================================================
"""

from src.normalizers import GeminiNormalizer
from src.pipeline import (
    EnterprisePipeline,
    PipelineContext,
)


def test_pipeline_process():

    pipeline = EnterprisePipeline()

    pipeline.register_provider(
        "gemini",
        GeminiNormalizer(),
    )

    provider_response = {

        "process": {

            "name": "Invoice Approval",

            "activities": [

                {

                    "name": "Approve Invoice"

                }

            ]
        }

    }

    context = PipelineContext(

        provider="gemini",

        source_name="invoice.pdf",

        source_type="pdf",
    )

    result = pipeline.process(
        context,
        provider_response,
    )

    assert result.success is True

    assert "process" in result.canonical_model