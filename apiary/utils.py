"""This module defines various utility classes and functions for the CoopHive simulator."""

import csv
import json
import logging
import os
import uuid
from datetime import datetime
from typing import TypedDict, Union

import colorlog
import matplotlib.pyplot as plt
import pandas as pd
import readwrite as rw
from dotenv import load_dotenv
from lighthouseweb3 import Lighthouse

load_dotenv(override=True)


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


class ERC20Token(TypedDict):
    """ERC20."""

    tokenStandard: str
    address: str
    amt: int


class ERC721Token(TypedDict):
    """ERC721."""

    tokenStandard: str
    address: str
    id: int


Token = Union[ERC20Token, ERC721Token]


def upload_and_get_cid(input, is_file_path):
    """Uploads content to Lighthouse and retrieves the content identifier (CID)."""
    lh = Lighthouse(os.getenv("LIGHTHOUSE_TOKEN"))
    if is_file_path:
        file_path = input
    else:
        if not isinstance(input, str):
            raise ValueError

        if not os.path.exists("tmp"):
            os.makedirs("tmp")

        file_path = "tmp/job_input.txt"
        rw.write(input, file_path)
    try:
        response = lh.upload(file_path)
        cid = response["data"]["Hash"]
    except Exception:
        logging.error("Lighthouse Error occurred.", exc_info=True)
        raise
    logging.info(f"https://gateway.lighthouse.storage/ipfs/{cid}")

    return cid


def create_offer_tokens(tokens_data: list) -> Token:
    """Create offer-compatible tokens object from buyer inputs tokens data."""
    if not all(isinstance(entry, list) for entry in tokens_data):
        # Uniformize format to bundles of assets for the one-dimensional case.
        tokens_data = [tokens_data]

    offer_tokens = []
    for token_data in tokens_data:
        token_standard = token_data[0]
        address = token_data[1]

        if token_standard == "ERC20":
            amt = token_data[2]
            os.environ["VALUATION_ESTIMATION"] = str(amt)
            offer_token = {"tokenStandard": "ERC20", "address": address, "amt": amt}
        elif token_standard == "ERC721":
            offer_token = {
                "tokenStandard": "ERC721",
                "address": address,
                "id": token_data[2],
            }
        else:
            raise ValueError(f"Unsupported token standard: {token_standard}")

        offer_tokens.append(offer_token)
    return offer_tokens


def parse_initial_offer(job_path, tokens_data):
    """Parses an initial offer for a compute job, including the job type, job content, and associated tokens.

    This function determines the job type based on the file extension of the provided job path, uploads the job to Lighthouse,
    and generates a unique offer ID. It then prepares the offer data, including the job CID, tokens, and additional metadata.
    """
    pubkey = os.getenv("PUBLIC_KEY")

    if job_path.split(".")[-1] == "Dockerfile":
        job_type = "docker"
    else:
        logging.error(f"Unsupported job type for file {job_path}.")
        raise

    job_cid = upload_and_get_cid(job_path, is_file_path=True)

    # TODO: placeholder to be abstracted at the cli level of the package.
    # Currently only cowsay supported!
    job_input = "Paying with ERC20, ERC721 or a generic combination of the two for Compute jobs is very nice!"

    job_input_cid = upload_and_get_cid(job_input, is_file_path=False)

    query = {"job_type": job_type, "job_cid": job_cid, "job_input_cid": job_input_cid}

    data = {
        "_tag": "offer",
        "query": query,
    }

    tokens_data = json.loads(tokens_data)
    tokens = create_offer_tokens(tokens_data)

    data["tokens"] = tokens

    # Initial Offer UNIX time (Buyer Measurement): negotiation thread t0.
    utc_time = datetime.utcnow().timestamp()
    os.environ["T0"] = str(utc_time)

    return {
        "pubkey": pubkey,
        "offerId": str(uuid.uuid4()),
        "initial": True,
        "data": data,
    }


def add_float_to_csv(value, filename: str):
    """Append a float value to a CSV file."""
    file_path = f"apiary_output/{filename}.csv"
    file_exists = os.path.isfile(file_path)

    with open(file_path, mode="a", newline="") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Amount"])
        writer.writerow([value])


def plot_negotiation(filename: str):
    """Plot negotiation offers from a CSV file file_path."""
    file_path = f"apiary_output/{filename}.csv"
    df = pd.read_csv(file_path)

    num_entries = len(df)
    downsample_rate = 1  # No downsampling by default
    max_points = 400

    if num_entries > max_points:
        downsample_rate = num_entries // max_points

    odd_entries = df.iloc[::2][::downsample_rate]
    even_entries = df.iloc[1::2][::downsample_rate]

    unit_price = 1e-6  # TODO: hardcoded, may change for != USDC.
    plt.figure(figsize=(13, 5))
    plt.plot(
        odd_entries.index,
        odd_entries * unit_price,
        color="g",
        linewidth=1.5,
        label="Seller Offers",
    )
    plt.plot(
        even_entries.index,
        even_entries * unit_price,
        color="m",
        linewidth=1.5,
        label="Buyer Offers",
    )

    plt.title("Negotiation Rounds vs Offers", fontsize=16, fontweight="bold")
    plt.xlabel("Negotiation Round []", fontsize=12)
    plt.ylabel("Offer [USDC]", fontsize=12)  # TODO: remove hardcoded.
    plt.grid(True, linestyle="--", linewidth=0.5)

    plt.legend()

    plt.tight_layout()

    plt.savefig(f"apiary_output/{filename}.png")
    plt.close()
