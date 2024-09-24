import re
import os
import time
import copy as cp

from ngxctl.utils import file_watcher

# copied from ngxtop
LOG_FORMAT_COMBINED = '$remote_addr - $remote_user [$time_local] ' \
                      '"$request" $status $body_bytes_sent ' \
                      '"$http_referer" "$http_user_agent"'
LOG_FORMAT_COMMON   = '$remote_addr - $remote_user [$time_local] ' \
                      '"$request" $status $body_bytes_sent ' \
                      '"$http_x_forwarded_for"'

LOG_FORMAT_EXTENDED = '$remote_addr - $remote_user [$time_local] '\
                    '"$request" $status $body_bytes_sent '\
                    '"$http_referer" "$http_user_agent" $request_id'


LOG_FORMAT_ERROR    = '$time_local [$log_level] $pid#$tid: *$cid $message'


TARGET_FIELDS = [
    "server_name",
    "remote_addr",
    "host",
    "status",
    "status_2xx",
    "status_3xx",
    "status_4xx",
    "status_5xx",
    "body_bytes_sent",
    "http_user_agent",
    "log_path",
    "http_referer",
    "time_local"
]

INT_FIELDS = ["status", "body_bytes_sent"]


DEFAULT_GROUP_BY_FIELDS = "server_name"
DEFAULT_ORDER_BY_FIELDS = "count"
DEFAULT_WHERE_CONDITIONS = "1"
DEFAULT_HAVING_CONDITIONS = "1"
DEFAULT_LIMIT_NUMBER = 20
DEFAULT_QUERY_NAME = "ServerName Top Stat"

# 29/Aug/2024:00:02:38

QUERY_TEMPLATE = """
    SELECT
       {--group-by},
       COUNT(1)                 AS count,
       SUM(status_2xx)          AS '2xx',
       SUM(status_3xx)          AS '3xx',
       SUM(status_4xx)          AS '4xx',
       SUM(status_5xx)          AS '5xx',
       AVG(body_bytes_sent)     AS avg_bytes_sent,
       SUM(body_bytes_sent)     AS sum_bytes_sent,
       SUBSTR(MIN(time_local), 1, 20)          AS start_time,
       SUBSTR(MAX(time_local), 1, 20)          AS end_time
     FROM log
     WHERE {--where}
     GROUP BY {--group-by}
     HAVING {--having}
     ORDER BY {--order-by} DESC
     LIMIT {--limit}
"""


def build_query(where, group_by, having, order_by, limit):
    temp = cp.deepcopy(QUERY_TEMPLATE)
    sql = temp.format_map({
        "--where": where,
        "--group-by": group_by,
        "--having": having,
        "--order-by": order_by,
        "--limit": limit,
    })

    return sql


def detect_extend_fields(cli_params, known_columns):
    """
    :param cli_params:  命令行运行时指定的参数
    :param known_columns:  所有可能存在的列
    :return:
    """
    detect_str = cli_params
    if isinstance(cli_params, list):
        detect_str = "\n".join(cli_params)

    # 定义正则表达式模式
    pattern = r'(?i)\b(' + '|'.join(known_columns) + r')\b'

    # 使用正则表达式查找所有匹配项
    matches = re.findall(pattern, detect_str)

    # 使用集合去重
    matched_columns = set(matches)

    # 返回排序后的列名列表
    return sorted(list(matched_columns))




# def get_log_format_known_fields(log_format_results):
#     """
#     根据log_format 里面的设定，把用到的nginx的变量名都抽取出来
#     比如：
#     {
#       "log_json": "{\"@timestamp\": \"$time_local\",  \"remote_addr\": \"$remote_addr\",  \"referer\": \"$http_referer\",  \"request\": \"$request\",  \"status\": $status,  \"bytes\": $body_bytes_sent,  \"agent\": \"$http_user_agent\",  \"x_forwarded\": \"$http_x_forwarded_for\",  \"up_addr\": \"$upstream_addr\", \"up_host\": \"$upstream_http_host\", \"up_resp_time\": \"$upstream_response_time\", \"request_time\": \"$request_time\"  }"
#     }
#
#     "$time_local"\"$remote_addr"就是possible fields
#
#     :param log_format_results:
#     :return:
#     """
#     fields = set()
#
#     def extract_fields(log_format):
#         results = [g for g, c in re.findall(r'\$(\w+)|(.)', log_format) if g]
#         return results
#
#     fields.update(
#         extract_fields(LOG_FORMAT_COMBINED)
#     )
#     fields.update(
#         extract_fields(LOG_FORMAT_ERROR)
#     )
#     fields.update(
#         extract_fields(LOG_FORMAT_COMMON)
#     )
#
#     if log_format_results:
#         for name in log_format_results:
#             fields.update(
#                 extract_fields(log_format_results[name])
#             )
#
#     return list(fields)


def build_pattern_dict(log_format_results):
    """
    Sample:
    {
      "log_json": "{\"@timestamp\": \"$time_local\",  \"remote_addr\": \"$remote_addr\",  \"referer\": \"$http_referer\",  \"request\": \"$request\",  \"status\": $status,  \"bytes\": $body_bytes_sent,  \"agent\": \"$http_user_agent\",  \"x_forwarded\": \"$http_x_forwarded_for\",  \"up_addr\": \"$upstream_addr\", \"up_host\": \"$upstream_http_host\", \"up_resp_time\": \"$upstream_response_time\", \"request_time\": \"$request_time\"  }"
    }

    :param log_format_results:
    :return:
    """

    # def build_pattern(log_format):
    #     """This function should also work, copy pattern from stackoverflow, but need to add $ to the end"""
    #     regex = ''.join(
    #         '(?P<' + g + '>.*?)' if g else re.escape(c)
    #         for g, c in re.findall(r'\$(\w+)|(.)', log_format))
    #     regex += "$"
    #     return re.compile(regex)

    def build_pattern(log_format):
        """
        Build regular expression to parse given format.
        this function is copied from Ngxtop lib
        :param log_format: format string to parse
        :return: regular expression to parse given format
        """
        # if log_format == 'combined':
        #     log_format = LOG_FORMAT_COMBINED
        # elif log_format == 'common':
        #     log_format = LOG_FORMAT_COMMON
        # if log_format == "extended":
        #     log_format = LOG_FORMAT_EXTENDED
        pattern = re.sub(REGEX_SPECIAL_CHARS, r'\\\1', log_format)
        pattern = re.sub(REGEX_LOG_FORMAT_VARIABLE, '(?P<\\1>.*)', pattern)
        return re.compile(pattern)

    pattern_dict = dict()

    # 先处理access log 的默认格式
    pattern_dict['combined'] = build_pattern(LOG_FORMAT_COMBINED)

    # 处理默认的error log格式
    pattern_dict['error'] = build_pattern(LOG_FORMAT_ERROR)

    if log_format_results:
        for name in log_format_results:
            pattern_dict[name] = build_pattern(log_format_results[name])

    return pattern_dict


def read_log_file(log_path, follow=False, queue=None):
    """
    读取文件的内容并将其放入队列中。
    如果 follow=True, 则像 tail -f 一样持续监控文件更新。
    否则，就像 cat 一样只读取一次文件内容。
    """
    try:
        with open(log_path, 'r') as file:
            # 移动到文件末尾
            if follow:
                file.seek(0, os.SEEK_END)
                while True:
                    where = file.tell()
                    line = file.readline()
                    if not line:
                        # 如果没有新行并且是 follow 模式，则等待一会儿再尝试读取
                        time.sleep(1)
                        file.seek(where)
                    else:
                        # 将文件名和行内容放入队列
                        queue.put({"log_path": log_path, "line": line})
            else:
                lines = file.readlines()
                for line in lines:
                    # 将文件名和行内容放入队列
                    queue.put({"log_path": log_path, "line": line})
    except FileNotFoundError:
        print(f"Log File not found: {log_path}")


def monitor_logs(sql_processor, log_path_results, log_pattern_dict, follow=True):
    """
        {
            "server_name": "www.wuwugames.com",
            "file_name": "/etc/nginx/sites-enabled/www.wuwugames.com.conf",
            "log_type": "access_log",
            "log_args": [
              "/var/log/nginx/shushu.log",
              "log_json"
            ]
          },
          {
            "server_name": "www.wuwugames.com",
            "file_name": "/etc/nginx/sites-enabled/www.wuwugames.com.conf",
            "log_type": "error_log",
            "log_args": [
              "/www/wwwlogs/www.wuwugames.com.error.log"
            ]
          }
        :param sql_processor:
        :param log_path_results:
        :param log_pattern_dict
        :param follow
        :return:
    """

    log_paths = []

    for item in log_path_results:
        log_type = item['log_type']
        if log_type != 'access_log':
            continue
        log_path = item['log_args'][0]
        log_paths.append(log_path)

    file_watcher.watch_logs(log_paths, process_top_log_line, follow,
                            log_path_results, log_pattern_dict, sql_processor)


def process_top_log_line(line, log_path, log_path_results, log_pattern_dict, sql_processor):
    log_args = [x for x in log_path_results if x['log_args'][0] == log_path][0]['log_args']
    server_name = [x for x in log_path_results if x['log_args'][0] == log_path][0]['server_name']
    pattern = "combined" if len(log_args) == 1 else log_args[1]
    log_pattern = log_pattern_dict[pattern]
    m = log_pattern.match(line.strip())
    # if "extend" in log_path and m is None:
    #     print("!!!!")
    #     import pdb; pdb.set_trace()
    parsed_data = m.groupdict()
    if parsed_data:
        new_data = dict()

        db_columns = sql_processor.column_list.split(",")
        for field in db_columns:
            new_data[field] = parsed_data.get(field, "-")  # host / log_path 等参数默认是没有的

            if field in parsed_data and field in INT_FIELDS:  # 存在并且知道是int的参数
                body_bytes_sent = parsed_data.get(field, "0")
                new_data[field] = int(body_bytes_sent) if body_bytes_sent.isdigit() else 0

        # 先补充两个不在log line 之中的内容
        new_data['log_path'] = log_path
        new_data['server_name'] = server_name

        # 处理status code
        new_data['status_2xx'] = 1 if parsed_data.get('status', "").startswith("2") else 0
        new_data['status_3xx'] = 1 if parsed_data.get('status', "").startswith("3") else 0
        new_data['status_4xx'] = 1 if parsed_data.get('status', "").startswith("4") else 0
        new_data['status_5xx'] = 1 if parsed_data.get('status', "").startswith("5") else 0

        sql_processor.process([new_data])



# def process_log_data(data_queue, log_path_results, log_pattern_dict, sql_processor):
#     """
#     主线程中的函数，从队列中获取数据并处理。
#
#     log_path_results Sample:
#     {
#         "server_name": "www.wuwugames.com",
#         "file_name": "/etc/nginx/sites-enabled/www.wuwugames.com.conf",
#         "log_type": "access_log",
#         "log_args": [
#           "/var/log/nginx/shushu.log",
#           "log_json"
#         ]
#       },
#       {
#         "server_name": "www.wuwugames.com",
#         "file_name": "/etc/nginx/sites-enabled/www.wuwugames.com.conf",
#         "log_type": "error_log",
#         "log_args": [
#           "/www/wwwlogs/www.wuwugames.com.error.log"
#         ]
#       }
#     :param log_path_results:
#     :return:
#
#     """
#     while True:
#         data = data_queue.get()  # 从队列中获取数据
#         if data is None:
#             break
#         # print(f"!!!!!!!!!!!!!!!!!!!Processing data: {data}")
#         line = data.get('line')
#         log_path = data.get('log_path')
#         if line and log_path:
#             process_top_log_line(line, log_path, log_path_results, log_pattern_dict, sql_processor)
# #
# #         data_queue.task_done()


# def display_content(content):
#     os.system('clear' if os.name == 'posix' else 'cls')
#     # Simulate fetching dynamic data (replace with actual logic)
#     print(content)
#     # Pause for a short period before refreshing
