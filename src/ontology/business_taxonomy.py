"""
===============================================================================
Enterprise Business Taxonomy
===============================================================================

Keyword-based enterprise taxonomy.

This is Version 1.

Later this becomes:

- ontology graph
- synonym engine
- semantic search
- knowledge graph

Author:
Jeen Labs
===============================================================================
"""

from __future__ import annotations

from typing import Dict

from .ontology_types import (
    BusinessCategory,
    BusinessDomain,
)


class BusinessTaxonomy:

    DOMAIN_KEYWORDS: Dict[str, BusinessDomain] = {

        "invoice": BusinessDomain.FINANCE,
        "payment": BusinessDomain.FINANCE,
        "finance": BusinessDomain.FINANCE,

        "purchase": BusinessDomain.PROCUREMENT,
        "vendor": BusinessDomain.PROCUREMENT,
        "procurement": BusinessDomain.PROCUREMENT,

        "employee": BusinessDomain.HR,
        "recruitment": BusinessDomain.HR,
        "leave": BusinessDomain.HR,

        "customer": BusinessDomain.CUSTOMER_SERVICE,
        "ticket": BusinessDomain.CUSTOMER_SERVICE,

        "server": BusinessDomain.IT,
        "application": BusinessDomain.IT,
        "system": BusinessDomain.IT,
    }

    CATEGORY_KEYWORDS: Dict[str, BusinessCategory] = {

        "approve": BusinessCategory.APPROVAL,
        "approval": BusinessCategory.APPROVAL,

        "review": BusinessCategory.REVIEW,

        "create": BusinessCategory.CREATION,
        "generate": BusinessCategory.CREATION,

        "validate": BusinessCategory.VALIDATION,
        "verify": BusinessCategory.VALIDATION,

        "pay": BusinessCategory.PAYMENT,
        "payment": BusinessCategory.PAYMENT,

        "notify": BusinessCategory.NOTIFICATION,
        "email": BusinessCategory.NOTIFICATION,

        "enter": BusinessCategory.DATA_ENTRY,

        "report": BusinessCategory.REPORTING,
    }