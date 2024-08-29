import threading
import time
import os
from queue import Queue, Empty  # 从 queue 模块导入 Empty 异常


def read_file(file_path, follow=False, queue=None):
    """
    读取文件的内容并将其放入队列中。
    如果 follow=True, 则像 tail -f 一样持续监控文件更新。
    否则，就像 cat 一样只读取一次文件内容。
    """
    try:
        with open(file_path, 'r') as file:
            # 移动到文件末尾
            if follow:
                file.seek(0, os.SEEK_END)
                while True:
                    where = file.tell()
                    line = file.readline()
                    if not line:
                        # 如果没有新行并且是 follow 模式，则等待一会儿再尝试读取
                        time.sleep(1)
                        file.seek(where)
                    else:
                        # 将文件名和行内容放入队列
                        queue.put({"file_path": file_path, "line": line})
            else:
                lines = file.readlines()
                for line in lines:
                    # 将文件名和行内容放入队列
                    queue.put({"file_path": file_path, "line": line})
    except FileNotFoundError:
        print(f"File not found: {file_path}")


def main():
    files = ['/var/log/nginx/www.flyml.net-extended.log']  # 文件列表
    queue = Queue()  # 创建一个队列用于传递数据

    # 创建读取文件的线程
    threads = []
    for file in files:
        file = file.strip()
        print(f"!!!!! file: {file} exists: {os.path.exists(file)}")
        thread = threading.Thread(target=read_file, args=(file, True, queue))  # 设置 follow=True
        threads.append(thread)
        thread.start()

    # 主线程中消费队列的内容
    while True:
        try:
            # 使用 timeout 参数来避免阻塞主线程
            item = queue.get(timeout=1)  # 超时时间为1秒
            print(item)
            queue.task_done()
        except Empty:
            pass  # 如果队列为空，跳过本次循环

        # 检查所有线程是否都已经完成
        all_threads_finished = all(t.is_alive() is False for t in threads)
        if all_threads_finished and queue.empty():
            break

    # 确保所有任务都被处理完毕
    queue.join()


if __name__ == "__main__":
    main()