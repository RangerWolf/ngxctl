import sqlite3
import time
import threading
import os
import re
from queue import Queue


class NginxLogFileWatcher(threading.Thread):
    def __init__(self, log_path, callback_function=None, callback_queue=None, follow=True):
        super().__init__()
        self.log_path = log_path
        self.callback_function = callback_function
        self.callback_queue = callback_queue
        self.stopped = threading.Event()
        self.follow = follow
        # self.log_pattern = log_pattern
        # self.server_name = server_name
        # self.sql_processor = sql_processor

    def run(self):
        with open(self.log_path, 'r') as file:
            if self.follow:
                file.seek(0, 2)  # 移动到文件末尾
                while not self.stopped.is_set():
                    where = file.tell()
                    line = file.readline()
                    if not line:
                        file.seek(where)
                        time.sleep(0.1)  # 没有新内容时稍作等待
                    else:
                        self.callback_function(self.log_path, self.callback_queue, line)
            else:
                while True:
                    line = file.readline()
                    if not line:
                        break
                    self.callback_function(self.log_path, self.callback_queue, line)

    def stop(self):
        self.stopped.set()


def monitor_files(file_paths, callback_function, data_queue=None, follow=True):
    watchers = [NginxLogFileWatcher(path, callback_function, data_queue, follow) for path in file_paths]
    for watcher in watchers:
        watcher.daemon = follow           # 必须要设置成True，否则主线程就会需要等子线程完成了才能退出
        watcher.start()

    # try:
    #     while True:
    #         time.sleep(1)  # 主线程也休眠，防止CPU占用过高
    # except KeyboardInterrupt:
    #     for watcher in watchers:
    #         watcher.stop()
    #     for watcher in watchers:
    #         watcher.join()


def handle_output(log_path, data_queue, line):
    print(f"!!!!log_path={log_path}; line={line}")
    # if line and line.strip():
    #     # print(f"callback:[{log_path}] {line}")
    #     data = {
    #         "log_path": log_path,
    #         "line": line,
    #     }
    #     data_queue.put(data)
    # else:
    #     print(f"callback:[{log_path}]  empty line....")


    # if log_pattern:
    #     m = log_pattern.match(line)
    #     if m:
    #         data = m.groupdict()
    #         insert_value = {
    #             "remote_addr": data.get('remote_addr', "-"),
    #             "status_2xx":  1 if data.get('status').startswith('2') else 0,
    #             "status_3xx": 1 if data.get('status').startswith('3') else 0,
    #             "status_4xx": 1 if data.get('status').startswith('4') else 0,
    #             "status_5xx": 1 if data.get('status').startswith('5') else 0,
    #             "body_bytes_sent": 0 if data.get('body_bytes_sent') and data.get('body_bytes_sent').isdigit() else 0,
    #             "http_user_agent": data.get('http_user_agent'),
    #             "log_path": log_path,
    #             "server_name": server_name
    #         }
    #
    #         sql_processor.process([insert_value])
    #
    #     print(sql_processor.report())
    #         print(f"!!!! [{file_path}] dict={data}", end='')
    #         # return data
    #     else:
    #         print(f"@@@@ [{file_path}] line={line}", end='')
    # else:
    #     print(f"#### [{file_path}] line={line}", end='')
    # # return line

def process_data(data_queue):
    """
    主线程中的函数，从队列中获取数据并处理。
    """
    while True:
        data = data_queue.get()  # 从队列中获取数据
        if data is None:
            break
        print(f"!!!!!!!!!!!!!!!!!!!Processing data: {data}")

        # 数据处理逻辑
        # ...

        data_queue.task_done()


def main():
    file_paths = """
    /www/wwwlogs/joy.acsmilelive.com.log
    /www/wwwlogs/www.acsmilelive.com.log
    /www/wwwlogs/www.wuwugames.com.log
    /www/wwwlogs/www.wuwugames.com.log 
    /www/wwwlogs/game.acsmilelive.com.log
    /www/wwwlogs/online.picigames.com.log
    /www/wwwlogs/www.freecolorgames.com.log
    /www/wwwlogs/www.funkernel.com.log
    /www/wwwlogs/www.baloogames.com.log
    /www/wwwlogs/www.baloogames.com.log 
    /www/wwwlogs/www.funnybabyworld.com.log
    /www/wwwlogs/kids.acsmilelive.com.log
    /www/wwwlogs/games.kittenquiz.com.log
    /www/wwwlogs/fun.nurserybuddies.com.log
    /www/wwwlogs/www.playdklily.com.log
    
    /var/log/nginx/www.flyml.net.log
    /var/log/nginx/www.flyml.net-extended.log
    """
    file_paths = file_paths.splitlines()
    file_paths = [x.strip() for x in file_paths if os.path.exists(x.strip())]

    for path in file_paths:
        print(path)

    # log_format = '$remote_addr - $remote_user [$time_local] ' \
    #               '"$request" $status $body_bytes_sent ' \
    #               '"$http_referer" "$http_user_agent"'
    # regex = ''.join(
    #     '(?P<' + g + '>.*?)' if g else re.escape(c)
    #     for g, c in re.findall(r'\$(\w+)|(.)', log_format))
    # log_pattern = re.compile(regex)

    data_queue = Queue()

    monitor_files(file_paths, handle_output, data_queue=data_queue, follow=False)

    # 主线程处理数据
    process_data(data_queue)

    # 等待所有任务完成
    data_queue.join()


if __name__ == '__main__':
    main()