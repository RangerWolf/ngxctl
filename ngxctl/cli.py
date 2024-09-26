# ngxctl/cli.py

import click
import crossplane
import tabulate
import json
import os.path
from queue import Queue

from ngxctl.cmds import top, misc
from ngxctl.utils import config_parser  # 假设你有一个配置解析工具


@click.group(invoke_without_command=False,
             context_settings=dict(help_option_names=['-h', '--help']))
@click.option('-c', '--conf', default='/etc/nginx/nginx.conf',
              help='Specify the Nginx configuration file. Default is /etc/nginx/nginx.conf.')
# @click.option('--show-vars', is_flag=True,
#               help='List all params that are available for access log.')
# @click.option('--show-logs', is_flag=True,
#               help='List all access log and error log related information.')
# @click.option('--follow/--no-follow', default=True,
#               help='Follow new lines in the log, similar to tail -f command.')
@click.option('--debug', is_flag=True, default=False)
@click.pass_context
def cli(ctx, conf, debug):
    """ngxctl: A command-line tool for managing and analyzing Nginx."""

    # ensure that ctx.obj exists and is a dict (in case `cli()` is called
    # by means other than the `if` block below)
    ctx.ensure_object(dict)

    ctx.obj['DEBUG'] = debug

    debug_conf = os.path.join(os.getcwd(), "samples", "nginx.debug.conf")
    if debug and os.path.exists(debug_conf):
        conf = debug_conf

    # payload 对象
    if not os.path.exists(conf):
        raise FileNotFoundError(f"{conf} does not exist")

    if conf.endswith(".json"):
        payload = json.load(open(conf, 'r', encoding="utf-8"))
    else:
        payload = crossplane.parse(conf)

    ctx.obj['payload'] = payload

    # 提取log_path & log format & 放到ctx之中
    log_path_results = config_parser.load_and_extract_log_paths(ngx_cfg_json_dict=payload, debug=debug)
    log_format_results = config_parser.load_and_extract_log_formats(ngx_cfg_json_dict=payload)
    ctx.obj['log_path_results'] = log_path_results
    ctx.obj['log_format_results'] = log_format_results

    # if show_vars:
    #     variables = config_parser.get_log_format_used_fields(log_path_results, log_format_results)
    #     table_data = [[item] for item in variables]
    #     print(tabulate.tabulate(table_data, headers=['Variables'], tablefmt='orgtbl'))
    #     ctx.exit()  # 退出程序
    #
    # if show_logs:
    #     table_data = []
    #     headers = ['server_name', 'file_name', 'log_path']
    #     for item in log_path_results:
    #         if item['log_type'] == 'access_log':
    #             row = []
    #             for header in headers:
    #                 if header == 'log_path':
    #                     row.append(
    #                         item.get('log_args')[0]
    #                     )
    #                 else:
    #                     row.append(
    #                         item.get(header, '')
    #                     )
    #             table_data.append(row)
    #     print(tabulate.tabulate(table_data, headers=headers, tablefmt='orgtbl'))
    #     ctx.exit()  # 退出程序


# 默认回调函数，目前没啥用
# @cli.result_callback()
# @click.pass_context
# def process_result(ctx, result, **kwargs):
#     if ctx.invoked_subcommand is None:
#         # 没有提供子命令时的默认行为
#         if ctx.obj['DEBUG']:
#             print("Debug mode is on.")
#         else:
#             print("No subcommand provided. Use --help to see available commands.")


# Add subcommands to the cli group
cli.add_command(top.top)
cli.add_command(misc.vars)
cli.add_command(misc.files)

# extract的功能暂时还没想清楚怎么使用，先暂停
# cli.add_command(extract.extract)

if __name__ == "__main__":
    cli()