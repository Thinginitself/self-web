import json

from ResPool.protocal import FUNCTION_TYPE_DEFAULT


def wrap_update(update):
    if not update or type(update) is not dict or "function" not in update['rule']:
        return None
    else:
        rule = update['rule']
        update['rule'] = {
            "method": rule['function']['type'] + '#' + rule['function']['name'],
            "parameter": rule['function']['parameter']
        }

        return {FUNCTION_TYPE_DEFAULT: update}


def get_res_list_from_environment_json(file_name):
    data = json.load(open(file_name))
    res_list = list()
    # print data['environment']
    for name, content in data['environment'].iteritems():
        print(name)
        res_list.append((name,
                         content['model'],
                         wrap_update(content.get('update'))))
    return res_list


# for a in get_res_list_from_environment_json("../static/environment.json"): print a


def find_res(name, value, res_list):
    if value.has_key('range') and value.has_key('impact'):
        res_list.append((name, {
            "format": "dict",
            "initial": value
        }, None))
    elif type(value) is dict:
        res_list.append((name, {
            "format": "list",
            "initial": value.keys()
        }, None))
        for k, v in value.iteritems():
            find_res(k, v, res_list)
    else:
        raise Exception("software json file format error")


def get_res_list_from_software_json(file_name):
    data = json.load(open(file_name))
    res_list = list()
    for name, value in data['software']['feature'].iteritems():
        find_res(name, value, res_list)
    res_list.append(("constraint", {
        "format": "list",
        "initial": data['constraint']
    }, None))
    return res_list


# for a in get_res_list_from_software_json("../static/software.json"): print a


def get_res_list_from_property_json(file_name):
    data = json.load(open(file_name))
    res_list = list()
    for p in data['property']:
        res_list.append((p['name'], {
            "format": "number",
            "initial": p["initial"]
        }, None))
    return res_list


# for a in get_res_list_from_property_json("../static/property.json"): print a


def get_res_list_from_goal_json(file_name):
    data = json.load(open(file_name))
    res_list = [("goal", data["goal"])]
    return res_list

# for a in get_res_list_from_goal_json("../static/goal.json"): print a
