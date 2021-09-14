# coding=utf-8
import collections
import json
import os

EMPTY_JSON = '{}'
HTTP_PREFIX = "http://"
HTTPS_PREFIX = "https://"


# 格式 title,url
# 官方给出的格式
# {"items": [
#     {
#         "uid": "desktop",
#         "type": "file",
#         "title": "Desktop",
#         "subtitle": "~/Desktop",
#         "arg": "~/Desktop",
#         "autocomplete": "Desktop",
#         "icon": {
#             "type": "fileicon",
#             "path": "~/Desktop"
#         }
#     }
# ]}
def get_alfred_out(infos):
    if infos is None:
        return EMPTY_JSON
    if not infos:
        return EMPTY_JSON
    result = []
    for item in infos:
        title = item["title"]
        url = item["url"]
        icon = item.get("icon", "")
        sub_title = __get_sub_title(item.get("from", ""), url)
        default_icon = {"type": "png", "path": icon}
        result.append(
            {
                "type": "default",
                "title": title,
                "subtitle": sub_title,
                "arg": url,
                "icon": default_icon
            }
        )
    return json.dumps({"items": result})


def __get_sub_title(data_from, url):
    url_title = __get_domain_url(url)
    if data_from == "bookmark" or data_from == u"bookmark":
        return u"来自书签 " + url_title
    if data_from == "history" or data_from == u"history":
        return u"来自历史记录 " + url_title
    if data_from == "hint" or data_from == u"hint":
        return u"来自推荐 " + url_title
    return "未知来源 " + url_title


# [[{},{}],[{}]] -> [{},{},{}]
# 按照url维度去重
def merge_result(result_lists):
    # 用于去除重复Key
    result_dict = collections.OrderedDict()

    for li in result_lists:
        for item in li:
            url = item.get("url", "")
            # 如果 title 不存在 或者 存在但是已经重复 则直接跳过
            if type(item) != dict or not url or result_dict.has_key(url):
                continue
            result_dict[url] = item
    return result_dict.values()


# http://www.baidu.com/dddddddd -> www.baidu.com
def __get_domain_url(url):
    url = url.strip()
    http_index = url.find(HTTP_PREFIX)
    if http_index != -1:
        url = url[http_index + len(HTTP_PREFIX):]
    https_index = url.find(HTTPS_PREFIX)
    if https_index != -1:
        url = url[https_index + len(HTTPS_PREFIX):]
    separated_index = url.find("/")
    if separated_index != -1:
        return url[0:separated_index]
    else:
        return url[0:25]


# 获取默认搜索引擎 Item
def get_default_search_item(words):
    key = ",".join(words)
    return {
        "title": u"在谷歌中搜索" + key,
        "url": "https://www.google.com.hk/search?q=" + key,
        "from": "hint",
        "icon": os.getcwd() + "/icons/google.png"
    }


if __name__ == "__main__":
    test_infos = [{"url": "baidu.com", "title": "baidu"}]
    result_json = get_alfred_out(test_infos)
    print result_json
