# coding=utf-8
import sys
import io
import os
import base64
from log import logBiz

file_max_size = 1024 * 1024 * 5


def main():
    arg = sys.argv
    if len(arg) == 1:
        sys.stdout.write('N|参数错误')
        return
    path = arg[1].strip()
    if not path:
        sys.stdout.write("N|参数错误")
        return

    if not os.path.isfile(path):
        logBiz('=====3=====')
        sys.stdout.write("N|不是文件")
        return

    fsize = os.path.getsize(path)
    if fsize > file_max_size:
        sys.stdout.write("N|文件大于5M")
        return

    file_bytes = io.open(path, mode='rb').read()
    b64 = base64.b64encode(file_bytes)
    sys.stdout.write("Y|" + b64)

if __name__ == '__main__':
    main()
