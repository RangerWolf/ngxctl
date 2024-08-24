# ngxctl/top.py

import click
from ngxctl import sql_utils  # 更新后的导入路径


@click.command()
@click.option('--conf', default='/etc/nginx/nginx.conf', help='Path to the nginx configuration file.')
@click.option('--group-by', default=None, help='Group results by specified fields, e.g., remote_addr, user_agent.')
@click.option('--order-by', default=None, help='Order results by specified criteria, e.g., avg(bytes_sent) * count.')
@click.option('--filter', default=None, help="Filter results based on conditions, e.g., 'status==404'.")
@click.option('--no-follow', is_flag=True, help='Read the entire log file without following new entries.')
def top(conf, group_by, order_by, filter, no_follow):
    """Display top statistics from Nginx logs."""
    click.echo(f'TABLE_NAME from sql_utils: {sql_utils.TABLE_NAME}')

    click.echo(f'Using config: {conf}')
    click.echo(f'Group by: {group_by}')
    click.echo(f'Order by: {order_by}')
    click.echo(f'Filter: {filter}')
    click.echo(f'No follow: {no_follow}')

    click.echo('Processing Nginx logs...')


if __name__ == "__main__":
    top()
