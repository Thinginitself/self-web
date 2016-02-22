import hashlib
import json
import threading
import traceback
import types
import protocal

__author__ = 'jason'

import sys
import sky_client
import utils
import logging
from protocal import *

import logging.config

logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,  # this fixes the problem

    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',

        },
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'DEBUG',
            'propagate': True
        }
    }
})


def log():
    return logging.getLogger(__name__)


# def sky_request(func):
#     def wrapper(*args, **kwargs):
#         func(*args, **kwargs)
#
#         func_name = func.func_name
#         param = utils.get_func_arguments(func, args, kwargs)
#         log().info("CALL %s, param = %s", func_name, param)
#
#         sky_client.write(tuple=(TARGET, func_name, utils.encode(param)), fill_content_id=True)
#
#     return wrapper


def sky_request_for_result(func):
    def wrapper(*args, **kwargs):
        func(*args, **kwargs)

        func_name = func.func_name
        param = utils.get_func_arguments(func, args, kwargs)
        log().info("CALL %s, param = %s", func_name, param)

        cid = sky_client.write(tuple=(TARGET, func_name, utils.encode(param)), fill_content_id=True)

        result = sky_client.take(template=(RECEIVER, cid, "?"))
        if result is None or len(result) < 3:
            log().warn("request failed, cid=%s", cid)
            log().warn("result=%s", str(result))
            return
        return utils.decode(result[RESULT_IDX_CONTENT])

    return wrapper

sky_request = sky_request_for_result


def add_res_from_file(file_path, file_type="xml"):
    """
    add a Res from file.
    file format:
    <res_list>
    <res name="some name">
        <model>
            <format>
                number/dict/str/list
            </format>
            <initial>
                .... some basic value match the format.
            </initial>
        </model>
        <update>
            <delay>
                int value: number of clock for first update
            </delay>
            <next>
                1.int: const cycle length of one update
            </next>
            <rule>
                function.
            </rule>
        </update>
    <res>
    <res>some other res.</res>
    <res_list>

    the function's format:
    basic value type:
        1. int/float: 234 or 1.23
        2. list: [basic_value1, basic_value2]
        3. dict: { 'a' : basic_value }
        4. string: "some string"
        5. $name: a resource's value of last clock. $self for it's own value.
    function body format:
    <function name="function name" type="function type"> both type and name defines an function.
        <parameter name="parameter name">
            parameter value, can be a basic value or another function.
        </parameter>
        <parameter name="parameter name">
            this function may contains multi parameter.
        </parameter>
    </function>

    currently support the following function:
    type = math_expression
        name = add : a+b
            :parameter a,b: can be a basic value or a function
        name = division: a/b
        name = minus: a-b
        name = multiply: a*b
        name = mod: a mod b
        name = linear : ax+b
            :parameter a,b:
            :parameter x: it's usually $name.
        name = sin : asin(x)+b
        name = log : alog(x)+b
        name = sum : term1+term2+...
            :parameter term (multi): the adder.
    type = probability
        name = "markov_chain"
            :parameter state_set: list
            :parameter init_state: string, initial state.
            :parameter trans_matrix: float matrix, has the same size as state_set.
        name = "simple_rand" random int from [min, max]
        name = "normal_variate_rand":
            :parameter mu
            :parameter sigma
    type = others
        name = "combine"
            :parameter section (multi)
                <name></name>
                <value></value>
        name = "data_list"
            :parameter data: list

    :param file_path:
    :param file_type: only support xml for now.
    :return:
    """

    if file_type == "xml":
        with open(file_path, "r") as fin:
            context = fin.read()
            return add_res_from_xml_context(context)
    else:
        print "unknown file_type"


@sky_request
def add_res_from_xml_context(context):
    """
    similar with add_res_from_file(file).
    :param context: xml context.
    :return:
    """
    pass

def add_res_with_update_preprocess(name, model, update):
    """
    An wrapper of __add_res. Do some pre-processing of update.
    """

    if utils.is_callable(update):
        update_function = {protocal.FUNCTION_TYPE_CALLABLE, utils.function_to_string(update)}
    elif type(update) is dict:
        update_function = {protocal.FUNCTION_TYPE_DEFAULT: update}
    else:
        update_function = None
        log().warn("invalid update function, update=%s", update)

    add_res(name, model, update_function)


@sky_request
def add_res(name, model, update):
    """
    add a Res Object in ResPool
    :param name: name of the Res. Must be unique.
    :param model: model of the Res. This should be a dict containing:
            type:
            initial:
    :param update: update method of the Res. This value can be a function object, a dict or None.
        function: a function object or lambda object which accept the old value of this Res as the first parameter.
        dict: use one of default function. Format:
            {
                delay: int, update delay in clock count.
                next: can be an int constant or a default function;
                update : a default function;
            }
        None: no update function. This Res only can be modified by its default set function.
    :return: None
    """
    pass

@sky_request
def delete_res(name):
    pass

@sky_request
def modify_res_value(name, delta):
    """
    this res must be a number type.
    :param name: name of the res
    :param delta: change value.
    :return: None
    """
    pass


@sky_request
def set_res_value(name, value):
    """
    NOTICE this operation will override the auto-update result of the res.
    :param name:
    :param value:x
    :return:
    """
    pass


@sky_request_for_result
def get_res_value(name, clock=-1):
    pass

@sky_request_for_result
def get_all_res_value(names, clock=-1):
    pass


@sky_request_for_result
def get_res_values(name):
    """
    get all history value of this res.
    :param name:
    :return: value of length $clock
    """
    pass


@sky_request
def update_res(name, cycle=None, param=None):
    pass


@sky_request_for_result
def get_clock():
    pass


@sky_request
def ticktock(time=1):
    pass


@sky_request_for_result
def reset_res_pool():
    pass


def register_listener(ref_res, condition, action):
    """
    register an event listener,
    :param ref_res: list of res names.
    :param condition: can be an callable object, or One of Default Condition, see in default_condition.py
    :param action: an callable object.
    :return: event_id
    """

    if utils.is_callable(condition):
        condition_dict = {protocal.FUNCTION_TYPE_CALLABLE: utils.function_to_string(condition)}
        event_id = utils.calc_function_hash([condition])
    else:
        condition_dict = {protocal.FUNCTION_TYPE_DEFAULT: condition}
        event_id = condition + "@" + RECEIVER

    event_book[event_id] = action
    log().info("new event id:%s", event_id)
    add_event_listener(event_id, ref_res, condition_dict)


@sky_request
def add_event_listener(event_id, ref_res, condition):
    pass

@utils.timing
def run_action(action):
    return action()

def __listen():
    while True:
        try:
            event, notify_id = sky_client.take((RECEIVER, "Event", "?", "?"), timeout=10000, return_id=True)
            if event is not None:
                event_id = event[2]
                action = event_book.get(event_id)
                ret = run_action(action)
                #sky_client.write(tuple=(TARGET, notify_id, utils.encode(ret)))
        except Exception as e:
            log().error("handle Event exception, exception:%s\n%s\nevent=%s", e, traceback.format_exc(), event)


__listen_thread = threading.Thread(target=__listen)
event_book = dict()


def init_listener():
    __listen_thread.setDaemon(True)
    __listen_thread.start()
    # log().info("STARTED")
    # event_id -> callable action

@sky_request
def get_all_res_values(names):
    pass

@sky_request
def ticktock_to_next_update(force):
    pass

@sky_request
def set_all_res_value(all_res_value):
    pass

@sky_request
def get_all():
    pass