from ngxctl.utils import file_watcher


def process_extact_log_line(line, log_path, log_path_results, log_pattern_dict):
    """
    功能1：内容展示 + 条件过滤
    功能2：convert format
    功能3：输入到out指定位置，通过append的方式输出内容
    :param line:
    :param log_path:
    :param log_path_results:
    :param log_pattern_dict:
    :return:
    """
    # 先实现最基础的功能：原始展示
    print(
        "line:", line, "\n",
        "path:", log_path
    )
    pass


def monitor_logs(log_path_results, log_pattern_dict, follow=True):
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

    file_watcher.watch_logs(log_paths, process_extact_log_line, follow,
                            log_path_results, log_pattern_dict)