import logging

__author__ = 'jason'

from lxml.builder import E
from lxml.etree import tostring
from clock import Clock
import types
import utils


def log():
    return logging.getLogger(__name__)


class Res:
    def __init__(self, name, model, update_func):
        self.name = name
        self.model = model
        self.update_func = update_func
        self.value = list()
        # if is_simple_model(model):
        # try :
        # v = eval(model)
        #     except Exception:
        #         v = model
        # else:
        #     print "full schema not support yet."
        value = None
        if type(model) is dict and "initial" in model:
            value = model["initial"]
            if "format" in model:
                format = model["format"]
                if utils.is_string(value) and format in ["number", "dict", "str", "list"]:
                    log().debug("eval [value:%s] in [format:%s]", value, format)
                    if len(value) > 0:
                        value = eval(value)
                    else:
                        value = None
        self.set_value(value)


    def update(self, param=None):
        if self.update_func is None:
            return
        if not utils.is_callable(self.update_func):
            log().warn("update_func of res[%s] is not callable, update_func=%s", self.name, self.update_func)
            return
        arg_cnt = self.update_func.__code__.co_argcount
        if arg_cnt == 0:
            new_value = self.update_func()
        elif arg_cnt == 1:
            new_value = self.update_func(self.get_value())
        else:
            new_value = self.update_func(self.get_value(), param)
        self.set_value(new_value)

    def modify_value(self, delta):
        value = self.get_value()
        if type(value) is int or type(value) is float:
            self.set_value(value + delta)
        else:
            print "error at modify value"

    def set_value(self, value):
        clk = Clock.get()
        #if len(self.value) > 1 and self.value[-1][0] == clk:
        self.value.append((clk, value))

    def get_value(self, clock=-1):
        cur = Clock.get()
        if clock < 0:
            clock = cur + clock

        if clock > cur or clock < 0:
            return None

        for item in reversed(self.value):
            if item[0] <= clock:
                return item[1]

    def get_value_history(self):
        values = self.value
        clk = Clock.get()
        ret = [None] * clk
        if values is None or len(values) == 0:
            return
        idx = 0
        pre_value = None
        for time, value in values:
            while idx < time:
                ret[idx] = pre_value
                idx += 1
            pre_value = value
            if time < clk:
                ret[time] = value
        while idx < clk:
            ret[idx] = pre_value
            idx += 1
        return ret

# format:
# name -> res
pool = dict()

# format :
# clock -> [callback,...]
timers = dict()

# format
# id -> (res_list, condition, action)
listeners = dict()

# format:
# name->[listener_id,]
res_to_listener = dict()

changed_res_set = set()


def add_timer_callback(time, callback):
    utils.get_list(timers, time).append(callback)


def get_res(name):
    if name not in pool:
        return None
    return pool[name]


def get(name, clock=-1):
    res = get_res(name)
    if res is None:
        log().warn("get res failed, name=%s", name)
        return None
    else:
        return res.get_value(clock)


def add(name, model, update_func):
    pool[name] = Res(name, model, update_func)


def update(name, cycle=None, param=None):
    changed_res_set.add(name)
    res = get_res(name)
    res.update(param)
    if cycle is not None:
        add_timer_callback(Clock.get() + cycle(), lambda: update(name, cycle, param))


def add_listener(res_list, condition, action):
    if not isinstance(condition, types.FunctionType) \
            or not isinstance(condition, types.FunctionType):
        return None

    listener_id = utils.calc_function_hash([condition, action])
    listener = (res_list, condition, action)
    listeners[listener_id] = listener

    for name in res_list:
        utils.get_list(res_to_listener, name).append(listener_id)

    return listener_id


def remove_listener(listener_id):
    if listener_id not in listeners:
        return
    listener = listeners.pop(listener_id)
    res_list = listener[0]
    for name in res_list:
        res_to_listener[name].remove(listener_id)


def get_next_update_time():
    while len(timers) > 0:
        t = min(timers)
        if t < Clock.get():
            timers.pop(t, None)
        else:
            return t
    return -1


def run_timer():
    clk = Clock.get()
    if clk not in timers:
        return
    callback_list = timers[clk]
    for callback in callback_list:
        callback()
    timers.pop(clk, None)


def run_listener():
    listener_id_set = set()
    for res_name in changed_res_set:
        if res_name in res_to_listener:
            for lid in res_to_listener.get(res_name):
                listener_id_set.add(lid)

    for listener_id in listener_id_set:
        if listener_id in listeners:
            res_list, condition, action = listeners.get(listener_id)
            if condition():
                action()


def report():
    for name in pool:
        print name, " = ", pool.get(name).get_value()


def report_xml(file_name="report.xml", clock=-1):
    cur = Clock.get()
    if clock < 0:
        clock += cur
    content = E.content(clock=str(clock))
    for name in pool:
        value = str(pool.get(name).get_value(clock))
        content.insert(0, E.feature(E.name(name), E.currentValue(value)))
    with open(file_name, "w") as fout:
        fout.write(tostring(content, encoding='utf-8', xml_declaration=True, pretty_print=True))


def reset():
    pool.clear()
    timers.clear()
    listeners.clear()
    res_to_listener.clear()
    changed_res_set.clear()


def update_delay(name, delay, cycle, param=None):
    add_timer_callback(Clock.get() + delay, lambda: update(name, cycle, param))


def set_res_value(name, value):
    res = get_res(name)
    if res :
        return res.set_value(value)


def modify_value(name, delta):
    return get_res(name).modify_value(delta)


def get_values(name):
    return get_res(name).get_value_history()


def delete_res(name):
    r = pool.pop(name, None)
    if r is None:
        return False
    else:
        return True


def get_all_value(names, clock=-1):
    ret = {}
    for name in names:
        ret[name] = get(name,clock)
    return ret


def get_all_values(names):
    ret = {}
    for name in names:
        ret[name] = get_values(name)
    return ret


def set_all_res_value(all_res_value):
    for name, value in all_res_value.items():
        set_res_value(name, value)


def get_all(clock=-1):
    ret = {}
    for name in pool:
        ret[name] = get(name,clock)
    return ret