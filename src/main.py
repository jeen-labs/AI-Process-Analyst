"""
AI Process Analyst

Main application entry point.

This module coordinates the high-level execution of the platform.

Version: 0.1.0
Status: Development
"""

from document_loader import DocumentLoader


def main():
    """
    Application entry point.
    """

    print("=" * 60)
    print("AI Process Analyst")
    print("Version 0.1.0")
    print("=" * 60)

    loader = DocumentLoader()

    print("\nPlatform initialised successfully.")
    print(f"Supported document types: {loader.supported_extensions}")


if __name__ == "__main__":
    main()