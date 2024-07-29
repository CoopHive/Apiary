"""This module defines the CLI (Command Line Interface) for the Coophive application."""

import click


@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
)
def cli():
    """Coophive."""
    pass
