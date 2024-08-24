# ngxctl/cli.py

import click
from ngxctl import top  # 更新后的导入路径

@click.group()
def cli():
    """ngxctl: A command-line tool for managing and analyzing Nginx."""
    pass

# Add subcommands to the cli group
cli.add_command(top.top)

if __name__ == "__main__":
    cli()
