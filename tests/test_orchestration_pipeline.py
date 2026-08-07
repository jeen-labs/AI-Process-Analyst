"""
===============================================================================
AI Process Analyst
===============================================================================

Module:
    tests/test_orchestration_pipeline.py

Purpose:
    Automated tests for the Enterprise OrchestrationPipeline.

Phase:
    Milestone 3 - Enterprise AI Orchestration Layer
    Phase 3.5 - Orchestration Pipeline
===============================================================================
"""

# =============================================================================
# Imports
# =============================================================================

import pytest

from src.orchestration.llm_client import LLMClient
from src.orchestration.orchestration_pipeline import (
    OrchestrationPipeline,
    OrchestrationPipelineError,
)
from src.orchestration.prompt_builder import PromptBuilder
from src.orchestration.response_parser import ResponseParser


# =============================================================================
# Test Doubles
# =============================================================================


class FakePromptBuilder:
    """Test double for PromptBuilder."""

    def __init__(self) -> None:
        self.received_document = None

    def build_prompt(self, document_text: str) -> str:
        """Return a deterministic test prompt."""

        self.received_document = document_text

        return f"PROMPT::{document_text}"


class FakeLLMClient:
    """Test double for LLMClient."""

    def __init__(self, response: str = '{"status": "approved"}') -> None:
        self.response = response
        self.received_prompt = None

    def generate(self, prompt: str) -> str:
        """Return a deterministic LLM response."""

        self.received_prompt = prompt

        return self.response


class FakeResponseParser:
    """Test double for ResponseParser."""

    def __init__(self) -> None:
        self.received_response = None

    def parse(self, response: str):
        """Return a deterministic parsed result."""

        self.received_response = response

        return {
            "parsed": True,
            "response": response,
        }


# =============================================================================
# Initialisation Tests
# =============================================================================


def test_orchestration_pipeline_initialises():
    """Pipeline should initialise with all required components."""

    prompt_builder = FakePromptBuilder()
    llm_client = FakeLLMClient()
    response_parser = FakeResponseParser()

    pipeline = OrchestrationPipeline(
        prompt_builder,
        llm_client,
        response_parser,
    )

    assert pipeline.get_prompt_builder() is prompt_builder
    assert pipeline.get_llm_client() is llm_client
    assert pipeline.get_response_parser() is response_parser


def test_orchestration_pipeline_rejects_none_prompt_builder():
    """Pipeline should reject a missing PromptBuilder."""

    with pytest.raises(ValueError):
        OrchestrationPipeline(
            None,
            FakeLLMClient(),
            FakeResponseParser(),
        )


def test_orchestration_pipeline_rejects_none_llm_client():
    """Pipeline should reject a missing LLMClient."""

    with pytest.raises(ValueError):
        OrchestrationPipeline(
            FakePromptBuilder(),
            None,
            FakeResponseParser(),
        )


def test_orchestration_pipeline_rejects_none_response_parser():
    """Pipeline should reject a missing ResponseParser."""

    with pytest.raises(ValueError):
        OrchestrationPipeline(
            FakePromptBuilder(),
            FakeLLMClient(),
            None,
        )


# =============================================================================
# Input Validation Tests
# =============================================================================


def test_process_rejects_non_string_document():
    """Pipeline should reject non-string document input."""

    pipeline = OrchestrationPipeline(
        FakePromptBuilder(),
        FakeLLMClient(),
        FakeResponseParser(),
    )

    with pytest.raises(TypeError):
        pipeline.process(None)


def test_process_rejects_empty_document():
    """Pipeline should reject an empty document."""

    pipeline = OrchestrationPipeline(
        FakePromptBuilder(),
        FakeLLMClient(),
        FakeResponseParser(),
    )

    with pytest.raises(ValueError):
        pipeline.process("")


def test_process_rejects_whitespace_document():
    """Pipeline should reject a whitespace-only document."""

    pipeline = OrchestrationPipeline(
        FakePromptBuilder(),
        FakeLLMClient(),
        FakeResponseParser(),
    )

    with pytest.raises(ValueError):
        pipeline.process("   ")


# =============================================================================
# Pipeline Execution Tests
# =============================================================================


def test_process_builds_prompt_from_document():
    """Pipeline should pass the document to PromptBuilder."""

    prompt_builder = FakePromptBuilder()

    pipeline = OrchestrationPipeline(
        prompt_builder,
        FakeLLMClient(),
        FakeResponseParser(),
    )

    pipeline.process("Customer onboarding process")

    assert (
        prompt_builder.received_document
        == "Customer onboarding process"
    )


def test_process_sends_generated_prompt_to_llm():
    """Pipeline should send the generated prompt to the LLM client."""

    prompt_builder = FakePromptBuilder()
    llm_client = FakeLLMClient()

    pipeline = OrchestrationPipeline(
        prompt_builder,
        llm_client,
        FakeResponseParser(),
    )

    pipeline.process("Customer onboarding process")

    assert (
        llm_client.received_prompt
        == "PROMPT::Customer onboarding process"
    )


def test_process_sends_raw_response_to_parser():
    """Pipeline should send the LLM response to ResponseParser."""

    llm_client = FakeLLMClient(
        '{"process": "Customer Onboarding"}'
    )
    response_parser = FakeResponseParser()

    pipeline = OrchestrationPipeline(
        FakePromptBuilder(),
        llm_client,
        response_parser,
    )

    pipeline.process("Customer onboarding process")

    assert (
        response_parser.received_response
        == '{"process": "Customer Onboarding"}'
    )


def test_process_returns_parsed_response():
    """Pipeline should return the parsed response."""

    pipeline = OrchestrationPipeline(
        FakePromptBuilder(),
        FakeLLMClient(),
        FakeResponseParser(),
    )

    result = pipeline.process(
        "Customer onboarding process"
    )

    assert result == {
        "parsed": True,
        "response": '{"status": "approved"}',
    }


def test_process_executes_components_in_order():
    """Pipeline should execute builder, client, and parser in sequence."""

    execution_order = []

    class OrderedPromptBuilder:
        def build_prompt(self, document_text):
            execution_order.append("prompt_builder")
            return "generated prompt"

    class OrderedLLMClient:
        def generate(self, prompt):
            execution_order.append("llm_client")
            return '{"result": "ok"}'

    class OrderedResponseParser:
        def parse(self, response):
            execution_order.append("response_parser")
            return {"result": "ok"}

    pipeline = OrchestrationPipeline(
        OrderedPromptBuilder(),
        OrderedLLMClient(),
        OrderedResponseParser(),
    )

    result = pipeline.process("document")

    assert result == {"result": "ok"}

    assert execution_order == [
        "prompt_builder",
        "llm_client",
        "response_parser",
    ]


# =============================================================================
# Error Propagation Tests
# =============================================================================


def test_process_propagates_prompt_builder_value_error():
    """Prompt construction validation errors should remain visible."""

    class FailingPromptBuilder:
        def build_prompt(self, document_text):
            raise ValueError("prompt construction failed")

    pipeline = OrchestrationPipeline(
        FailingPromptBuilder(),
        FakeLLMClient(),
        FakeResponseParser(),
    )

    with pytest.raises(ValueError, match="prompt construction failed"):
        pipeline.process("document")


def test_process_propagates_llm_value_error():
    """LLM client validation errors should remain visible."""

    class FailingLLMClient:
        def generate(self, prompt):
            raise ValueError("LLM execution failed")

    pipeline = OrchestrationPipeline(
        FakePromptBuilder(),
        FailingLLMClient(),
        FakeResponseParser(),
    )

    with pytest.raises(ValueError, match="LLM execution failed"):
        pipeline.process("document")


def test_process_propagates_response_parser_value_error():
    """Response parsing validation errors should remain visible."""

    class FailingResponseParser:
        def parse(self, response):
            raise ValueError("response parsing failed")

    pipeline = OrchestrationPipeline(
        FakePromptBuilder(),
        FakeLLMClient(),
        FailingResponseParser(),
    )

    with pytest.raises(ValueError, match="response parsing failed"):
        pipeline.process("document")


def test_process_wraps_unexpected_exception():
    """Unexpected component failures should become pipeline errors."""

    class FailingLLMClient:
        def generate(self, prompt):
            raise RuntimeError("unexpected provider failure")

    pipeline = OrchestrationPipeline(
        FakePromptBuilder(),
        FailingLLMClient(),
        FakeResponseParser(),
    )

    with pytest.raises(
        OrchestrationPipelineError,
        match="Orchestration pipeline execution failed",
    ):
        pipeline.process("document")