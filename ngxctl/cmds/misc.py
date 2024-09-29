# ngxctl/cmds/extract.py

import click
import json
import re

import tabulate

from ngxctl.utils import config_parser


@click.command()
@click.pass_context
def vars(ctx):
    """Read nginx conf and show all variables access logs used"""
    log_path_results = ctx.obj['log_path_results']
    log_format_results = ctx.obj['log_format_results']

    variables = config_parser.get_log_format_used_fields(log_path_results, log_format_results)
    table_data = [[item] for item in variables]
    print(tabulate.tabulate(table_data, headers=['Variables'], tablefmt='orgtbl'))
    ctx.exit()  # 退出程序


@click.command()
@click.pass_context
def files(ctx):
    """Read nginx conf and show all access logs"""
    log_path_results = ctx.obj['log_path_results']
    log_format_results = ctx.obj['log_format_results']

    table_data = []
    headers = ['server_name', 'file_name', 'log_path']
    for item in log_path_results:
        if item['log_type'] == 'access_log':
            row = []
            for header in headers:
                if header == 'log_path':
                    row.append(
                        item.get('log_args')[0]
                    )
                else:
                    row.append(
                        item.get(header, '')
                    )
            table_data.append(row)
    print(tabulate.tabulate(table_data, headers=headers, tablefmt='orgtbl'))
    ctx.exit()  # 退出程序


if __name__ == "__main__":
    vars()