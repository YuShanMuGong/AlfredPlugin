# coding=utf-8

import sys
# 将本地的包，添加进入模块搜索
sys.path.append("./site-packages")
import alfred_util
from search_in_bookmark import ChromeBookMarkSearch, ChromeHistorySearch


def do_search(words):
    list = []
    list.append(ChromeBookMarkSearch().find(words))
    list.append(ChromeHistorySearch().find(words))
    return alfred_util.get_alfred_out(alfred_util.merge_result(list))


if __name__ == "__main__":
    word = sys.argv[1]
    words = [word.decode("utf-8")]
    result = do_search(words)
    sys.stdout.write(result)
    sys.stdout.flush()
    exit(0)
