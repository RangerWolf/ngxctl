import datetime

def convert_nginx_time_str_to_timestamp(nginx_time_str, include_timezone=False):
    """
    将 Nginx 的时间字符串转换为 datetime 对象。
    :param nginx_time_str: Nginx 时间字符串，例如 '27/Sep/2024:17:54:00 +0800'
    :param include_timezone: 是否包含时区信息
    :return: datetime 对象
    """
    ptn_with_tz = '%d/%b/%Y:%H:%M:%S %z'
    ptn_no_tz = '%d/%b/%Y:%H:%M:%S'

    if include_timezone:
        return datetime.datetime.strptime(nginx_time_str, ptn_with_tz)
    else:
        return datetime.datetime.strptime(nginx_time_str, ptn_no_tz)


def calc_nginx_time_diff(start_time, end_time, include_timezone=False):
    """
    计算两个 Nginx 时间字符串之间的时间差（以秒为单位）。
    :param start_time: 开始时间的 Nginx 时间字符串
    :param end_time: 结束时间的 Nginx 时间字符串
    :param include_timezone: 是否包含时区信息
    :return: 时间差（秒）
    """
    # 转换时间字符串为 datetime 对象
    start_dt = convert_nginx_time_str_to_timestamp(start_time, include_timezone)
    end_dt = convert_nginx_time_str_to_timestamp(end_time, include_timezone)

    # 计算时间差
    time_diff = end_dt - start_dt

    # 将时间差转换为秒
    time_diff_seconds = int(time_diff.total_seconds())

    return time_diff_seconds

# 示例调用

if __name__ == '__main__':
    _start_time = '27/Sep/2024:00:01:46 +0800'
    _end_time = '27/Sep/2024:00:18:28 +0800'

    _start_time = '27/Sep/2024:00:01:46'
    _end_time = '27/Sep/2024:18:39:39'
    time_diff_in_seconds = calc_nginx_time_diff(_start_time, _end_time, include_timezone=False)
    print(f'Time difference in seconds: {time_diff_in_seconds}')