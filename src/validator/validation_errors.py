"""
===============================================================================
Validation Errors
===============================================================================

Defines validation exceptions used throughout the Enterprise
AI Process Analyst.

Author:
Jeen Labs
===============================================================================
"""


class ValidationError(Exception):
    """
    Raised whenever a canonical process model
    violates schema or business validation rules.
    """

    pass