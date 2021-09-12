# coding=utf-8
import json
import io
import os
import shutil
import time
from abc import abstractmethod
import sqlite3
import collections
from pypinyin import pinyin, Style

# Chrome 书签文件地址


CHROME_PATH = "/Library/Application Support/Google/Chrome"

CHROME_BOOK_MARK_PATH = os.path.expanduser("~") + "/" + CHROME_PATH + "/Default/Bookmarks"
CHROME_BOOK_HISTORY_PATH = os.path.expanduser("~") + "/" + CHROME_PATH + "/Default/History"

CHROME_HISTORY_DB_CACHE_PATH = os.path.expanduser("~") + "/logs/alfred_caches/"
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
        body_list = []
        for item in result_list:
            info = item["info"]
            r = {"title": info["name"], "url": info["url"], "from": "bookmark"}
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
    @staticmethod
    def __match_words(info, words):
        weight = 0
        for word in words:
            if "name" in info:
                name = info["name"]
                if name.find(word) != -1:
                    weight += 1

            if "url" in info:
                if info["url"].find(word) != -1:
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
        result = collections.OrderedDict()
        with self.__get_db_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(self.__build_and_query_sql(words))
            r1 = cursor.fetchall()
            for item in r1:
                result[item[0]] = item
            cursor.execute(self.__build_or_query_sql(words))
            r2 = cursor.fetchall()
            for item in r2:
                key = item[0]
                if not result.has_key(key):
                    result[key] = item
        body_list = []
        for value in result.values():
            r = {"title": value[2], "url": value[1], "from": "history"}
            body_list.append(r)
        return body_list

    def __build_and_query_sql(self, words):
        condition = ""
        is_first = True
        for word in words:
            if not is_first:
                condition = condition + " and "
            is_first = False
            condition = condition + "(lower(title) like '%" + word.lower() + "%')"

        return "SELECT * from urls WHERE (" + condition + ") ORDER BY visit_count desc , last_visit_time desc limit 20"

    def __build_or_query_sql(self, words):
        condition = ""
        is_first = True
        for word in words:
            if not is_first:
                condition = condition + " or "
            is_first = False
            condition = condition + "(lower(title) like '%" + word.lower() + "%')"

        return "SELECT * from urls WHERE (" + condition + ") ORDER BY visit_count desc , last_visit_time desc limit 20"

    def __get_db_conn(self):
        db_file_path = self.__get_db_file_path()
        return sqlite3.connect(db_file_path)

    def __get_db_file_path(self):
        cache_folder = os.path.exists(CHROME_HISTORY_DB_CACHE_PATH)
        if not cache_folder:
            os.makedirs(CHROME_HISTORY_DB_CACHE_PATH)
        cache_file_path = CHROME_HISTORY_DB_CACHE_PATH + "history"
        if os.path.isfile(cache_file_path) and time.time() - os.path.getmtime(cache_file_path) < 30:
            return cache_file_path
        try:
            shutil.copy(CHROME_BOOK_HISTORY_PATH, cache_file_path)
        except:
            raise IOError("read history from chrome fail")
        return cache_file_path


if __name__ == '__main__':
    word = u"qqyouxiang"
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
