from tabulate import tabulate

# 定义列表
data = ['time_local', 'body_bytes_sent', 'status', 'remote_user', 'request_id', 'remote_addr', 'http_user_agent', 'http_referer', 'request']

# 将单行列表转换为表格形式的数据
table_data = [[item] for item in data]

# 定义表头
headers = ["variables"]

# 使用tabulate打印表格
print(tabulate(table_data, headers, tablefmt="grid"))