# coding=utf-8
import io
import os
import sys
import hashlib
import time

import chrome_util
import urllib2
import config

HTTP_PREFIX = "http://"
HTTPS_PREFIX = "https://"

CHROME_PATH = "/Library/Application Support/Google/Chrome"

CHROME_BOOK_MARK_PATH = os.path.expanduser("~") + "/" + CHROME_PATH + "/Default/Bookmarks"
CHROME_BOOK_HISTORY_PATH = os.path.expanduser("~") + "/" + CHROME_PATH + "/Default"
__CACHE_PATH = os.path.expanduser("~") + "/logs/alfred_caches/"


# 返回值 [{url,icon}]
def get_domain_icon(urls):
    start_time = time.time() * 1000
    result = __get_icon_from_chrome_cache(urls)
    end_time = time.time() * 1000
    if config.IS_DEBUG_MODE:
        print "get_urls_icon===time={0}".format(end_time - start_time)
    return result


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
# 先按照URL去找ICON，找不到再用domain兜底
def __get_icon_from_chrome_cache(urls):
    icon_cache_path = __CACHE_PATH + "icons/"
    cache_folder = os.path.exists(icon_cache_path)
    if not cache_folder:
        os.makedirs(icon_cache_path)
    result = {}
    cache_result = __get_icon_by_url_from_cache(urls)
    result = dict(result.items() + cache_result[0].items())
    not_cache_urls = cache_result[1]
    # 都已经缓存了，直接返回即可
    if not not_cache_urls:
        return result

    with chrome_util.get_db_conn("Favicons", CHROME_BOOK_HISTORY_PATH) as conn:
        url_imgs_map = __get_icon_by_urls(not_cache_urls, conn)
        not_found_urls = []
        for url in not_cache_urls:
            # 如果找到了图片
            if url in url_imgs_map:
                result[url] = url_imgs_map[url]
            else:
                not_found_urls.append(url)
        # domain icon 兜底
        for url in not_found_urls:
            domain_icon_path = __get_icon_by_domain(url, conn)
            if domain_icon_path is not None:
                result[url] = domain_icon_path
    return result


# 从缓存中读取URL ICON
# 返回值 {key1:value1,key2:values},[not_match_key...]
def __get_icon_by_url_from_cache(keys):
    icon_cache_path = __CACHE_PATH + "icons/"
    icon_map = {}
    not_match_keys = []
    for key in keys:
        path = icon_cache_path + hashlib.md5(key).hexdigest() + ".png"
        if os.path.isfile(path) and os.path.getsize(path) > 0:
            # 如果从缓存中找到了
            icon_map[key] = path
        else:
            not_match_keys.append(key)
    return (icon_map, not_match_keys)


def __get_icon_by_domain(domain, conn):
    icon_cache_path = __CACHE_PATH + "icons/"
    path = icon_cache_path + hashlib.md5(domain).hexdigest() + ".png"
    if os.path.isfile(path) and os.path.getsize(path) > 0:
        # 如果从缓存中找到了，则直接put 进入result
        return path
    cursor = conn.cursor()
    try:
        cursor.execute(__get_domain_icon_sql(domain))
        rows = cursor.fetchall()
        # 找到了 icon，需要写进本地缓存
        if rows:
            icon_data = rows[0][0]
            with io.open(path, "ab+") as f:
                f.write(icon_data)
                f.flush()
                f.close()
            return path
    except Exception as e:
        sys.stdout.write(str(e))
        if os.path.exists(path):
            os.remove(path)
        pass
    finally:
        cursor.close()
    return None


# 返回值{url:path,....}
def __get_icon_by_urls(urls, conn):
    cursor = conn.cursor()
    icon_cache_path = __CACHE_PATH + "icons/"
    result = {}
    try:
        cursor.execute(__get_urls_icon_sql(urls))
        rows = cursor.fetchall()
        # 找到了 icon，需要写进本地缓存
        for row in rows:
            (url, img) = row
            path = icon_cache_path + hashlib.md5(url).hexdigest() + ".png"
            with io.open(path, "ab+") as f:
                f.write(img)
                f.flush()
                f.close()
            result[url] = path
    except Exception as e:
        sys.stdout.write(str(e))
        pass
    finally:
        cursor.close()
    return result


def __get_icon_by_url(url, conn):
    icon_cache_path = __CACHE_PATH + "icons/"
    path = icon_cache_path + hashlib.md5(url).hexdigest() + ".png"
    cursor = conn.cursor()
    try:
        cursor.execute(__get_url_icon_sql(url))
        rows = cursor.fetchall()
        # 找到了 icon，需要写进本地缓存
        if rows:
            icon_data = rows[0][0]
            with io.open(path, "ab+") as f:
                f.write(icon_data)
                f.flush()
                f.close()
            return path
    except Exception as e:
        sys.stdout.write(str(e))
        if os.path.exists(path):
            os.remove(path)
        pass
    finally:
        cursor.close()
    return None


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
    if url.find("www.") != -1 or url.find("wap.") != -1 or url.find("cloud."):
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


# 获取URL对应的二进制数据
def __get_url_icon_sql(key):
    sql = """select b.image_data from icon_mapping a 
    inner join favicon_bitmaps b 
    on a.icon_id = b.icon_id
    where a.page_url = "{0}"
    order by (b.width * b.height) desc 
    limit 1"""
    return sql.format(key)


# 获取URLs对应的二进制数据
def __get_urls_icon_sql(keys):
    condition = ""
    is_first = True
    for key in keys:
        if not is_first:
            condition += " , "
        is_first = False
        condition += "'{0}'".format(key)
    sql = """select page_url as url, b.image_data as image from icon_mapping a 
    inner join favicon_bitmaps b 
    on a.icon_id = b.icon_id
    where a.page_url in ({0})
    """
    return sql.format(condition)


# 获取域Icon的二进制数据
def __get_domain_icon_sql(key):
    sql = """select b.image_data from favicons a 
    inner join favicon_bitmaps b
    on a.id = b.icon_id
    where a.url like '%{0}%'
    order by (b.width * b.height) desc 
    limit 1"""
    return sql.format(key)


if __name__ == "__main__":
    print get_domain_icon(["www.baidu.com"])
