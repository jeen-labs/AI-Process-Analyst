"""
===============================================================================
AI Process Analyst
===============================================================================

Module:
    mock_llm_response.py

Purpose:
    Generate enterprise-grade mock LLM responses during development.

Responsibilities:
    - Produce valid enterprise process JSON
    - Simulate AI extraction
    - Support regression testing
    - Exercise the complete processing pipeline

Author:
    Jeen Labs

Version:
    0.1.0

Status:
    Development
===============================================================================
"""

# =============================================================================
# Standard Library Imports
# =============================================================================

import json
import uuid
from datetime import datetime

# =============================================================================
# Module Constants
# =============================================================================

SCHEMA_VERSION = "0.2.0"

PROCESS_VERSION = "1.0"

STATUS = "Draft"


# =============================================================================
# Helper Functions
# =============================================================================

def new_id(prefix: str) -> str:
    """
    Generate a unique enterprise identifier.
    """

    return f"{prefix}-{uuid.uuid4().hex[:8].upper()}"


# =============================================================================
# Public Functions
# =============================================================================

def generate_mock_response() -> str:
    """
    Return a complete enterprise process JSON document.

    Returns
    -------
    str
        JSON string.
    """

    now = datetime.utcnow().isoformat()

    process = {

        "metadata": {

            "process_id": new_id("PROC"),

            "process_name": "Customer Onboarding",

            "parent_process": None,

            "previous_process": None,

            "next_process": None,

            "process_level": 1,

            "version": PROCESS_VERSION,

            "status": STATUS,

            "created_by": "AI Process Analyst",

            "created_on": now,

            "schema_version": SCHEMA_VERSION
        },

        "overview": {

            "description":
                "End-to-end onboarding of a new customer.",

            "objective":
                "Open a customer account after successful verification.",

            "scope":
                "Retail customer onboarding.",

            "trigger":
                "Customer submits an application.",

            "end_condition":
                "Customer account is activated."
        },

        "actors": [

            {

                "actor_id": new_id("ACTOR"),

                "actor_name": "Customer",

                "actor_type": "External"

            },

            {

                "actor_id": new_id("ACTOR"),

                "actor_name": "Operations Officer",

                "actor_type": "Internal"

            },

            {

                "actor_id": new_id("ACTOR"),

                "actor_name": "Operations Manager",

                "actor_type": "Internal"

            }

        ],

        "systems": [

            "CRM System",

            "Document Management System"

        ],

        "documents": [

            "Customer Application",

            "Identity Proof",

            "Address Proof"

        ],

        "inputs": [

            "Application Form",

            "Supporting Documents"

        ],

        "outputs": [

            "Customer Account",

            "Welcome Email"

        ],

        "activities": [

            {

                "activity_id": new_id("ACT"),

                "activity_name": "Receive Application",

                "activity_type": "Start Event",

                "actor": "Customer"

            },

            {

                "activity_id": new_id("ACT"),

                "activity_name": "Verify Documents",

                "activity_type": "User Task",

                "actor": "Operations Officer"

            },

            {

                "activity_id": new_id("ACT"),

                "activity_name": "Approve Customer",

                "activity_type": "Approval",

                "actor": "Operations Manager"

            },

            {

                "activity_id": new_id("ACT"),

                "activity_name": "Create Customer Account",

                "activity_type": "System Task",

                "actor": "CRM System"

            },

            {

                "activity_id": new_id("ACT"),

                "activity_name": "Send Welcome Email",

                "activity_type": "End Event",

                "actor": "CRM System"

            }

        ],

        "decisions": [

            {

                "decision_id": new_id("DEC"),

                "decision_name": "Documents Complete?",

                "decision_type": "Exclusive Gateway"

            }

        ],

        "business_rules": [

            {

                "rule_id": new_id("RULE"),

                "rule_name": "Identity Verification",

                "rule_description":
                    "Customer identity must be verified before approval."

            },

            {

                "rule_id": new_id("RULE"),

                "rule_name": "Manager Approval",

                "rule_description":
                    "Manager approval is mandatory before account creation."

            }

        ],

        "risks": [

            "Fraudulent identity",

            "Missing mandatory documentation"

        ],

        "controls": [

            "KYC Verification",

            "Manager Approval"

        ],

        "kpis": [

            "Average onboarding time",

            "First-time approval rate"

        ],

        "relationships": {

            "previous_process": None,

            "next_process": "Customer Account Maintenance",

            "subprocesses": [

                "Identity Verification",

                "Account Creation"

            ]
        },

        "source": {

            "document_name":
                "customer_onboarding_process_specification.md",

            "document_type":
                "Markdown",

            "page_numbers": [

                1

            ],

            "confidence_score":

                0.98
        }

    }

    return json.dumps(process, indent=4)


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":

    print("=" * 80)
    print("MOCK LLM RESPONSE")
    print("=" * 80)

    print(generate_mock_response())