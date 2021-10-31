# coding=utf-8
import sys
import time
import config

# 将本地的包，添加进入模块搜索
sys.path.append("./site-packages")

import alfred_util
from search_in_bookmark import ChromeBookMarkSearch, ChromeHistorySearch


def do_search(words):
    list = []
    start_time = time.time() * 1000
    list.append(ChromeBookMarkSearch().find(words))
    end_book_mark_time = time.time() * 1000
    list.append(ChromeHistorySearch().find(words))
    history_time = time.time() * 1000
    merged_result = alfred_util.merge_result(list)
    merged_time = time.time() * 1000
    default_search_item = alfred_util.get_default_search_item(words)
    if len(merged_result) <= 2:
        merged_result.append(default_search_item)
    else:
        merged_result.insert(2, default_search_item)
    end_time = time.time() * 1000
    if config.IS_DEBUG_MODE:
        print("book_mark={0},history={1},merged_time={2},end_time={3}".format(
            end_book_mark_time - start_time,
            history_time - end_book_mark_time,
            merged_time - history_time,
            end_time - start_time
        ))
    return alfred_util.get_alfred_out(merged_result)


def do_main(word):
    word = word.lstrip().strip()
    # 按照空格分隔成List
    words = word.split(" ")
    # 搜索时候要去除List中的空元素，因为中间可能有多个连续的空格
    result = do_search(list(filter(lambda x: x != '', words)))
    if config.IS_DEBUG_MODE:
        return result.decode("unicode_escape").encode("utf-8")
    else:
        return result


if __name__ == "__main__":
    result = do_main(sys.argv[1].decode("utf-8"))
    if config.IS_DEBUG_MODE:
        sys.stdout.write(result.decode("unicode_escape").encode("utf-8"))
    else:
        sys.stdout.write(result)
    sys.stdout.flush()
    exit(0)
