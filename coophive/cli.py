"""This module defines the CLI (Command Line Interface) for the Coophive application."""

import logging
import os

import click

from coophive.client import Client, create_client
from coophive.job_offer import JobOffer
from coophive.resource_offer import ResourceOffer
from coophive.resource_provider import ResourceProvider
from coophive.smart_contract import SmartContract
from coophive.solver import Solver
from coophive.utils import Tx

logger = logging.getLogger(f"test")
logging.basicConfig(
    filename=f"{os.getcwd()}/local_logs", filemode="w", level=logging.DEBUG
)


@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
)
def cli():
    """Coophive."""
    pass
