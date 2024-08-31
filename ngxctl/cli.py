# ngxctl/cli.py

import click
from ngxctl.cmds import top


@click.group()
def cli():
    """ngxctl: A command-line tool for managing and analyzing Nginx."""
    pass

# Add subcommands to the cli group
cli.add_command(top.run)

if __name__ == "__main__":
    cli()
