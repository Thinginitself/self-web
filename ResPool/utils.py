from collections import defaultdict
import time
import json
import marshal
import hashlib
import types
import base64

from clock import Clock
from random import random
from xml.etree import cElementTree as ET

__author__ = 'jason'


def calc_function_hash(func_list):
    s = ""
    for f in func_list:
        s += f.__code__.co_code
    return hashlib.sha1(s).hexdigest()


def get_set(dic, key):
    if key not in dic:
        dic[key] = set()
    return dic[key]


def get_list(dic, key):
    if key not in dic:
        dic[key] = list()
    return dic[key]


def function_to_string(func):
    if func is None:
        return None
    if not is_callable(func):
        raise Exception("func is not callable!")
    code_str = marshal.dumps(func.func_code)
    return base64.b64encode(code_str)


def string_to_function(string, function_name="func"):
    if string is None:
        return None
    string = base64.b64decode(string)
    code = marshal.loads(string)
    from res_manager import get

    func = types.FunctionType(code, dict(globals().items() + locals().items()), function_name)
    return func


def is_callable(func):
    return hasattr(func, '__call__')

def timing(f):
    def wrap(*args):
        time1 = time.time()
        ret = f(*args)
        time2 = time.time()
        print '%s function took %0.3f ms' % (f.func_name, (time2 - time1) * 1000.0)
        return ret
    return wrap


def get_data_from_xml_context(context):
    t = ET.XML(context)
    return etree_to_dict(t)


def etree_to_dict(t):
    d = {t.tag: {} if t.attrib else None}
    children = list(t)
    if children:
        dd = defaultdict(list)
        for dc in map(etree_to_dict, children):
            for k, v in dc.iteritems():
                dd[k].append(v)
        d = {t.tag: {k: v[0] if len(v) == 1 else v for k, v in dd.iteritems()}}
    if t.attrib:
        d[t.tag].update(('@' + k, v) for k, v in t.attrib.iteritems())
    if t.text:
        text = t.text.strip()
        if children or t.attrib:
            if text:
                d[t.tag]['#text'] = text
        else:
            d[t.tag] = text
    return d


def warp_update_value(func):
    """

    :param func:
    :return: format:
    {
        "function": function name,
        "parameter": {
            some parameter: parameter value,
            ...
        }
    }
    """
    if "function" not in func:
        if is_string(func) and not func.startswith("$"):
            return json.loads(func)
        else:
            return func
    ret = dict()
    f = func["function"]
    ret["method"] = f["@type"] + "#" + f["@name"]
    p = dict()
    ret["parameter"] = p
    if type(f["parameter"]) is not list:
        p[f["parameter"]["@name"]] = warp_update_value(f["parameter"]["#text"])
    else:
        for param in f["parameter"]:
            pname = param["@name"]
            if pname in p: #TODO bug here ~~
                if type(p[pname]) is list:
                    p[pname].append(warp_update_value(param["#text"]))
                else:
                    p[pname] = [p[pname], warp_update_value(param["#text"])]
            else:
                p[pname] = warp_update_value(param["#text"])
    return ret


def warp_update(update):
    ret = dict()
    ret["delay"] = int(update["delay"])
    ret["next"] = int(update["next"])
    ret["rule"] = warp_update_value(update["rule"])
    return ret


def get_func_arguments(func, args, kwargs):
    arg_cnt = func.func_code.co_argcount
    arg_defaults = func.func_defaults
    arg_names = func.func_code.co_varnames
    # if len(args) + len(kwargs) +  != arg_cnt:
    # log().error("argument count not match, args = %s, kwargs = %s, argcount = %d", args, kwargs, arg_cnt)
    # return
    param = dict().fromkeys(func.func_code.co_varnames[0:arg_cnt])
    if arg_defaults is not None:
        for i in range(len(arg_defaults)):
            param[arg_names[arg_cnt - len(arg_defaults) + i]] = arg_defaults[i]

    if args is not None:
        for i in range(len(args)):
            param[arg_names[i]] = args[i]

    if kwargs is not None:
        for k, v in kwargs.items():
            param[k] = v
    return param


def decode(obj):
    return json.loads(base64.b64decode(obj))


def encode(obj):
    return base64.b64encode(json.dumps(obj))


def is_string(string):
    return isinstance(string, basestring)