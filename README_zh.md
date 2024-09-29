# `ngxctl` - real-time metrics for nginx server

## 项目介绍
1. 参考ngxtop这个项目，重新构建，并根据实际情况进行了改造
2. 基本原理还是把log内容解析并存入sqlite，实时进行group by 显示top的内容。因此不宜长时间运行

## 安装
```shell
# install from pypi
pip install ngxtop


# install from tencent cloud source
pip install ngxtop --index-url https://mirrors.cloud.tencent.com/pypi/simple --trusted-host mirrors.cloud.tencent.com
```

## 运行

### 显示当前配置了哪些log
| server_name         | file_name                                         | log_path                                  |
|---------------------+---------------------------------------------------+-------------------------------------------|
| www.test1.net...    | /etc/nginx/sites-enabled/www.test1.net.conf       | /var/log/nginx/www.test1.net-extended.log |


### 显示access log一共使用了哪些变量
```shell
# cmd
ngxctl vars


# output
| Variables       |
|-----------------|
| http_referer    |
| status          |
| http_user_agent |
| body_bytes_sent |
| request         |
| time_local      |
| remote_addr     |
| remote_user     |
| request_id      |
```

### 显示Top统计
#### 基本命令
```shell
# cmd (内容略)
running for 7 seconds, 0 records processed

ServerName Top Stat
| server_name   | count   | 2xx   | 3xx   | 4xx   | 5xx   | avg_bytes_sent   | sum_bytes_sent   | start_time   | end_time   | req/s   |
|---------------+---------+-------+-------+-------+-------+------------------+------------------+--------------+------------+---------|

| detai content is ommited here |
```

#### 支持的参数
```shell
Usage: ngxctl top [OPTIONS]

  Analyze and display top Nginx log statistics.

  Examples:

  ngxctl top

  ngxctl top --conf /etc/nginx/nginx.conf

  ngxctl top --group-by remote_addr,http_user_agent

  ngxctl top -w 'status==404' --no-follow

Options:
  -g, --group-by TEXT     Group the results by the specified fields, e.g.,
                          server_name,remote_addr, etc.
  -o, --order-by TEXT     Order the results by a specified criteria, e.g.,
                          avg(bytes_sent) * count.
  --where TEXT            Apply a filter to the raw log data before stat,
                          e.g., status==404.
  --having TEXT           Apply a filter to stat result, e.g.,
                          remote_addr==1.2.3.4
  -n, --limit INTEGER     Limit to top lines
  --follow / --no-follow  Read the entire log file at once instead of
                          following new lines.
  -h, --help              Show this message and exit.



```

### run from source

```shell
python -m ngxctl.cli
```