# ngxctl/cmds/top.py

import json
import os.path
from queue import Queue

import click


from ngxctl.utils import top_stat, config_parser, sqlite_utils
from ngxctl.utils.misc_utils import display_report

@click.command()
@click.option('-g', '--group-by', default=top_stat.DEFAULT_GROUP_BY_FIELDS,
              help='Group the results by the specified fields, e.g., server_name,remote_addr, etc.')
@click.option('-o', '--order-by', default=top_stat.DEFAULT_ORDER_BY_FIELDS,
              help='Order the results by a specified criteria, e.g., avg(bytes_sent) * count.')
@click.option('--where', default=top_stat.DEFAULT_WHERE_CONDITIONS,
              help='Apply a filter to the raw log data before stat, e.g., status==404.')
@click.option('--having', default=top_stat.DEFAULT_HAVING_CONDITIONS,
              help='Apply a filter to stat result, e.g., remote_addr==1.2.3.4')
@click.option('-n', '--limit', default=top_stat.DEFAULT_LIMIT_NUMBER,
              help='Limit to top lines')
@click.option('--follow/--no-follow', default=True,
              help='Read the entire log file at once instead of following new lines.')
@click.pass_context
def top(ctx, group_by, order_by, where, having, limit, follow):
    """
    Analyze and display top Nginx log statistics.

    Examples:

    ngxctl top

    ngxctl top --conf /etc/nginx/nginx.conf

    ngxctl top --group-by remote_addr,http_user_agent

    ngxctl top -w 'status==404' --no-follow

    \f

    :param ctx:
    :param group_by:
    :param order_by:
    :param where:
    :param having:
    :param limit:
    :param follow:
    :return:
    """
    # 构建SQL processor 对象
    # TBD: 需要补充一个Top Error Request Stat
    queries = list()
    sql = top_stat.build_query(
        where, group_by, having, order_by, limit
    )

    if group_by == top_stat.DEFAULT_GROUP_BY_FIELDS:
        queries.append((
            top_stat.DEFAULT_QUERY_NAME, sql
        ))
    else:
        queries.append(sql)


    # step: 从ctx之中读取log_path_results & log_format_results
    log_path_results = ctx.obj['log_path_results']
    log_format_results = ctx.obj['log_format_results']

    # 根据log_format提取pattern
    log_pattern_dict = config_parser.build_pattern_dict(log_format_results)
    # 根据log format提取所有用到的field，比如http_user_agent

    # log_format_fields 感觉应该复用config_parser里面的函数，跟get_log_format_known_fields应该是重复的
    # log_format_fields = top_stat.get_log_format_known_fields(log_format_results)
    log_format_fields = config_parser.get_log_format_used_fields(log_path_results, log_format_results)

    query_str = [
        where, group_by, having, order_by
    ]

    extend_fields = top_stat.detect_extend_fields(cli_params=query_str, known_columns=log_format_fields)

    final_fields = set(top_stat.TARGET_FIELDS)
    final_fields.update(extend_fields)
    final_fields = list(final_fields)

    processor = sqlite_utils.SQLProcessor(
        report_queries=queries,
        fields=final_fields
    )

    if follow:
        display_report(processor)

    # 通过队列在多线程之间传输数据
    top_stat.monitor_logs(
        processor, log_path_results, log_pattern_dict, follow
    )

    if not follow:
        output = processor.report()
        print(output)


if __name__ == "__main__":
    top()
