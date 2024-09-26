"""This module defines various utility classes and functions for the CoopHive simulator."""

import logging
import os

import colorlog
import readwrite as rw
from dotenv import load_dotenv


def template(input: str, variables: dict) -> None:
    """Replace placeholders in the input string with values from the variables dictionary."""
    return input.format_map(variables)


def setup_logger(logs_path, verbose, no_color):
    """Set up a logger with both console and file handlers.

    Args:
        logs_path (str): The path for the log file.
        verbose (bool): If True, set logging level to DEBUG; otherwise, set to INFO.
        no_color (bool): If True, disable color in console output; otherwise, enable color.

    Returns:
        logging.Logger: Configured logger instance.
    """
    console_handler = colorlog.StreamHandler()

    log_format = (
        "%(levelname)s:%(message)s"
        if no_color
        else "%(log_color)s%(levelname)s:%(message)s%(reset)s"
    )

    log_colors = {
        "DEBUG": "green",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "red,bg_white",
    }
    console_handler.setFormatter(
        logging.Formatter(log_format)
        if no_color
        else colorlog.ColoredFormatter(log_format, log_colors)
    )

    logger = colorlog.getLogger()
    logger.addHandler(console_handler)

    if verbose:
        # Set the desired file path here
        file_handler = logging.FileHandler(logs_path)
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        )
        logger.addHandler(file_handler)

    # Set the logging level
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)

    return logger


def set_env_variables(config: dict):
    """Set environment variables based on a configuration dictionary.

    This function flattens the nested dictionary and assigns the corresponding values
    to environment variables. Existing environment variables take precedence over
    values in the config.
    """
    load_dotenv(override=True)

    def get_keys(d, parent_key=""):
        """Recursively flatten dictionary keys."""
        keys = []
        for k, v in d.items():
            new_key = f"{parent_key}.{k}" if parent_key else k
            if isinstance(v, dict):
                keys.extend(get_keys(v, new_key))
            else:
                keys.append(new_key)
        return keys

    def get_value_by_key(d, key):
        """Get the value from a nested dictionary using a flattened key."""
        keys = key.split(".")
        value = d
        for k in keys:
            value = value.get(k)
        return value

    # Flatten the config keys
    keys = get_keys(config)

    for key in keys:
        # Use the dotted keys directly for environment variables
        env_key = key.upper()

        # If the env variable is not already set, use the value from config
        if not os.getenv(env_key):
            value = get_value_by_key(config, key)
            os.environ[env_key] = str(value)
            logging.info(f"Set {env_key} = {value}")


def load_configuration(config_path: str):
    """Load configuration from a file and set environment variables.

    This function reads the configuration from a given file path and sets the
    appropriate environment variables, including setting AGENT_NAME based on the file name if not already defined.
    """
    config = rw.read(config_path)

    if not os.getenv("AGENT_NAME"):
        agent_name = config_path.rpartition(".")[0]
        agent_name = agent_name.rpartition("/")[-1]
        os.environ["AGENT_NAME"] = agent_name
        logging.info(f"Set AGENT_NAME: {agent_name}")

    set_env_variables(config)
