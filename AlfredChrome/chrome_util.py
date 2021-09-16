# coding=utf-8
import os
import shutil
import sqlite3
import time
import config

__CACHE_PATH = os.path.expanduser("~") + "/logs/alfred_caches/"


def get_db_conn(db_file_name, path):
    db_file_path = __get_db_file_path(db_file_name, path)
    return sqlite3.connect(db_file_path)


def __get_db_file_path(db_file_name, path):
    start_time = time.time() * 1000
    cache_folder = os.path.exists(__CACHE_PATH)
    if not cache_folder:
        os.makedirs(__CACHE_PATH)
    cache_file_path = __CACHE_PATH + db_file_name
    if os.path.isfile(cache_file_path) and time.time() - os.path.getmtime(cache_file_path) < 30:
        return cache_file_path
    checked_time = time.time() * 1000
    try:
        start_copy_time = time.time() * 1000
        shutil.copy(path + "/" + db_file_name, cache_file_path)
        end_copy_time = time.time() * 1000
        if config.IS_DEBUG_MODE:
            print("copy_time = {0}".format(end_copy_time - start_copy_time))
    except:
        raise IOError("read history from chrome fail")
    end_time = time.time() * 1000
    if config.IS_DEBUG_MODE:
        print("file_name={0},check_time={1},all_time={2}".format(db_file_name,checked_time - start_time,
              end_time - start_time))
    return cache_file_path
