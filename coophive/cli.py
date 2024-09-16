"""This module defines the CLI (Command Line Interface) for the Coophive application."""

import json
import logging
import os
import subprocess
from datetime import datetime

import click

from coophive import constants, utils
from coophive.buyer import Buyer
from coophive.seller import Seller

current_time = datetime.now().replace(second=0, microsecond=0)

CLI_TIME = current_time.strftime("%Y-%m-%d_%H-%M")
output_path: str


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.option("--verbose", is_flag=True)
@click.option("--no-color", is_flag=True)
@click.option("--logs-filename", default="coophive-{time}.log")
@click.option(
    "--output-path",
    default="./coophive_output/",
)
def cli(
    verbose: bool,
    no_color: bool,
    logs_filename: str,
    output_path: str,
):
    """Management CLI for CoopHive."""
    constants.VERBOSE = verbose
    constants.NO_COLOR = no_color

    logs_filename = utils.template(logs_filename, dict(time=CLI_TIME))

    output_dir = os.path.dirname(output_path)
    os.makedirs(output_dir, exist_ok=True)

    logs_path = os.path.join(output_dir, logs_filename)

    utils.setup_logger(logs_path=logs_path, verbose=verbose, no_color=no_color)


@cli.command()
@click.option(
    "--private-key",
    required=True,
)
@click.option(
    "--public-key",
    required=True,
)
@click.option("--messaging-client-url", default="redis://localhost:6379")
@click.option("--policy-name", required=True, help="Agent Policy.")
def sell(
    private_key: str, public_key: str, messaging_client_url: str, policy_name: str
):
    """Sell."""
    logging.info(f"Messaging client: {messaging_client_url}")
    logging.info(f"Policy name: {policy_name}")
    subprocess.run(["uvicorn", "coophive.fastapi_app:app", "--reload"], check=True)


@cli.command()
@click.option("--initial-offer", required=True, help="Buyer Agent Initial Policy.")
@click.option(
    "--private-key",
    required=True,
)
@click.option(
    "--public-key",
    required=True,
)
@click.option("--messaging-client-url", default="redis://localhost:6379")
@click.option("--policy-name", required=True, help="Agent Policy.")
def buy(
    initial_offer: str,
    private_key: str,
    public_key: str,
    messaging_client_url: str,
    policy_name: str,
):
    """Buy."""
    logging.info(f"Initial Offer: {initial_offer}")
    logging.info(f"Messaging client: {messaging_client_url}")
    logging.info(f"Policy name: {policy_name}")

    command = f"redis-cli publish initial_offers '{initial_offer}'"
    subprocess.run(command, shell=True, text=True)

    initial_offer = json.loads(initial_offer)

    pubkey = initial_offer["pubkey"]

    buyer = Buyer(
        private_key=private_key,
        public_key=public_key,
        messaging_client_url=messaging_client_url,
        policy_name=policy_name,
    )

    tmp = buyer.policy.infer(
        "Some scheme-compliant message from seller, read by buyer."
    )

    # TODO: migrate these functionalities within the agent above.
    # TODO: bug: this cli is wrong, in the example the message represented the buyer,
    # the agent here is seller. Fix.
    command = "cd ../redis-scheme-client/src && bun run runner.ts seller localhost:3000"
    subprocess.run(command, shell=True, text=True)
