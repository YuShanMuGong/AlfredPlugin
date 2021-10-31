# coding=utf-8
import json
import sys
import time
import urllib2
import config
import os

from http import alfred_util

STATE_FILE_DIR_PATH = os.path.expanduser("~") + "/logs/alfred_chrome_plugin"
STATE_FILE_PATH = STATE_FILE_DIR_PATH + "/running_state"
SERVER_LOG_PATH = os.path.expanduser("~") + "/logs/alfred_chrome_plugin/chrome_plugin.log"


def read_state_file(state_file):
    if not state_file:
        return None
    content = state_file.read()
    if content.strip() == "":
        return None
    keys = json.loads(content)
    return keys


# 校验HttpServer 是否处于开启状态
def check_http_server():
    # 如果文件不存在直接返回 false
    if not os.path.exists(STATE_FILE_PATH):
        return False
    state_file = open(STATE_FILE_PATH)
    # 读取到文件为空，返回 false，（可能是正在加锁状态）
    keys = read_state_file(state_file)
    if keys is None:
        return False
    state = keys.get("STATE", None)
    if state is not None and state == u"OPEN":
        pid = keys["PID"]
        # 如果检查进程存在
        if check_pid(pid):
            return True
        else:
            return False
    else:
        return False


def check_pid(pid):
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True


def handle_when_server_alive():
    start_time = time.time() * 1000
    keyword = sys.argv[1]
    url = "http://localhost:9567/do_search"
    form = {"keyword": keyword}
    req = urllib2.Request(url,
                          data=json.dumps(form),
                          headers={'Content-Type': 'application/json'})
    response = urllib2.urlopen(req)
    result = response.read()
    end_time = time.time() * 1000
    if config.IS_DEBUG_MODE:
        sys.stdout.write(result.decode("unicode_escape").encode("utf-8"))
        print "\nrt = {}".format(end_time - start_time)
    else:
        sys.stdout.write(result)
    sys.stdout.flush()
    exit(0)


def handle_when_server_not_alive():
    sys.stdout.write(alfred_util.get_alfred_out(
        [
            {
                "title": "服务正在初始化,请稍等3秒重试",
                "url": "",
            }
        ]
    ))
    sys.stdout.flush()
    # 启动服务脚本
    os.system("nohup python -u ./http/http_main.py > " + SERVER_LOG_PATH + " 2>&1 &")
    exit(0)


if __name__ == "__main__":
    if check_http_server():
        handle_when_server_alive()
    else:
        handle_when_server_not_alive()
