# coding=utf-8

import json
import io
import os
import chrome_util
from abc import abstractmethod
import collections
import search_icon
from pypinyin import pinyin, Style
import time
import config

# Chrome 书签文件地址

CHROME_PATH = "/Library/Application Support/Google/Chrome"

CHROME_BOOK_MARK_PATH = os.path.expanduser("~") + "/" + CHROME_PATH + "/Default/Bookmarks"
CHROME_BOOK_HISTORY_PATH = os.path.expanduser("~") + "/" + CHROME_PATH + "/Default"
BOOK_MARK_DEFAULT_ICON = os.getcwd() + "/icons/book_mark.png"
HISTORY_DEFAULT_ICON = os.getcwd() + "/icons/history.png"

# 各种中英文的符号字符，在做拼音转换的时候会去除符号字符
SYMBOL = u'~`!#$%^&*()_+-=|\';":/.,?><~·！@#￥%……&*（）——+-=“：’；、。，？》《{}【】[]'


def get_word_pinyin(word):
    res = pinyin(word, style=Style.NORMAL)
    res_str = ""
    for item in res:
        if type(item) == list:
            for i in item:
                try:
                    res_str += str(i)
                except Exception:
                    pass
        else:
            try:
                res_str += str(item)
            except Exception:
                pass
    return res_str.lower().decode("utf-8")


# 去除关键字中的标点符号 空格（中英文标点符号都会去除）
def get_out_symbol(word):
    for c in SYMBOL:
        word = word.replace(c, "")
    return word.strip()


class Search():

    @abstractmethod
    def find(self, words):
        pass


# Chrome 拼音搜索书签
class ChromeBookMarkSearch(Search):

    # 寻找关键字然后，返回找到的Chrome记录
    def find(self, words):
        book_mark = io.open(CHROME_BOOK_MARK_PATH, "r")
        mark_json = json.load(book_mark)
        roots = mark_json["roots"]
        result_list = list()
        for sub_root in roots.values():
            self.__doFind(sub_root, words, result_list)
        result_list.sort(lambda e, x: (e["weight"]), reverse=True)
        urls = []
        for item in result_list:
            info = item["info"]
            urls.append(info["url"])
        urls_dict = search_icon.get_domain_icon(urls)
        body_list = []
        for item in result_list:
            info = item["info"]
            r = {"title": info["name"],
                 "url": info["url"],
                 "from": "bookmark",
                 "icon": urls_dict.get(info["url"], BOOK_MARK_DEFAULT_ICON)
                 }
            body_list.append(r)
        return body_list

    def __doFind(self, root, words, result_list):
        # 如果类型是URL，则需要进行比对
        if "type" in root and root["type"] == "url":
            match_info = self.__match_words(root, words)
            pinyin_match = self.__pinyin_match(root, words)
            if match_info["match"] or pinyin_match["match"]:
                result_list.append({"info": root, "weight": match_info["weight"]})
            return
        children = root["children"]
        if type(children) == list:
            for item in children:
                self.__doFind(item, words, result_list)
            return
        if type(children) == dict:
            self.__doFind(children, words, result_list)

    # 返回值 true 和 weight(int)
    # 匹配关键字
    # 主要会匹配 name 和 url，比对时候忽略大小写
    @staticmethod
    def __match_words(info, words):
        weight = 0
        for word in words:
            lower_word = word.lower()
            if "name" in info:
                name = info["name"].lower()
                if name.find(lower_word) != -1:
                    weight += 1

            if "url" in info:
                url = info["url"].lower()
                if url.find(lower_word) != -1:
                    weight += 1
        return {"match": weight > 0, "weight": weight}

    @staticmethod
    def __pinyin_match(info, words):
        namePinyin = ""
        if "name" in info:
            # 返回的拼音是纯小写的，没有标点符号的
            namePinyin = get_word_pinyin(get_out_symbol(info["name"]))
        weight = 0
        for word in words:
            low_word = word.lower()
            if namePinyin and namePinyin.find(low_word) != -1:
                weight += 1
            if "url" in info:
                if info["url"].lower().find(low_word) != -1:
                    weight += 1
        return {"match": weight > 0, "weight": weight}


class ChromeHistorySearch(Search):

    def find(self, words):
        start_time = time.time() * 1000
        result = collections.OrderedDict()
        with chrome_util.get_db_conn("History", CHROME_BOOK_HISTORY_PATH) as conn:
            get_db_coon_time = time.time() * 1000
            cursor = conn.cursor()
            cursor.execute(self.__build_and_query_sql(words))
            r1 = cursor.fetchall()
            do_search_time = time.time() * 1000
            for item in r1:
                result[item[0]] = item
            end_and_search_time = time.time() * 1000
            # 只有当搜索关键字个数大于1的时候，才开启或查询
            if len(words) > 1:
                cursor.execute(self.__build_or_query_sql(words))
                r2 = cursor.fetchall()
                for item in r2:
                    key = item[0]
                    if not result.has_key(key):
                        result[key] = item
            end_or_search_time = time.time() * 1000
        body_list = []
        urls = []
        for value in result.values():
            urls.append(value[1])
        urls_dict = search_icon.get_domain_icon(urls)
        search_icon_time = time.time() * 1000
        for value in result.values():
            r = {"title": value[2],
                 "url": value[1],
                 "from": "history",
                 "icon": urls_dict.get(value[1], HISTORY_DEFAULT_ICON)
                 }
            body_list.append(r)
        end_time = time.time() * 1000
        if config.IS_DEBUG_MODE:
            print("and_search_time={0},or_search_time={1},search_icon_time={2},func_end_time={3}".format(end_and_search_time - start_time,
                  end_or_search_time - end_and_search_time ,
                 search_icon_time - end_or_search_time,
                  end_time - start_time))
            print("db_conn_time={0},execute_time={1}".format(get_db_coon_time - start_time,
                                                             do_search_time - get_db_coon_time))
        return body_list

    def __build_and_query_sql(self, words):
        condition = ""
        is_first = True
        for word in words:
            word = word.lower()
            if not is_first:
                condition = condition + " and "
            is_first = False
            condition = condition + "(lower(title) like '%" + word + "%' or lower(url) like '%" + word + "%')"
        return "SELECT * from urls WHERE (" + condition + ") ORDER BY visit_count desc , last_visit_time desc limit 20"

    def __build_or_query_sql(self, words):
        condition = ""
        is_first = True
        for word in words:
            word = word.lower()
            if not is_first:
                condition = condition + " or "
            is_first = False
            condition = condition + "(lower(title) like '%" + word + "%' or lower(url) like '%" + word + "%')"
        return "SELECT * from urls WHERE (" + condition + ") ORDER BY visit_count desc , last_visit_time desc limit 20"


if __name__ == '__main__':
    word = u"ceshi"
    result1 = ChromeBookMarkSearch().find([word])
    result2 = ChromeHistorySearch().find([word])
    result = collections.OrderedDict()
    for r in result1:
        result[r["title"]] = r

    for r in result2:
        key = r["title"]
        if not result.has_key(key):
            result[key] = r

    print str(json.dumps(result.values())).decode("unicode-escape")
