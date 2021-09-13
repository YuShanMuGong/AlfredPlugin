# coding=utf-8
import collections
import json

EMPTY_JSON = '{}'


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
        icon = item.get("icon")
        default_icon = {"type": "filetype", "path": "public.png"}
        sub_title = __get_sub_title(item.get("from",""))
        if icon:
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

def __get_sub_title(data_from):
    if data_from == "bookmark" or data_from == u"bookmark":
        return u"来自书签"
    if data_from == "history" or data_from == u"history":
        return u"来自历史记录"
    return "未知来源"

# [[{},{}],[{}]] -> [{},{},{}]
def merge_result(result_lists):
    # 用于去除重复Key
    result_dict = collections.OrderedDict()

    for li in result_lists:
        for item in li:
            if type(item) != dict or "title" not in item:
                continue
            result_dict[item["title"]] = item
    return result_dict.values()


if __name__ == "__main__":
    test_infos = [{"url": "baidu.com", "title": "baidu"}]
    result_json = get_alfred_out(test_infos)
    print result_json
