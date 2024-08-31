import re

def extract_variables(log_format):
    # 正则表达式匹配以$开头的变量
    pattern = r'\$(\w+)'
    # 使用findall方法找到所有匹配项
    variables = re.findall(pattern, log_format)
    return variables

# 示例使用
log_format = "$remote_addr - $remote_user [$time_local] \"$request\" $status $body_bytes_sent \"$http_referer\" \"$http_user_agent\" $request_id"
variables = extract_variables(log_format)

print(variables)