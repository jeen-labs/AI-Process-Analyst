"""
===============================================================================
Tests - Enterprise Schema Validator
===============================================================================
"""

import pytest

from src.validator import (
    SchemaValidator,
    ValidationError,
)


def test_valid_model():

    validator = SchemaValidator()

    model = {
        "schemaVersion": "1.0.0",
        "modelVersion": "1.0.0",
        "metadata": {},
        "process": {},
    }

    assert validator.validate(model) is True


def test_missing_schema_version():

    validator = SchemaValidator()

    model = {
        "modelVersion": "1.0.0",
        "metadata": {},
        "process": {},
    }

    with pytest.raises(ValidationError):

        validator.validate(model)


def test_missing_metadata():

    validator = SchemaValidator()

    model = {
        "schemaVersion": "1.0.0",
        "modelVersion": "1.0.0",
        "process": {},
    }

    with pytest.raises(ValidationError):

        validator.validate(model)


def test_invalid_object_type():

    validator = SchemaValidator()

    with pytest.raises(ValidationError):

        validator.validate([])  # type: ignore