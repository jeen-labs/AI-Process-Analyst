"""
===============================================================================
AI Process Analyst
===============================================================================

Application Entry Point

Purpose:
    Coordinate the end-to-end execution of the AI Process Analyst pipeline.

Author:
    Jeen Labs

Version:
    0.3.0

Status:
    Development
===============================================================================
"""

# =============================================================================
# Standard Library Imports
# =============================================================================

from pathlib import Path

# =============================================================================
# Project Imports
# =============================================================================

from document_catalog import DocumentCatalog
from document_loader import DocumentLoader
from document_reader import DocumentReader
from document_parser import DocumentParser
from prompt_builder import PromptBuilder
from llm_client import LLMClient
from response_parser import ResponseParser
from schema_validator import SchemaValidator
from process_repository import ProcessRepository


# =============================================================================
# Application
# =============================================================================

class AIProcessAnalyst:
    """
    Main application orchestrator.
    """

    def __init__(self) -> None:

        self.catalog = DocumentCatalog()
        self.loader = DocumentLoader()
        self.reader = DocumentReader()
        self.parser = DocumentParser()
        self.prompt_builder = PromptBuilder()
        self.llm = LLMClient()
        self.response_parser = ResponseParser()
        self.validator = SchemaValidator()
        self.repository = ProcessRepository()

    # -------------------------------------------------------------------------

    def run(self) -> None:
        """
        Execute the complete application workflow.
        """

        print("=" * 80)
        print("AI PROCESS ANALYST")
        print("Enterprise Process Intelligence Platform")
        print("=" * 80)

        print("\nActive LLM Configuration")

        configuration = self.llm.get_configuration()

        for key, value in configuration.items():

            print(f"  {key:<18}: {value}")

        print()

        document_folder = Path("sample_documents")

        try:

            documents = self.catalog.discover_documents(document_folder)

        except FileNotFoundError:

            print("Sample document folder not found.")

            return

        if not documents:

            print("No supported documents discovered.")

            return

        print(f"{len(documents)} document(s) discovered.\n")

        for document in documents:

            self.process_document(document)

        print("\nApplication completed successfully.")

    # -------------------------------------------------------------------------

    def process_document(self, document: Path) -> None:
        """
        Process a single document.
        """

        print("=" * 80)
        print(f"Processing Document : {document.name}")
        print("=" * 80)

        try:

            #
            # Stage 1
            #

            print("[1/8] Loading document...")

            loaded_document = self.loader.load(document)

            #
            # Stage 2
            #

            print("[2/8] Reading document...")

            document_text = self.reader.read(loaded_document)

            #
            # Stage 3
            #

            print("[3/8] Parsing document...")

            parsed_document = self.parser.parse(document_text)

            #
            # Stage 4
            #

            print("[4/8] Building extraction prompt...")

            prompt = self.prompt_builder.build_prompt(parsed_document)

            #
            # Stage 5
            #

            print("[5/8] Calling LLM...")

            response = self.llm.generate_response(prompt)

            #
            # Stage 6
            #

            print("[6/8] Parsing LLM response...")

            extracted_process = self.response_parser.parse(response)

            #
            # Stage 7
            #

            print("[7/8] Validating extracted process...")

            self.validator.validate(extracted_process)

            #
            # Stage 8
            #

            print("[8/8] Saving process repository...")

            self.repository.save(extracted_process)

            print("Document processed successfully.\n")

        except Exception as error:

            print(f"\nProcessing failed:\n{error}\n")


# =============================================================================
# Entry Point
# =============================================================================

def main() -> None:
    """
    Application entry point.
    """

    application = AIProcessAnalyst()

    application.run()


if __name__ == "__main__":

    main()