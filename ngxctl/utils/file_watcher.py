# ngxctl/utils/file_watcher.py

import threading
import queue
import time
import os
import signal
import sys

# 全局标志，用于通知所有线程退出
stop_event = threading.Event()


def follow_file(file_path, data_queue):
    """Follow a file and put new lines into the queue."""
    with open(file_path, 'r') as file:
        # Move to the end of the file
        file.seek(0, os.SEEK_END)

        while not stop_event.is_set():
            line = file.readline()
            if not line:
                time.sleep(0.1)  # Sleep briefly to avoid busy waiting
                continue
            data_queue.put({'line': line.strip(), 'log_path': file_path})


def start_watchers(log_paths, data_queue):
    """Start a watcher for each log path."""
    threads = []

    for log_path in log_paths:
        thread = threading.Thread(target=follow_file, args=(log_path, data_queue))
        thread.daemon = True  # Set as daemon so it will exit when the main program exits
        thread.start()
        threads.append(thread)

    return threads


def process_log_line(line, log_path, *args, **kwargs):
    """Process a single log line. This function should be overridden by the caller."""
    print(f"Processing: {line} from {log_path}")
    # Implement your specific processing logic here
    pass


def watch_logs(log_paths, process_function, follow=True, *args, **kwargs):
    """Watch multiple log files and process each line using the provided function."""
    data_queue = queue.Queue()
    threads = []

    if follow:
        # Start watchers in separate threads
        threads = start_watchers(log_paths, data_queue)

        try:
            while not stop_event.is_set():
                try:
                    data = data_queue.get(timeout=1)  # 使用超时避免阻塞
                    if data is None:
                        break
                    line = data.get('line')
                    log_path = data.get('log_path')
                    if line and log_path:
                        process_function(line, log_path, *args, **kwargs)
                except queue.Empty:
                    continue
        except KeyboardInterrupt:
            print("Stopping log watchers...")
            stop_event.set()  # 设置停止标志
        finally:
            # 等待所有线程退出
            for thread in threads:
                thread.join()
            print("All log watchers stopped.")
    else:
        # 一次性读取并处理所有日志文件
        for log_path in log_paths:
            with open(log_path, 'r') as file:
                for line in file:
                    process_function(line.strip(), log_path, *args, **kwargs)


# 捕获 SIGINT 信号
def signal_handler(sig, frame):
    print("Stopping log watchers...")
    stop_event.set()  # 设置停止标志
    sys.exit(0)


# 设置信号处理器
signal.signal(signal.SIGINT, signal_handler)