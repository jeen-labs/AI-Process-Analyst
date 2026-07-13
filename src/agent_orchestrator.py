"""
===============================================================================
AI Process Analyst
===============================================================================

Module:
    agent_orchestrator.py

Purpose:
    Coordinate the end-to-end document processing workflow.

Responsibilities:
    - Coordinate platform modules
    - Execute processing pipeline
    - Handle workflow execution
    - Prepare for future multi-agent orchestration

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

from pathlib import Path

# =============================================================================
# Third-Party Imports
# =============================================================================

# (None)

# =============================================================================
# Project Imports
# =============================================================================

from document_loader import DocumentLoader
from document_reader import DocumentReader
from document_parser import DocumentParser
from llm_client import LLMClient
from schema_validator import SchemaValidator
from process_repository import ProcessRepository

# =============================================================================
# Classes
# =============================================================================


class AgentOrchestrator:
    """
    Coordinate the AI Process Analyst workflow.

    This class manages the interaction between platform modules.
    """

    def __init__(self) -> None:
        """Initialise platform components."""

        self.loader = DocumentLoader()
        self.reader = DocumentReader()
        self.parser = DocumentParser()
        self.llm = LLMClient()
        self.validator = SchemaValidator()
        self.repository = ProcessRepository()

    def run(self, document_path: str) -> bool:
        """
        Execute the complete document processing workflow.

        Parameters
        ----------
        document_path : str
            Path to the business process document.

        Returns
        -------
        bool
            True if processing completed successfully.
        """

        print("=" * 70)
        print("AI PROCESS ANALYST")
        print("=" * 70)

        print("Step 1 : Validating document")

        path = self.loader.resolve_document(document_path)

        print("✓ Document validated")

        print("Step 2 : Reading document")

        document_text = self.reader.read(path)

        print("✓ Document read")

        print("Step 3 : Preparing document")

        parsed_document = self.parser.parse(document_text)

        print("✓ Document prepared")

        print("Step 4 : Sending prompt to AI")

        prompt = "\n".join(parsed_document)

        response = self.llm.generate_response(prompt)

        print("✓ AI response received")

        print("Step 5 : Validating AI output")

        validation = self.validator.validate(response)

        if validation["valid"]:

            self.repository.save(response)

            print("✓ Process stored")

        else:

            print("Validation failed:")

            for error in validation["errors"]:
                print(f" - {error}")

        print()

        print("Workflow complete.")

        return True


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":

    orchestrator = AgentOrchestrator()

    print("Agent Orchestrator initialised successfully.")