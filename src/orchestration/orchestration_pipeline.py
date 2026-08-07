"""
===============================================================================
AI Process Analyst
===============================================================================

Module:
    orchestration.orchestration_pipeline

Purpose:
    Coordinate the enterprise AI orchestration flow from document input to
    structured LLM output.

Responsibilities:
    - Build a prompt from document content
    - Execute the prompt through the orchestration LLM client
    - Parse the raw LLM response
    - Return structured Python data
    - Keep orchestration flow separate from individual components

Architecture:
    Enterprise AI Orchestration Layer

Pipeline:
    Document
        |
        v
    PromptBuilder
        |
        v
    LLMClient
        |
        v
    ResponseParser
        |
        v
    Structured Result

This component does NOT:
    - Implement an LLM provider
    - Manage API credentials
    - Implement prompt templates
    - Implement JSON parsing rules
    - Perform enterprise schema validation
    - Normalize enterprise process models
    - Execute business rules
    - Build the enterprise knowledge graph

Phase:
    Milestone 3 - Enterprise AI Orchestration Layer
    Phase 3.5 - Orchestration Pipeline
===============================================================================
"""

# =============================================================================
# Imports
# =============================================================================

from typing import Any

from src.orchestration.llm_client import LLMClient
from src.orchestration.prompt_builder import PromptBuilder
from src.orchestration.response_parser import ResponseParser


# =============================================================================
# Exceptions
# =============================================================================


class OrchestrationPipelineError(Exception):
    """
    Base exception raised for orchestration pipeline failures.
    """

    pass


# =============================================================================
# Orchestration Pipeline
# =============================================================================


class OrchestrationPipeline:
    """
    Coordinate prompt construction, LLM execution, and response parsing.

    The pipeline intentionally delegates each responsibility to a dedicated
    orchestration component.

    PromptBuilder
        Responsible for constructing the LLM prompt.

    LLMClient
        Responsible for invoking the configured LLM client.

    ResponseParser
        Responsible for converting the raw LLM response into structured
        Python data.
    """

    def __init__(
        self,
        prompt_builder: PromptBuilder,
        llm_client: LLMClient,
        response_parser: ResponseParser,
    ) -> None:
        """
        Initialise the orchestration pipeline.

        Parameters
        ----------
        prompt_builder : PromptBuilder
            Component responsible for constructing the LLM prompt.

        llm_client : LLMClient
            Provider-independent orchestration LLM client.

        response_parser : ResponseParser
            Component responsible for parsing the raw LLM response.

        Raises
        ------
        ValueError
            If any required component is None.
        """

        if prompt_builder is None:
            raise ValueError(
                "prompt_builder must not be None"
            )

        if llm_client is None:
            raise ValueError(
                "llm_client must not be None"
            )

        if response_parser is None:
            raise ValueError(
                "response_parser must not be None"
            )

        self._prompt_builder = prompt_builder
        self._llm_client = llm_client
        self._response_parser = response_parser

    # =========================================================================
    # Main Pipeline
    # =========================================================================

    def process(self, document_text: str) -> Any:
        """
        Process a document through the complete orchestration pipeline.

        Parameters
        ----------
        document_text : str
            Business process document to be analysed.

        Returns
        -------
        Any
            Structured Python representation of the LLM response.

        Raises
        ------
        TypeError
            If document_text is not a string.

        ValueError
            If document_text is empty or contains only whitespace.

        OrchestrationPipelineError
            If a pipeline component fails during execution.
        """

        if not isinstance(document_text, str):
            raise TypeError(
                "document_text must be a string"
            )

        if not document_text.strip():
            raise ValueError(
                "document_text cannot be empty"
            )

        try:
            # Step 1: Construct the LLM prompt.
            prompt = self._prompt_builder.build_prompt(
                document_text
            )

            # Step 2: Execute the prompt through the orchestration client.
            raw_response = self._llm_client.generate(
                prompt
            )

            # Step 3: Parse the raw LLM response.
            parsed_response = self._response_parser.parse(
                raw_response
            )

            return parsed_response

        except (TypeError, ValueError):
            raise

        except Exception as exc:
            raise OrchestrationPipelineError(
                "Orchestration pipeline execution failed."
            ) from exc

    # =========================================================================
    # Component Accessors
    # =========================================================================

    def get_prompt_builder(self) -> PromptBuilder:
        """
        Return the configured PromptBuilder.

        Returns
        -------
        PromptBuilder
            Prompt construction component.
        """

        return self._prompt_builder

    def get_llm_client(self) -> LLMClient:
        """
        Return the configured LLMClient.

        Returns
        -------
        LLMClient
            Orchestration LLM client.
        """

        return self._llm_client

    def get_response_parser(self) -> ResponseParser:
        """
        Return the configured ResponseParser.

        Returns
        -------
        ResponseParser
            Response parsing component.
        """

        return self._response_parser