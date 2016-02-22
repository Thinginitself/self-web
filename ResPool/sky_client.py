import logging

__author__ = 'jason'
import requests
import hashlib
import json
import base64
import random

SKY_SERVER = "http://127.0.0.1:9000"
WRITE_URL = "/skyentry/write"
READ_URL = "/skyentry/read"
TAKE_URL = "/skyentry/take"
RESET_URL = "/skyentry/reset"


def log():
    return logging.getLogger(__name__)


def __handle_result(r, is_multi, return_id):
    if r.status_code != 200:
        log().error("request failed, status code = %d", r.status_code)
        return
    ret = r.json()
    if not is_multi:
        if len(ret) != 1:
            if return_id:
                return None, None
            else:
                return None
        else:
            ret = ret[0]
            content = ret["content"].split(",")
            if return_id:
                return content[0:-1], content[-1]
            else:
                return content
    else:
        print "not implement yet"
        return None


def write(tuple, type=-1, expire=5000, fill_content_id=False):
    content, cid = get_content(tuple, fill_content_id)
    param = {
        "content": content,
        "type": type,
        "expire": expire
    }
    log().debug("SKY_CLIENT[write],data=%s", param)
    requests.post(SKY_SERVER + WRITE_URL, data=param)
    return cid


def read(template, is_multi=False, timeout=500, return_id=False):
    content, cid = get_content(template, False)
    param = {
        "content": content,
        "isMulti": is_multi,
        "timeout": timeout
    }
    log().debug("SKY_CLIENT[read],data=%s", param)
    r = requests.post(SKY_SERVER + READ_URL, data=param)
    return __handle_result(r, is_multi, return_id)


def take(template, is_multi=False, timeout=5000, return_id=False):
    content, cid = get_content(template, False)
    param = {
        "content": content,
        "isMulti": is_multi,
        "timeout": timeout
    }
    log().debug("SKY_CLIENT[take],data=%s", param)
    r = requests.post(SKY_SERVER + TAKE_URL, data=param)
    return __handle_result(r, is_multi, return_id)


def get_content(item_list, fill_content_id=True):
    """
    this will append content_id in result!
    :param item_list:
    :param return_id:
    :return: content , content_id
    """
    #print "get_content:", item_list, return_id
    # content = ",".join(map(__encode, item_list))

    content = ",".join(item_list or [])
    content_id = hashlib.sha1(content + str(random.random())).hexdigest()
    if fill_content_id:
        content = content + "," + content_id
    return content, content_id


def reset():
    r = requests.post(SKY_SERVER + RESET_URL)
    return r.status_code == 200