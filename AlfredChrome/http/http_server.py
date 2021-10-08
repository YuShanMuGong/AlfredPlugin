# coding=utf-8

import BaseHTTPServer


# 监听器的接口
class ServerListener(object):

    def on_active(self, server):
        pass

    def before_shutdown(self, server):
        pass

    def after_shutdown(self):
        pass


# 自定义的本地HTTP服务器
class PluginHttpServer(BaseHTTPServer.HTTPServer):

    def __init__(self, server_address, RequestHandlerClass, listener, bind_and_activate=True):
        self.listener = listener
        BaseHTTPServer.HTTPServer.__init__(self, server_address, RequestHandlerClass, bind_and_activate)

    def server_activate(self):
        BaseHTTPServer.HTTPServer.server_activate(self)
        self.listener.on_active(self)

    def shutdown(self):
        self.listener.before_shutdown(self)
        BaseHTTPServer.HTTPServer.shutdown(self)
        self.listener.after_shutdown()
