import io
import time

_BIZ_LOG = io.open("/Users/xs/Documents/pu_test/biz.log", "a+")


def logBiz(msg):
    _BIZ_LOG.write((getTimePrefix() + "|" + msg + "\n").decode("utf-8"))
    return


def getTimePrefix():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
