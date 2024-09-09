"""This module defines the CLI (Command Line Interface) for the Coophive application."""

import os

import click
import pandas as pd

from coophive import constants, utils

CLI_TIME = str(pd.Timestamp.now().floor("T")).replace(":", "-").replace(" ", "_")
output_path: str


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.option("--verbose", is_flag=True)
@click.option("--no-color", is_flag=True)
@click.option("--logs-filename", default="coophive-{time}.log")
@click.option(
    "--output-path",
    default="../coophive_output/",
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


# cli.command('seller'):
# agent = Agent(policy='ridge_regressor')
# states = LoadStates()
# agent.train(states=states)
# def ():
# Clarify the relationship between these two steps:
# uvicorn.run(agent)
# agent.infer(received_message)

# cli.command('buyer'):
# agent = Agent(policy='naive_accepter')
# ...
