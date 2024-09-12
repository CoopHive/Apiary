"""This module defines the CLI (Command Line Interface) for the Coophive application."""

import json
import logging
import os
import subprocess
from datetime import datetime

import click

from coophive import constants, utils
from coophive.client import Client
from coophive.resource_provider import ResourceProvider

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
@click.option("--messaging-client-url", required=True, help="Agent Policy.")
@click.option("--policy-name", required=True, help="Agent Policy.")
def seller(
    private_key: str, public_key: str, messaging_client_url: str, policy_name: str
):
    """Seller."""
    logging.info(f"Messaging client: {messaging_client_url}")
    logging.info(f"Policy name: {policy_name}")

    # additionalstates = LoadAdditionalStates(policy=policy_name)
    # TODO: given we are going for a stateless implementation, also the environmental states are stored and
    # either loaded only at inference time or loaded to train.
    # In the same way in which the inference is separate from the update of the policy state, as more messages flow in,
    # the policy train/infer are both separate from the population of the environmental state, both historical and point-in-time.

    seller_agent = ResourceProvider(
        private_key=private_key,
        public_key=public_key,
        messaging_client_url=messaging_client_url,
        policy_name=policy_name,
    )
    tmp = seller_agent.policy.infer("Some scheme-compliant message from buyer.")

    # TODO: migrate these functionalities within the agent above.
    command = "cd ../redis-scheme-client/example-agent && bun run index.ts"
    subprocess.run(command, shell=True, text=True)


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
@click.option("--messaging-client-url", required=True, help="Agent Policy.")
@click.option("--policy-name", required=True, help="Agent Policy.")
def buyer(
    initial_offer: str,
    private_key: str,
    public_key: str,
    messaging_client_url: str,
    policy_name: str,
):
    """Buyer."""
    logging.info(f"Initial Offer: {initial_offer}")
    logging.info(f"Messaging client: {messaging_client_url}")
    logging.info(f"Policy name: {policy_name}")

    command = f"redis-cli publish initial_offers '{initial_offer}'"
    subprocess.run(command, shell=True, text=True)

    initial_offer = json.loads(initial_offer)

    pubkey = initial_offer["pubkey"]

    buyer_agent = Client(
        private_key=private_key,
        public_key=public_key,
        messaging_client_url=messaging_client_url,
        policy_name=policy_name,
    )

    tmp = buyer_agent.policy.infer("Some scheme-compliant message from seller.")

    # TODO: migrate these functionalities within the agent above.
    command = "cd ../redis-scheme-client/src && bun run runner.ts seller localhost:3000"
    subprocess.run(command, shell=True, text=True)
