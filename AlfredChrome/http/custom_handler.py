# coding=utf-8
from SimpleHTTPServer import SimpleHTTPRequestHandler
import io
import json
import shutil
import time
import urllib
import http_util
from abc import abstractmethod
import sys

sys.path.append('../')
from AlfredChrome import alfred_main


class CustomHttpHandler(SimpleHTTPRequestHandler):

    def __init__(self, request, client_address, server):
        SimpleHTTPRequestHandler.__init__(self, request, client_address, server)
        self.shutdownHandler = ShutdownHandler(server)
        self.doSearchHandler = DoSearchHandler()
        self.checkHealthHandler = CheckHealthHanlder()

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

    def do_GET(self):
        path = urllib.unquote(self.path)
        print http_util.get_mapping_path(path)
        self.send_datas(u"你好世界")

    def do_POST(self):
        handler = ROUTE_CONFIG.get(self.path, None)
        if handler is None:
            self.send_datas(u"找不到页面")
            return
        start_time = time.time() * 1000
        content_length = int(self.headers['Content-Length'])
        content = urllib.unquote(self.rfile.read(content_length))
        res_obj = handler.handle(json.loads(content))
        if type(res_obj) == str or type(res_obj) == unicode:
            self.send_datas(res_obj)
        else:
            self.send_datas(json.dumps(res_obj))
        end_time = time.time() * 1000
        print "http invoke {} , rt={}".format(self.path, end_time - start_time)

    def __get_request_handler(self, path):
        pass


class CustomBizHandler:

    @abstractmethod
    def handle(self, content):
        pass


class DoSearchHandler(CustomBizHandler):

    def handle(self, content):
        keyword = content["keyword"]
        return alfred_main.do_main(keyword)


# 健康检查
class CheckHealthHanlder(CustomBizHandler):

    def handle(self, content):
        return "success"


# 手动关闭服务
class ShutdownHandler(CustomBizHandler):

    def __init__(self, server):
        self.server = server

    def handle(self, content):
        print("server start shutdown...")
        self.server.shutdown()
        print("server shutdown complete...")


ROUTE_CONFIG = {
    "/do_search": DoSearchHandler()
}
