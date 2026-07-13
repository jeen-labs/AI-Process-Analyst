"""
===============================================================================
AI Process Analyst
===============================================================================

Module:
    main.py

Purpose:
    Application entry point for the AI Process Analyst platform.

Responsibilities:
    - Display application information
    - Initialise core platform components
    - Start the document processing workflow
    - Handle application-level exceptions

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

import sys

# =============================================================================
# Third-Party Imports
# =============================================================================

# (None)

# =============================================================================
# Project Imports
# =============================================================================

from document_loader import DocumentLoader

# =============================================================================
# Module Constants
# =============================================================================

APPLICATION_NAME = "AI Process Analyst"
APPLICATION_VERSION = "0.1.0"

# =============================================================================
# Main Functions
# =============================================================================


def display_banner() -> None:
    """Display the application banner."""

    print("=" * 70)
    print(f"{APPLICATION_NAME}")
    print(f"Version: {APPLICATION_VERSION}")
    print("=" * 70)


def initialise_platform() -> DocumentLoader:
    """
    Initialise platform components.

    Returns
    -------
    DocumentLoader
        Initialised document loader instance.
    """

    print("Initialising platform...")

    loader = DocumentLoader()

    print("Platform initialised successfully.")

    return loader


def main() -> int:
    """
    Main application entry point.

    Returns
    -------
    int
        Process exit code.
    """

    try:

        display_banner()

        loader = initialise_platform()

        print()
        print("Supported document types:")

        for extension in loader.supported_extensions:
            print(f"  • {extension}")

        print()
        print("System ready.")

        return 0

    except Exception as error:

        print(f"Application Error: {error}")

        return 1


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    sys.exit(main())