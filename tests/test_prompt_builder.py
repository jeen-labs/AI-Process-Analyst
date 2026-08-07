"""
===============================================================================
AI Process Analyst
===============================================================================

Module:
    tests/test_prompt_builder.py

Purpose:
    Automated tests for the Enterprise PromptBuilder.

Phase:
    Milestone 3 - Enterprise AI Orchestration Layer
    Phase 3.1 - Refactor Prompt Builder
===============================================================================
"""

from pathlib import Path

import pytest

from src.orchestration.prompt_builder import (
    DOCUMENT_PLACEHOLDER,
    PromptBuilder,
    PromptTemplateError,
)


# =============================================================================
# Template Loading
# =============================================================================

def test_load_template(tmp_path: Path):
    """
    A valid template should be loaded successfully.
    """

    template_path = tmp_path / "prompt.md"

    template_path.write_text(
        "Analyse this document:\n\n{{DOCUMENT_TEXT}}",
        encoding="utf-8",
    )

    builder = PromptBuilder(template_path)

    template = builder.load_template()

    assert template == (
        "Analyse this document:\n\n{{DOCUMENT_TEXT}}"
    )


def test_missing_template_raises_error(tmp_path: Path):
    """
    A missing template should raise FileNotFoundError.
    """

    template_path = tmp_path / "missing_prompt.md"

    builder = PromptBuilder(template_path)

    with pytest.raises(FileNotFoundError):
        builder.load_template()


def test_template_without_placeholder_raises_error(
    tmp_path: Path,
):
    """
    A template without the required document placeholder
    should raise PromptTemplateError.
    """

    template_path = tmp_path / "invalid_prompt.md"

    template_path.write_text(
        "This template has no document placeholder.",
        encoding="utf-8",
    )

    builder = PromptBuilder(template_path)

    with pytest.raises(PromptTemplateError):
        builder.load_template()


# =============================================================================
# Prompt Construction
# =============================================================================

def test_build_prompt_replaces_document_placeholder(
    tmp_path: Path,
):
    """
    Document content should replace the document placeholder.
    """

    template_path = tmp_path / "prompt.md"

    template_path.write_text(
        "Analyse:\n{{DOCUMENT_TEXT}}",
        encoding="utf-8",
    )

    builder = PromptBuilder(template_path)

    result = builder.build_prompt(
        "Customer submits application."
    )

    assert result == (
        "Analyse:\nCustomer submits application."
    )

    assert DOCUMENT_PLACEHOLDER not in result


def test_build_prompt_strips_document_whitespace(
    tmp_path: Path,
):
    """
    Leading and trailing document whitespace should be removed.
    """

    template_path = tmp_path / "prompt.md"

    template_path.write_text(
        "Document:\n{{DOCUMENT_TEXT}}",
        encoding="utf-8",
    )

    builder = PromptBuilder(template_path)

    result = builder.build_prompt(
        "   Invoice approval process   "
    )

    assert result == (
        "Document:\nInvoice approval process"
    )


def test_build_prompt_rejects_non_string_document(
    tmp_path: Path,
):
    """
    document_text must be a string.
    """

    template_path = tmp_path / "prompt.md"

    template_path.write_text(
        "Document:\n{{DOCUMENT_TEXT}}",
        encoding="utf-8",
    )

    builder = PromptBuilder(template_path)

    with pytest.raises(TypeError):
        builder.build_prompt(123)


# =============================================================================
# Preview
# =============================================================================

def test_preview_prompt_returns_full_prompt_when_short(
    tmp_path: Path,
):
    """
    A short prompt should not be truncated.
    """

    template_path = tmp_path / "prompt.md"

    template_path.write_text(
        "Document:\n{{DOCUMENT_TEXT}}",
        encoding="utf-8",
    )

    builder = PromptBuilder(template_path)

    result = builder.preview_prompt(
        "Invoice approval",
        max_length=500,
    )

    assert result == (
        "Document:\nInvoice approval"
    )


def test_preview_prompt_truncates_long_prompt(
    tmp_path: Path,
):
    """
    A prompt longer than max_length should be truncated.
    """

    template_path = tmp_path / "prompt.md"

    template_path.write_text(
        "Document:\n{{DOCUMENT_TEXT}}",
        encoding="utf-8",
    )

    builder = PromptBuilder(template_path)

    result = builder.preview_prompt(
        "A" * 100,
        max_length=20,
    )

    assert result.startswith(
        "Document:\nAAAAAAAAAA"
    )

    assert result.endswith(
        "\n\n... (truncated)"
    )


def test_preview_prompt_rejects_invalid_max_length(
    tmp_path: Path,
):
    """
    max_length must be greater than zero.
    """

    template_path = tmp_path / "prompt.md"

    template_path.write_text(
        "Document:\n{{DOCUMENT_TEXT}}",
        encoding="utf-8",
    )

    builder = PromptBuilder(template_path)

    with pytest.raises(ValueError):
        builder.preview_prompt(
            "Invoice approval",
            max_length=0,
        )