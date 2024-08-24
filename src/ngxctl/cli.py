# src/ngxctl/cli.py

import click
from .commands import top

@click.group()
def cli():
    """ngxctl: A command-line tool for managing and analyzing Nginx."""
    pass

# Add subcommands to the cli group
cli.add_command(top.top)


# 参考的运行代码： python -m src.ngxctl.cli top --conf /etc/nginx/nginx.conf
if __name__ == "__main__":
    cli()
