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
    0.2.0

Status:
    Development
===============================================================================
"""

# =============================================================================
# Standard Library Imports
# =============================================================================

from pathlib import Path
from typing import Any

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
    Central configuration loader for the application.
    """

    CONFIG_DIRECTORY = CONFIG_DIRECTORY

    # -------------------------------------------------------------------------

    @classmethod
    def load_yaml(
        cls,
        filename: str
    ) -> dict[str, Any]:
        """
        Load a YAML configuration file.

        Parameters
        ----------
        filename : str

        Returns
        -------
        dict
        """

        file_path = cls.CONFIG_DIRECTORY / filename

        if not file_path.exists():

            raise FileNotFoundError(
                f"Configuration file not found:\n{file_path}"
            )

        with file_path.open(
            mode="r",
            encoding="utf-8"
        ) as yaml_file:

            configuration = yaml.safe_load(yaml_file)

        if configuration is None:

            return {}

        if not isinstance(configuration, dict):

            raise ValueError(
                f"{filename} must contain a YAML dictionary."
            )

        return configuration

    # -------------------------------------------------------------------------

    @classmethod
    def load_configuration(
        cls,
        filename: str
    ) -> dict[str, Any]:
        """
        Generic configuration loader.
        """

        return cls.load_yaml(filename)

    # -------------------------------------------------------------------------

    @classmethod
    def load_llm_configuration(cls) -> dict[str, Any]:
        """
        Load LLM configuration.

        This is now the preferred method.
        """

        return cls.load_yaml("llm_config.yaml")

    # -------------------------------------------------------------------------

    @classmethod
    def load_llm_config(cls) -> dict[str, Any]:
        """
        Backward compatibility.

        Older modules may still call this method.
        """

        return cls.load_llm_configuration()

    # -------------------------------------------------------------------------

    @classmethod
    def load_logging_configuration(cls) -> dict[str, Any]:
        """
        Load logging configuration.
        """

        return cls.load_yaml("logging.yaml")

    # -------------------------------------------------------------------------

    @classmethod
    def load_logging_config(cls) -> dict[str, Any]:
        """
        Backward compatibility.
        """

        return cls.load_logging_configuration()

    # -------------------------------------------------------------------------

    @classmethod
    def load_prompt_configuration(cls) -> dict[str, Any]:
        """
        Load prompt configuration.
        """

        return cls.load_yaml("prompts.yaml")

    # -------------------------------------------------------------------------

    @classmethod
    def load_prompt_config(cls) -> dict[str, Any]:
        """
        Backward compatibility.
        """

        return cls.load_prompt_configuration()


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":

    print("=" * 70)
    print("CONFIGURATION TEST")
    print("=" * 70)

    try:

        configuration = ConfigLoader.load_llm_configuration()

        print()

        for key, value in configuration.items():

            print(f"{key:<35}: {value}")

    except Exception as error:

        print(error)