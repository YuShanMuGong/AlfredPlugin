# coding=utf-8
from SimpleHTTPServer import SimpleHTTPRequestHandler
import io
import json
import shutil
import time
import urllib
import http_util
from abc import abstractmethod

# sys.path.append('../')
import alfred_main


class CustomBizHandler:

    @abstractmethod
    def handle(self, server, content):
        pass


class DoSearchHandler(CustomBizHandler):

    def handle(self, server, content):
        keyword = content["keyword"]
        return alfred_main.do_main(keyword)


# 健康检查
class CheckHealthHanlder(CustomBizHandler):

    def handle(self, server, content):
        return "success"


# 手动关闭服务
class ShutdownHandler(CustomBizHandler):

    def handle(self, server, content):
        print("server start shutdown...")
        # server.shutdown()
        print("server shutdown complete...")
        return "shutdown complete"


class HandlerFactory(object):

    def __init__(self):
        self.doSearchHandler = DoSearchHandler()
        self.checkHealthHandler = CheckHealthHanlder()
        self.shutdownHandler = ShutdownHandler()

    def get_handler(self, path):
        if path == "/do_search":
            return self.doSearchHandler
        if path == "/check_health":
            return self.checkHealthHandler
        if path == "/shutdown":
            return self.shutdownHandler
        return None


handleFactory = HandlerFactory()

class CustomHttpHandler(SimpleHTTPRequestHandler):

    def send_datas(self, content):
        # 指定返回编码
        encoding = "utf-8"
        f = io.BytesIO()
        if type(content) == str:
            content_str = content
        else:
            content_str = content.encode("utf-8")
        f.write(content_str)
        f.seek(0)
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=%s" % encoding)
        self.send_header("Content-Length", str(len(content_str)))
        self.end_headers()
        shutil.copyfileobj(f, self.wfile)

    # get 方法传递的参数 都忽略
    def do_GET(self):
        path = urllib.unquote(self.path)
        path = http_util.get_mapping_path(path)
        handler = handleFactory.get_handler(path)
        if handler is None:
            self.send_datas(u"找不到页面")
            return
        res_obj = handler.handle(self, None)
        if type(res_obj) == str or type(res_obj) == unicode:
            self.send_datas(res_obj)
        else:
            self.send_datas(json.dumps(res_obj))

    def do_POST(self):
        handler = handleFactory.get_handler(self.path)
        if handler is None:
            self.send_datas(u"找不到页面")
            return
        start_time = time.time() * 1000
        content_length = int(self.headers['Content-Length'])
        content = urllib.unquote(self.rfile.read(content_length))
        res_obj = handler.handle(self, json.loads(content))
        if type(res_obj) == str or type(res_obj) == unicode:
            self.send_datas(res_obj)
        else:
            self.send_datas(json.dumps(res_obj))
        end_time = time.time() * 1000
        print "http invoke {} , rt={}".format(self.path, end_time - start_time)
