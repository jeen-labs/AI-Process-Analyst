"""
===============================================================================
Ontology Types
===============================================================================

Defines common ontology enumerations.

Author:
Jeen Labs
===============================================================================
"""

from enum import Enum


class BusinessDomain(str, Enum):

    FINANCE = "finance"
    PROCUREMENT = "procurement"
    SALES = "sales"
    HR = "human_resources"
    CUSTOMER_SERVICE = "customer_service"
    IT = "information_technology"
    LEGAL = "legal"
    OPERATIONS = "operations"
    COMPLIANCE = "compliance"
    UNKNOWN = "unknown"


class BusinessCategory(str, Enum):

    APPROVAL = "approval"
    REVIEW = "review"
    CREATION = "creation"
    VALIDATION = "validation"
    PAYMENT = "payment"
    PROCUREMENT = "procurement"
    REPORTING = "reporting"
    NOTIFICATION = "notification"
    DATA_ENTRY = "data_entry"
    UNKNOWN = "unknown"