# coding=utf-8
import SocketServer
import atexit

from custom_handler import CustomHttpHandler


def shutdown(httpd):
    httpd.shutdown()


def start_server():
    server_host = '127.0.0.1'
    server_port = 8080
    httpd = SocketServer.TCPServer((server_host, server_port), CustomHttpHandler)
    atexit.register(shutdown, httpd)
    print(u'http服务启动' + str(server_host) + u'端口:' + str(server_port))
    httpd.serve_forever()


if __name__ == "__main__":
    start_server()
