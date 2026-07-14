"""
===============================================================================
AI Process Analyst
===============================================================================

Module:
    config_loader.py

Purpose:
    Load and manage application configuration files.

Responsibilities:
    - Load YAML configuration files
    - Validate configuration file existence
    - Provide a central interface for application configuration
    - Avoid duplicated configuration loading logic

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
from typing import Any, Dict

# =============================================================================
# Third-Party Imports
# =============================================================================

import yaml

# =============================================================================
# Module Constants
# =============================================================================

CONFIG_DIRECTORY = Path("config")

# =============================================================================
# Classes
# =============================================================================


class ConfigLoader:
    """
    Load YAML configuration files for the application.
    """

    def __init__(self) -> None:
        """
        Initialise the configuration loader.
        """
        self.config_directory = CONFIG_DIRECTORY

    def load_yaml(self, filename: str) -> Dict[str, Any]:
        """
        Load a YAML configuration file.

        Parameters
        ----------
        filename : str
            Name of the YAML file.

        Returns
        -------
        Dict[str, Any]
            Parsed configuration.
        """

        file_path = self.config_directory / filename

        if not file_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {file_path}"
            )

        with file_path.open(
            mode="r",
            encoding="utf-8"
        ) as yaml_file:

            configuration = yaml.safe_load(yaml_file)

        return configuration or {}

    def load_llm_config(self) -> Dict[str, Any]:
        """
        Load LLM configuration.

        Returns
        -------
        Dict[str, Any]
        """

        return self.load_yaml("llm_config.yaml")

    def load_logging_config(self) -> Dict[str, Any]:
        """
        Load logging configuration.

        Returns
        -------
        Dict[str, Any]
        """

        return self.load_yaml("logging.yaml")

    def load_prompt_config(self) -> Dict[str, Any]:
        """
        Load prompt configuration.

        Returns
        -------
        Dict[str, Any]
        """

        return self.load_yaml("prompts.yaml")


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":

    loader = ConfigLoader()

    print("=" * 70)
    print("CONFIGURATION TEST")
    print("=" * 70)

    try:

        configuration = loader.load_llm_config()

        for key, value in configuration.items():

            print(f"{key}: {value}")

    except FileNotFoundError as error:

        print(error)