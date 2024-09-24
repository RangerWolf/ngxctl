import json
import os.path
import re
import time
import copy as cp

from jsonpath_ng.ext import parse

from ngxctl.utils.top_stat import LOG_FORMAT_COMBINED, LOG_FORMAT_ERROR


REGEX_SPECIAL_CHARS = r'([\.\*\+\?\|\(\)\{\}\[\]])'
REGEX_LOG_FORMAT_VARIABLE = r'\$([a-zA-Z0-9\_]+)'

def get_log_format_used_fields(log_path_results, log_format_results):
    """
    log_path_results
    [
        {
        "file_name": "/etc/nginx/sites-enabled/blog.flyml.net.conf",
        "log_type": "access_log",
        "log_args": [
          "/var/log/nginx/blog.flyml.net.log"
        ],
        "server_name": "blog.flyml.net"
      }
    ]

    log_format_results
    {
      "extended": "$remote_addr - $remote_user [$time_local] \"$request\" $status $body_bytes_sent \"$http_referer\" \"$http_user_agent\" $request_id"
    }


    :param log_path_results:
    :param log_format_results:
    :return:
    """
    # get all used log_formats
    used_formats = []
    for item in log_path_results:
        if item['log_type'] == 'access_log':
            log_args = item['log_args']
            if len(log_args) == 1:
                used_formats.append('combined')
            else:
                used_formats.append(''.join(log_args[1:]))

    used_formats = list(set(used_formats))

    def __extract_variables(log_format):
        # 正则表达式匹配以$开头的变量
        pattern = r'\$(\w+)'
        # 使用findall方法找到所有匹配项
        variables = re.findall(pattern, log_format)
        return variables

    # 逐步format遍历，取出用到的变量
    used_variables = []
    for f in used_formats:
        if f == 'combined':
            used_variables.extend(__extract_variables(LOG_FORMAT_COMBINED))
        elif f == 'error':
            used_variables.extend(__extract_variables(LOG_FORMAT_ERROR))
        else:
            # custom log format
            log_format = log_format_results.get(f)
            if log_format:
                used_variables.extend(__extract_variables(log_format))
            else:
                raise Exception(f"Log format[{f}] not found!")

    used_variables = list(set(used_variables))
    sorted(used_variables)

    return used_variables


def load_and_extract_log_formats(ngx_cfg_json_path=None, ngx_cfg_json_dict=None):
    if not ngx_cfg_json_dict and not ngx_cfg_json_path:
        raise Exception("Empty data and data File")

    if ngx_cfg_json_path and os.path.exists(ngx_cfg_json_path):
        payload = json.load(open(ngx_cfg_json_path))
    else:
        payload = cp.deepcopy(ngx_cfg_json_dict)

    status = payload['status']
    if status != "ok":
        raise Exception("Parse failed!")

    jsonpath_expression = parse(f'$..*[?directive="log_format"]')

    log_format_results = {}

    for match in jsonpath_expression.find(payload):
        args = match.value['args']
        name = args[0]
        # if name == "extended":
        #     print("!!! extended!!!!")
        #     import pdb; pdb.set_trace()
        value = ''.join(args[1:])
        log_format_results[name] = value
        # print("!!!!format name=", name, "value=", value)

    return log_format_results


def load_and_extract_log_paths(ngx_cfg_json_path=None, ngx_cfg_json_dict=None, debug=False):
    if not ngx_cfg_json_dict and not ngx_cfg_json_path:
        raise Exception("Empty data and data File")

    if ngx_cfg_json_path and os.path.exists(ngx_cfg_json_path):
        payload = json.load(open(ngx_cfg_json_path))
    else:
        payload = cp.deepcopy(ngx_cfg_json_dict)

    status = payload['status']
    if status != "ok":
        raise Exception("Parse failed!")

    config_objs = payload['config']

    # 解析sites-enabled / sites-available / conf.d 里面的配置
    target_prefixes = [
        "/etc/nginx/sites-enabled",
        "/etc/nginx/sites-available",
        "/etc/nginx/conf.d",
    ]

    if debug:
        # 当前工作目录
        target_prefixes.append(os.getcwd())

    log_path_results = []

    # 使用json path 解析出各种参数
    for item in config_objs:
        file = item['file']

        if any(file.startswith(prefix) for prefix in target_prefixes):
            file_parse_status = item['status']

            if file_parse_status == "ok":
                # print("---- file:", file)
                # t0 = time.time()

                # 先查找server_name
                server_name = "server-name-not-found"
                jsonpath_expression = parse(f'$..block[?directive="server_name"]')
                for match in jsonpath_expression.find(item):
                    args = match.value['args']
                    if len(args) == 1:  #  只有1个server name
                        server_name = args[0]
                    else:  # 不止一个
                        server_name = args[0] + "..."

                # t1 = time.time()

                # 使用json path 找出所有的access_log / error_log
                names = ["access_log", "error_log"]
                for name in names:
                    jsonpath_expression = parse(f'$..block[?directive="{name}"]')
                    for match in jsonpath_expression.find(item):

                        log_args = match.value['args']
                        if len(log_args) == 1 and log_args[0].lower() in ("off", "/dev/null"):
                            continue

                        log_path_results.append(
                            {
                                "file_name": file,
                                "log_type": name,
                                "log_args": match.value['args'],
                                "server_name": server_name
                            }
                        )
                # t2 = time.time()

                # print("cost time: t1-t0:", (t1 - t0))
                # print("cost time: t2-t1:", (t2 - t1))
    return log_path_results


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


if __name__ == '__main__':
    json_path = "../samples/nginx.baloo.json"
    result = load_and_extract_log_formats(json_path)
    print(result)

    result = load_and_extract_log_paths(json_path)
    print(result)