"""
===============================================================================
AI Process Analyst
===============================================================================

Module:
    orchestration.planner

Purpose:
    Provide the enterprise orchestration layer with a deterministic planner
    responsible for converting a process-analysis request into an ordered
    execution plan.

Responsibilities:
    - Accept a process-analysis request
    - Validate planner input
    - Produce a deterministic execution plan
    - Keep planning separate from execution
    - Keep planning separate from LLM communication
    - Provide a stable interface for future agentic planning

Architecture:
    Enterprise AI Orchestration Layer

Phase:
    Milestone 3 - Enterprise AI Orchestration Layer
    Phase 3.6 - Add Planner

This component does NOT:
    - Execute LLM requests
    - Build prompts
    - Parse LLM responses
    - Execute tools or agents
    - Apply business rules
    - Perform schema validation
    - Modify process data
    - Execute the generated plan

The planner establishes the boundary between:
    Request
        |
        v
    Planner
        |
        v
    Execution Plan
        |
        v
    Orchestration Pipeline

The initial implementation is intentionally deterministic. Future phases can
replace or extend the planning logic with policy-aware, agent-aware or
LLM-assisted planning without changing the orchestration pipeline contract.
===============================================================================
"""

# =============================================================================
# Standard Library Imports
# =============================================================================

from typing import Any


# =============================================================================
# Exceptions
# =============================================================================


class PlannerError(ValueError):
    """
    Base exception raised for planner validation or planning failures.
    """

    pass


# =============================================================================
# Planner
# =============================================================================


class Planner:
    """
    Deterministic planner for the enterprise orchestration layer.

    The Planner converts a process-analysis request into an ordered execution
    plan.

    Planning is intentionally separated from execution. The Planner does not
    invoke the LLM, execute tools, parse responses, or modify process data.
    """

    def __init__(self) -> None:
        """
        Initialise the Planner.
        """

        pass

    # =========================================================================
    # Public API
    # =========================================================================

    def plan(self, request: str) -> dict[str, Any]:
        """
        Create an execution plan for a process-analysis request.

        Parameters
        ----------
        request : str
            Process-analysis request supplied to the orchestration layer.

        Returns
        -------
        dict[str, Any]
            Deterministic execution plan.

        Raises
        ------
        PlannerError
            If the request is not a valid non-empty string.
        """

        if not isinstance(request, str):
            raise PlannerError(
                "Planning request must be a string."
            )

        if not request.strip():
            raise PlannerError(
                "Planning request cannot be empty."
            )

        return {
            "request": request.strip(),
            "plan_type": "process_analysis",
            "steps": [
                {
                    "step": 1,
                    "name": "build_prompt",
                    "description": (
                        "Build the analysis prompt from the process request."
                    ),
                },
                {
                    "step": 2,
                    "name": "execute_llm",
                    "description": (
                        "Send the generated prompt to the configured LLM."
                    ),
                },
                {
                    "step": 3,
                    "name": "parse_response",
                    "description": (
                        "Parse the raw LLM response into structured data."
                    ),
                },
            ],
        }

    # =========================================================================
    # Validation
    # =========================================================================

    def is_valid_request(self, request: str) -> bool:
        """
        Determine whether a planning request is valid.

        Parameters
        ----------
        request : str
            Candidate planning request.

        Returns
        -------
        bool
            True when the request is a non-empty string; otherwise False.
        """

        if not isinstance(request, str):
            return False

        return bool(request.strip())


# =============================================================================
# Main
# =============================================================================


if __name__ == "__main__":

    planner = Planner()

    execution_plan = planner.plan(
        "Analyse the customer onboarding process."
    )

    print("=" * 80)
    print("PLANNER PREVIEW")
    print("=" * 80)

    print(execution_plan)
