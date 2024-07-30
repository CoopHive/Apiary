"""This module provides a logging utility function to log messages in JSON format."""

import json


def log_json(logger, message, data=None):
    """Log a message and optional data in JSON format.

    Args:
        logger (logging.Logger): The logger instance used to log the message.
        message (str): The logging message.
        data (dict, optional): A dictionary of additional data to be logged. Defaults to None.

    The function combines the message and data into a single JSON object and logs it using the provided logger.
    """
    log_entry = {"message": message}
    if data:
        log_entry.update(data)
    logger.info(json.dumps(log_entry))
