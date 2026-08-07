"""
===============================================================================
AI Process Analyst
===============================================================================

Module:
    tests/test_response_parser.py

Purpose:
    Automated tests for the Enterprise ResponseParser.

Phase:
    Milestone 3 - Enterprise AI Orchestration Layer
    Phase 3.3 - Refactor Response Parser
===============================================================================
"""

# =============================================================================
# Imports
# =============================================================================

import pytest

from src.orchestration.response_parser import (
    ResponseParser,
    ResponseParserError,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def parser() -> ResponseParser:
    """
    Provide a ResponseParser instance for tests.
    """

    return ResponseParser()


# =============================================================================
# Initialisation Tests
# =============================================================================


def test_response_parser_initialises():
    """
    ResponseParser should initialise successfully.
    """

    parser = ResponseParser()

    assert parser is not None


# =============================================================================
# JSON Parsing Tests
# =============================================================================


def test_parse_valid_json_object(parser):
    """
    Parser should convert a JSON object into a Python dictionary.
    """

    response = '{"process_name": "Customer Onboarding"}'

    result = parser.parse(response)

    assert isinstance(result, dict)
    assert result["process_name"] == "Customer Onboarding"


def test_parse_valid_json_array(parser):
    """
    Parser should convert a JSON array into a Python list.
    """

    response = '["Submit Application", "Verify Documents"]'

    result = parser.parse(response)

    assert isinstance(result, list)
    assert result == [
        "Submit Application",
        "Verify Documents",
    ]


def test_parse_nested_json(parser):
    """
    Parser should preserve nested JSON structures.
    """

    response = """
    {
        "process": {
            "name": "Customer Onboarding",
            "activities": [
                {
                    "name": "Submit Application"
                }
            ]
        }
    }
    """

    result = parser.parse(response)

    assert result["process"]["name"] == "Customer Onboarding"
    assert result["process"]["activities"][0]["name"] == (
        "Submit Application"
    )


# =============================================================================
# Markdown Code Fence Tests
# =============================================================================


def test_parse_json_code_fence(parser):
    """
    Parser should handle JSON wrapped in a Markdown code fence.
    """

    response = """
    ```json
    {
        "process_name": "Invoice Approval"
    }
    ```
    """

    result = parser.parse(response)

    assert result["process_name"] == "Invoice Approval"


def test_parse_plain_code_fence(parser):
    """
    Parser should handle a generic Markdown code fence.
    """

    response = """
    ```
    {
        "status": "approved"
    }
    ```
    """

    result = parser.parse(response)

    assert result["status"] == "approved"


# =============================================================================
# Validation Tests
# =============================================================================


def test_parse_rejects_non_string_response(parser):
    """
    Parser should reject non-string responses.
    """

    with pytest.raises(ResponseParserError):
        parser.parse({"process_name": "Customer Onboarding"})


def test_parse_rejects_empty_response(parser):
    """
    Parser should reject an empty response.
    """

    with pytest.raises(ResponseParserError):
        parser.parse("")


def test_parse_rejects_whitespace_response(parser):
    """
    Parser should reject a whitespace-only response.
    """

    with pytest.raises(ResponseParserError):
        parser.parse("   \n\t  ")


def test_parse_rejects_invalid_json(parser):
    """
    Parser should raise ResponseParserError for invalid JSON.
    """

    response = '{"process_name": "Customer Onboarding"'

    with pytest.raises(ResponseParserError):
        parser.parse(response)


# =============================================================================
# JSON Validation Tests
# =============================================================================


def test_is_valid_json_returns_true_for_valid_json(parser):
    """
    is_valid_json should return True for valid JSON.
    """

    response = '{"status": "approved"}'

    assert parser.is_valid_json(response) is True


def test_is_valid_json_returns_true_for_code_fenced_json(parser):
    """
    is_valid_json should recognise JSON inside a Markdown code fence.
    """

    response = """
    ```json
    {
        "status": "approved"
    }
    ```
    """

    assert parser.is_valid_json(response) is True


def test_is_valid_json_returns_false_for_invalid_json(parser):
    """
    is_valid_json should return False for invalid JSON.
    """

    response = '{"status": "approved"'

    assert parser.is_valid_json(response) is False


def test_is_valid_json_returns_false_for_empty_response(parser):
    """
    is_valid_json should return False for an empty response.
    """

    assert parser.is_valid_json("") is False


def test_is_valid_json_returns_false_for_non_string(parser):
    """
    is_valid_json should return False for non-string input.
    """

    assert parser.is_valid_json({"status": "approved"}) is False