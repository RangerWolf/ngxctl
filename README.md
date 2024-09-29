# ngxctl - Real-time Metrics for Nginx Server

## Project Overview
1. Rebuilt based on the [ngxtop](https://github.com/lebinh/ngxtop) project and adapted for actual usage scenarios.
2. The core principle remains the same: parsing log contents and storing them in SQLite, displaying top statistics in real-time using GROUP BY. As such, it is not suitable for long-term operation.

## Installation
```shell
# Install from PyPI
pip install ngxctl

# Install from Tencent Cloud source
pip install ngxctl --index-url https://mirrors.cloud.tencent.com/pypi/simple --trusted-host mirrors.cloud.tencent.com

```


## Usage
### Display Configured Log Files
```shell
# cmd
ngxctl files

# output example
| server_name         | file_name                                       | log_path                                  |
|---------------------+-------------------------------------------------+-------------------------------------------|
| www.test1.net...    | /etc/nginx/sites-enabled/www.test1.net.conf     | /var/log/nginx/www.test1.net-extended.log |

```


### Display Variables Used in Access Logs
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


### Display Top Statistics
#### Basic Command

```shell
# cmd (output omitted)
running for 7 seconds, 0 records processed

ServerName Top Stat
| server_name   | count   | 2xx   | 3xx   | 4xx   | 5xx   | avg_bytes_sent   | sum_bytes_sent   | start_time   | end_time   | req/s   |
|---------------+---------+-------+-------+-------+-------+------------------+------------------+--------------+------------+---------|

| Detailed content is omitted here |

```


#### Supported Parameters
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
                          remote_addr==1.2.3.4.
  -n, --limit INTEGER     Limit to top lines.
  --follow / --no-follow  Read the entire log file at once instead of
                          following new lines.
  -h, --help              Show this message and exit.



```


### Running from source
```shell
python -m ngxctl.cli
```