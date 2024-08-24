# ngxctl/top.py
import json
from queue import Queue

import click
import crossplane

from ngxctl.utils import top_stat, log_info_extractor, sqlite_utils
from ngxctl.utils.misc_utils import display_report


@click.command(help="""\
Analyze and display top Nginx log statistics.

Examples:

  ngxtools top --conf /etc/nginx/nginx.conf --group-by remote_addr,http_user_agent
  ngxtools top --order-by "avg(bytes_sent) * count" --filter 'status==404'
  ngxtools top --no-follow
""")
@click.option('--conf', default='/etc/nginx/nginx.conf',
              help='Specify the Nginx configuration file. Default is /etc/nginx/nginx.conf.')
@click.option('--group-by', default=top_stat.DEFAULT_GROUP_BY_FIELDS,
              help='Group the results by the specified fields, e.g., server_name,remote_addr, etc.')
@click.option('--order-by', default=top_stat.DEFAULT_ORDER_BY_FIELDS,
              help='Order the results by a specified criteria, e.g., avg(bytes_sent) * count.')
@click.option('--where', default=top_stat.DEFAULT_WHERE_CONDITIONS,
              help='Apply a filter to the raw log data before status, e.g., status==404.')
@click.option('--having', default=top_stat.DEFAULT_HAVING_CONDITIONS,
              help='Apply a filter to stat result, e.g., remote_addr==1.2.3.4')
@click.option('--limit', default=top_stat.DEFAULT_LIMIT_NUMBER,
              help='Limit to top lines')
@click.option('--follow/--no-follow', default=True,
              help='Read the entire log file at once instead of following new lines.')
def top(conf, group_by, order_by, where, having, limit, follow):
    """
    :param conf:
    :param group_by:
    :param order_by:
    :param where:
    :param having:
    :param limit:
    :param follow:
    :return:
    """
    # step: 先尝试解析conf
    if conf.endswith(".json"):
        payload = json.load(open(conf, 'r', encoding="utf-8"))
    else:
        payload = crossplane.parse(conf)

    # 构建SQL processor 对象
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

    # TBD: 需要补充一个Top Error Request Stat

    # step: 提取log_path & log format
    log_path_results = log_info_extractor.load_and_extract_log_paths(ngx_cfg_json_dict=payload)
    log_format_results = log_info_extractor.load_and_extract_log_formats(ngx_cfg_json_dict=payload)
    # 根据log_format提取pattern
    # import pdb; pdb.set_trace()
    log_pattern_dict = top_stat.build_pattern_dict(log_format_results)
    # 根据log format提取所有用到的field，比如http_user_agent
    log_format_fields = top_stat.get_log_format_fields(log_format_results)

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

    display_report(processor)

    # 通过队列在多线程之间传输数据
    data_queue = Queue()

    top_stat.monitor_logs(
        data_queue=data_queue,
        log_path_results=log_path_results,
        follow=follow
    )
    top_stat.process_log_data(
        data_queue=data_queue,
        log_path_results=log_path_results,
        log_pattern_dict=log_pattern_dict,
        sql_processor=processor
    )
    data_queue.join()


if __name__ == "__main__":
    top()
