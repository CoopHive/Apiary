"""This module defines various utility classes and functions for the CoopHive simulator."""

import hashlib
import json
import logging
from dataclasses import dataclass

import colorlog


def template(input: str, variables: dict) -> None:
    """Replace placeholders in the input string with values from the variables dictionary."""
    for key, value in variables.items():
        key = "{" + key + "}"
        input = input.replace(key, str(value))

    return input


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


def log_json(message, data=None):
    """Log a message and optional data in JSON format.

    Args:
        message (str): The logging message.
        data (dict, optional): A dictionary of additional data to be logged. Defaults to None.

    The function combines the message and data into a single JSON object and logs it using the provided logger.
    """
    log_entry = {"message": message}
    if data:
        log_entry.update(data)

    try:
        # Attempt to serialize the entire log_entry and log it
        logging.info(json.dumps(log_entry))
    except (TypeError, ValueError) as e:
        # Log the error if the entire log_entry is not JSON serializable
        logging.error(f"Logging error: {e}")


@dataclass
class Tx:
    """Ethereum transaction metadata."""

    sender: str
    value: float  # [wei]


def hash_dict(dict) -> str:
    """Generate a SHA-256 hash of a dictionary.

    Args:
        dict (dict): Dictionary to be hashed.

    Returns:
        str: Hexadecimal representation of the SHA-256 hash.
    """
    hash_function = hashlib.sha256()
    encoded = json.dumps(dict, sort_keys=True).encode()
    hash_function.update(encoded)
    return hash_function.hexdigest()
