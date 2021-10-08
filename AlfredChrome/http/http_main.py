# coding=utf-8
import atexit
import os
import io
import json
import fcntl
import psutil

from http_server import PluginHttpServer, ServerListener
from custom_handler import CustomHttpHandler

STATE_FILE_PATH = os.getcwd() + "/running_state"


def read_state_file():
    if not os.path.isfile(STATE_FILE_PATH):
        return None
    with io.open(STATE_FILE_PATH, "r") as f:
        content = f.read()
        if content.strip() == "":
            return None
        keys = json.loads(content)
        return keys


def shutdown(httpd):
    httpd.shutdown()


# 是否有旧进程正在运行
# 返回值 true 表示服务处于打开状态，false表示服务没有打开
def check_old_process():
    keys = read_state_file()
    if keys is None:
        return False
    state = keys.get("STATE", None)
    if state is not None and state == u"OPEN":
        pid = keys["PID"]
        # 如果进程不存在了 直接返回 False
        if not psutil.pid_exists(pid):
            return False
        old_process = psutil.Process(pid)
        # 检查进程的执行脚本是否是当前脚本
        cmd_lines = old_process.cmdline()
        for line in cmd_lines:
            if line.find("http_main.py") != -1:
                return True
        return False
    else:
        return False


# 服务监听器
class ServerStateFileWriteListener(ServerListener):

    def __init__(self, state_file):
        self.state_file = state_file

    def on_active(self, server):
        if self.state_file is not None:
            self.state_file.seek(0, 0)
            infos = {"STATE": u"OPEN", "PID": os.getpid()}
            self.state_file.write(json.dumps(infos).decode("utf-8"))
            self.state_file.flush()
        print("ServerStateFileWriteListener====on_active")
        # http 服务启动&状态文件写入后，需要解锁文件锁
        fcntl.flock(self.state_file.fileno(), fcntl.LOCK_UN)

    def before_shutdown(self, server):
        if self.state_file is not None:
            self.state_file.seek(0, 0)
            infos = {"STATE": u"CLOSE", "PID": os.getpid()}
            self.state_file.write(json.dumps(infos).decode("utf-8"))
            self.state_file.flush()


def start_server():
    state_file = open(STATE_FILE_PATH, "w")
    # 加文件独占锁，防止并发启动
    fcntl.flock(state_file.fileno(), fcntl.LOCK_EX)
    if check_old_process():
        print(u'旧的http服务正在运行')
        return
    server_host = '127.0.0.1'
    server_port = 8080
    httpd = PluginHttpServer((server_host, server_port), CustomHttpHandler, ServerStateFileWriteListener(state_file))
    atexit.register(shutdown, httpd)
    httpd.serve_forever()


if __name__ == "__main__":
    start_server()
