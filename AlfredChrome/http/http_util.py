# coding=utf-8

def get_mapping_path(req_path):
    if req_path is None or req_path.strip() == "":
        return None
    mark_pos = req_path.find("?")
    return req_path[0:mark_pos + 1]
