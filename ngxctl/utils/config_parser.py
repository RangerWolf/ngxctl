import json
import os.path
import time
import copy as cp

from jsonpath_ng.ext import parse


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


def load_and_extract_log_paths(ngx_cfg_json_path=None, ngx_cfg_json_dict=None):
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


if __name__ == '__main__':
    json_path = "../samples/nginx.baloo.json"
    result = load_and_extract_log_formats(json_path)
    print(result)

    result = load_and_extract_log_paths(json_path)
    print(result)