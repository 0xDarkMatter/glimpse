"""Main CLI entry point for Glimpse RV"""

import click
from dotenv import load_dotenv

from glimpse.commands import create, list_cmd, reveal, status

# Load environment variables
load_dotenv()


@click.group()
@click.version_option(version='0.2.0')
def cli():
    """CLI application for Remote Viewing testing with random target images"""
    pass


# Register commands
cli.add_command(create.create)
cli.add_command(list_cmd.list_sessions)
cli.add_command(reveal.reveal)
cli.add_command(status.status)


if __name__ == '__main__':
    cli()
