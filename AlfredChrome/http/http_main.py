# coding=utf-8
import SocketServer
import atexit
import os
import io
import json
import psutil

from custom_handler import CustomHttpHandler

STATE_FILE_PATH = os.getcwd() + "/running_state"


def read_state_file():
    if not os.path.isfile(STATE_FILE_PATH):
        return None
    with io.open(STATE_FILE_PATH, "r") as f:
        content = f.read()
        keys = json.loads(content)
        return keys


def shutdown(httpd):
    httpd.shutdown()


# 是否有旧进程正在运行
def check_old_process():
    keys = read_state_file()
    if keys is None:
        return False
    state = keys.get("STATE", None)
    if state is not None and state == u"OPEN":
        pid = keys["PID"]

    return True


def write_process_state():
    infos = {"STATE": u"OPEN", "PID": os.getpid()}
    with io.open(STATE_FILE_PATH, "w") as f:
        f.write(json.dumps(infos).decode("utf-8"))


def start_server():
    # if not check_old_process():
    #     print(u'旧的http服务正在运行')
    #     return
    server_host = '127.0.0.1'
    server_port = 8080
    httpd = SocketServer.TCPServer((server_host, server_port), CustomHttpHandler)
    atexit.register(shutdown, httpd)
    print(u'http服务启动' + str(server_host) + u'端口:' + str(server_port))
    write_process_state()
    httpd.serve_forever()


if __name__ == "__main__":
    start_server()
