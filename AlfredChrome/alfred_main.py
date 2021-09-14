# coding=utf-8
import os
import sys

# 将本地的包，添加进入模块搜索
sys.path.append("./site-packages")
import alfred_util
from search_in_bookmark import ChromeBookMarkSearch, ChromeHistorySearch


def do_search(words):
    list = []
    list.append(ChromeBookMarkSearch().find(words))
    list.append(ChromeHistorySearch().find(words))
    merged_result = alfred_util.merge_result(list)
    default_search_item = alfred_util.get_default_search_item(words)
    if len(merged_result) <= 2:
        merged_result.append(default_search_item)
    else:
        merged_result.insert(2, default_search_item)
    return alfred_util.get_alfred_out(merged_result)


if __name__ == "__main__":
    word = sys.argv[1]
    words = [word.decode("utf-8")]
    result = do_search(words)
    sys.stdout.write(result)
    sys.stdout.flush()
    exit(0)
