# coding=utf-8
import atexit
import commands
import os
import json
import fcntl
import sys
import time

sys.path.append("./site-packages")
sys.path.append(os.getcwd() + "/site-packages")
print os.getcwd() + "/site-packages"
from http_server import PluginHttpServer, ServerListener
from custom_handler import CustomHttpHandler

STATE_FILE_DIR_PATH = os.path.expanduser("~") + "/logs/alfred_chrome_plugin"
STATE_FILE_PATH = STATE_FILE_DIR_PATH + "/running_state"

PORT = 9567

def read_state_file(state_file):
    if not state_file:
        return None
    content = state_file.read()
    if content.strip() == "":
        return None
    keys = json.loads(content)
    return keys


def shutdown(httpd):
    httpd.shutdown()


def make_dir_exist():
    if os.path.exists(STATE_FILE_DIR_PATH):
        return
    os.makedirs(STATE_FILE_DIR_PATH)


# 是否有旧进程正在运行
# 返回值 true 表示服务处于打开状态，false表示服务没有打开
def check_old_process(state_file):
    keys = read_state_file(state_file)
    if keys is None:
        return False
    state = keys.get("STATE", None)
    if state is not None and state == u"OPEN":
        pid = keys["PID"]
        if not check_pid(pid):
            return False
        else:
            return True
    else:
        return False


def check_pid(pid):
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True


def kill_old_process():
    out = commands.getstatusoutput("lsof -i:" + str(PORT) + " | grep TCP | awk {'print $2'}")
    if out[0] != 0:
        return
    pid = out[1]
    os.system("kill -15 " + pid)
    # 睡眠一秒，以保证旧进程被杀死
    time.sleep(2)

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
    make_dir_exist()
    state_file = open(STATE_FILE_PATH, "w+")
    # 加文件独占锁，防止并发启动
    fcntl.flock(state_file.fileno(), fcntl.LOCK_EX)
    if check_old_process(state_file):
        print(u'旧的http服务正在运行')
        return
    kill_old_process()
    server_host = '127.0.0.1'
    server_port = PORT
    httpd = PluginHttpServer((server_host, server_port), CustomHttpHandler, ServerStateFileWriteListener(state_file))
    atexit.register(shutdown, httpd)
    httpd.serve_forever()


if __name__ == "__main__":
    start_server()
