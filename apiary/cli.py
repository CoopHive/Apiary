"""This module defines the CLI (Command Line Interface) for the CoopHive application."""

import os
from datetime import datetime

import click

from apiary import constants, utils

current_time = datetime.now().replace(second=0, microsecond=0)
CLI_TIME = current_time.strftime("%Y-%m-%d_%H-%M")


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.option("--verbose", is_flag=True)
@click.option("--no-color", is_flag=True)
@click.option("--logs-filename", default="CoopHive-{time}.log")
@click.option(
    "--output-path",
    default="./apiary_output/",
)
def cli(
    verbose: bool,
    no_color: bool,
    logs_filename: str,
    output_path: str,
):
    """Management CLI for Apiary."""
    constants.VERBOSE = verbose
    constants.NO_COLOR = no_color

    logs_filename = utils.template(logs_filename, dict(time=CLI_TIME))

    output_dir = os.path.dirname(output_path)
    os.makedirs(output_dir, exist_ok=True)

    logs_path = os.path.join(output_dir, logs_filename)

    utils.setup_logger(logs_path=logs_path, verbose=verbose, no_color=no_color)


@cli.command()
def start_buy():
    """Start Buyer."""
    # TODO: load config
    # env > json > cli_inputs
    # config = {"a": 2, "b": 3}
    # config = {**config, "b":4, "c":5}
    # config = load_config('config.json')
    # config: {dict}

    # TODO: add initial message to cli.
    # initial_offer = .

    # Same as sell...

    pass


@cli.command()
def start_sell():
    """Start Seller."""
    # TODO: load config
    # env > json > cli_inputs
    # config = {"a": 2, "b": 3}
    # config = {**config, "b":4, "c":5}
    # config = load_config('config.json')
    # TODO: store final config as environmental variables with os. (without overwriting entries in .env file)
    # to use them anywhere in the process afterwards.

    # start_job_daemon(config) # launch docker

    # start_inference_endpoint(config)

    # start_messaging_client(config)

    # config = {
    #     'inference_endpoint': {
    #         'port': int, "host": str
    #     }
    # }
    pass


@cli.command()
def cancel_buy(offer_id):
    """Turn Off Buyer Services."""
    # TODO: turn off services in backward order as they have been turned on.
    # TODO: gracefully kill killable process (including messaging cancellation messages to messaging client)
    # and warn user about in-progress processes that cannot be stopped.
    pass


@cli.command()
def cancel_sell():
    """Turn Off Seller Services."""
    # TODO: turn off services in backward order as they have been turned on.
    # TODO: gracefully kill killable process and warn user about in-progress processes that cannot be stopped.
    # TODO: include force flag to kill all the in-progress jobs, else wait for them to turn everything off.
    pass


@cli.command()
def buy_status():
    """Parse log output and show metrics relevant for the Buyer."""
    # TODO
    pass


@cli.command()
def sell_status():
    """Parse log output and show metrics relevant for the Seller."""
    # TODO
    pass
