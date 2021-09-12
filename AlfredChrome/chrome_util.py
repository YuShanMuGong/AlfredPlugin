# coding=utf-8
import os
import shutil
import sqlite3
import time

__CACHE_PATH = os.path.expanduser("~") + "/logs/alfred_caches/"


def get_db_conn(db_file_name, path):
    db_file_path = __get_db_file_path(db_file_name, path)
    return sqlite3.connect(db_file_path)


def __get_db_file_path(db_file_name, path):
    cache_folder = os.path.exists(__CACHE_PATH)
    if not cache_folder:
        os.makedirs(__CACHE_PATH)
    cache_file_path = __CACHE_PATH + db_file_name
    if os.path.isfile(cache_file_path) and time.time() - os.path.getmtime(cache_file_path) < 30:
        return cache_file_path
    try:
        shutil.copy(path + "/" + db_file_name, cache_file_path)
    except:
        raise IOError("read history from chrome fail")
    return cache_file_path
