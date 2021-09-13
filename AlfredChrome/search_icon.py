# coding=utf-8
import io
import os
import sys

import chrome_util
import urllib2

HTTP_PREFIX = "http://"
HTTPS_PREFIX = "https://"

CHROME_PATH = "/Library/Application Support/Google/Chrome"

CHROME_BOOK_MARK_PATH = os.path.expanduser("~") + "/" + CHROME_PATH + "/Default/Bookmarks"
CHROME_BOOK_HISTORY_PATH = os.path.expanduser("~") + "/" + CHROME_PATH + "/Default"
__CACHE_PATH = os.path.expanduser("~") + "/logs/alfred_caches/"


# 返回值 [{url,icon}]
def get_domain_icon(urls):
    return __get_icon_from_chrome_cache(urls)


def __get_icon_from_internet(urls):
    # 确保Cache文件夹一定存在
    icon_cache_path = __CACHE_PATH + "icons/"
    cache_folder = os.path.exists(icon_cache_path)
    if not cache_folder:
        os.makedirs(icon_cache_path)
    result = {}
    with chrome_util.get_db_conn("Favicons", CHROME_BOOK_HISTORY_PATH) as conn:
        for url in urls:
            domain = __get_domain_str(url)
            path = icon_cache_path + domain + ".png"
            if os.path.isfile(path) and os.path.getsize(path) > 0:
                result[url] = path
                continue
            cursor = conn.cursor()
            try:
                cursor.execute(__get_icon_search_sql(domain))
                rows = cursor.fetchall()
                if not rows:
                    continue
                icon_url = rows[0][0]
                res = urllib2.urlopen(icon_url, timeout=2)
                if res.getcode() != 200:
                    continue
                data = res.read()
                with io.open(path, "ab+") as f:
                    f.write(data)
                    f.flush()
                    f.close()
                res.close()
                result[url] = path
            except Exception as e:
                sys.stdout.write(str(e))
                if os.path.exists(path):
                    os.remove(path)
                pass
            finally:

                cursor.close()
    return result


# 从 Chrome 缓存中获取网页的 ICON
def __get_icon_from_chrome_cache(urls):
    icon_cache_path = __CACHE_PATH + "icons/"
    cache_folder = os.path.exists(icon_cache_path)
    if not cache_folder:
        os.makedirs(icon_cache_path)
    result = {}
    with chrome_util.get_db_conn("Favicons", CHROME_BOOK_HISTORY_PATH) as conn:
        for url in urls:
            domain = __get_domain_str(url)
            path = icon_cache_path + domain + ".png"
            if os.path.isfile(path) and os.path.getsize(path) > 0:
                result[url] = path
                continue
            cursor = conn.cursor()
            try:
                cursor.execute(__get_icon_sql(domain))
                rows = cursor.fetchall()
                if not rows:
                    continue
                icon_data = rows[0][0]
                with io.open(path, "ab+") as f:
                    f.write(icon_data)
                    f.flush()
                    f.close()
                result[url] = path
            except Exception as e:
                sys.stdout.write(str(e))
                if os.path.exists(path):
                    os.remove(path)
                pass
            finally:
                cursor.close()
    return result


def __get_domain_str(url):
    url = url.strip()
    http_index = url.find(HTTP_PREFIX)
    if http_index != -1:
        url = url[http_index + len(HTTP_PREFIX):]
    https_index = url.find(HTTPS_PREFIX)
    if https_index != -1:
        url = url[https_index + len(HTTPS_PREFIX):]
    # www.baidu.com?dddfdasfsdafsdafasd
    # wap.baidu.com?dddfdasfsdafsdafasd
    if url.find("www.") != -1 or url.find("wap.") != -1:
        first_pointer = url.find(".")
        url = url[first_pointer + 1:]
        second_pointer = url.find(".")
        return url[0:second_pointer]
    else:
        # 裸域名 无前缀
        first_pointer = url.find(".")
        return url[0:first_pointer]


# 获取 Icon的 URL
def __get_icon_search_sql(key):
    sql = """SELECT url from icon_mapping a
        INNER JOIN favicons b
        on a.icon_id = b.id
        where lower(page_url) like '%{0}%'
        ORDER BY a.id desc
        limit 1"""
    return sql.format(key)


# 获取Icon的二进制数据
def __get_icon_sql(key):
    sql = """select b.image_data from favicons a 
    inner join favicon_bitmaps b
    on a.id = b.icon_id
    where a.url like '%{0}%'
    order by (b.width * b.height) desc 
    limit 1"""
    return sql.format(key)


if __name__ == "__main__":
    print get_domain_icon(["www.baidu.com"])
