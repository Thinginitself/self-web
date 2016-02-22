import math
import res_manager
import utils
__author__ = 'jason'

METHOD_TIME = "Time"
# new method format. type=math
MATH_PREFIX = "math_expression"
METHOD_MATH_ADD = "math_expression#add"
METHOD_MATH_DIVISION = "math_expression#division"
METHOD_MATH_MINUS = "math_expression#minus"
METHOD_MATH_MULTIPLY = "math_expression#multiply"
METHOD_MATH_MOD = "math_expression#mod"
METHOD_MATH_LINEAR = "math_expression#linear"
METHOD_MATH_SIN = "math_expression#sin"
METHOD_MATH_LOG = "math_expression#log"
METHOD_MATH_SUM = "math_expression#sum"
METHOD_MATH_MEAN = "math_expression#mean"

# type = probability
PROBABILITY_PREFIX = "probability"
METHOD_PROBABILITY_MARKOV_CHAIN = "probability#markov_chain"
METHOD_PROBABILITY_SIMPLE_RAND = "probability#simple_rand"
METHOD_PROBABILITY_NORMAL_VARIATE_RAND = "probability#normal_variate_rand"

#type = others
METHOD_OTHERS_COMBINE = "others#combine"
METHOD_OTHERS_DATA_LIST = "others#data_list"
METHOD_OTHERS_APPROACH = "others#approach"

from time import strftime
from clock import Clock
from random import normalvariate, randint, random


def markov_chain(value, states, init_state, transform):
    if value not in states:
        print "invalid state:", value
        return init_state
    cur_index = states.index(value)
    p = random()
    weight_list = transform[cur_index]
    total_weight = sum(weight_list)
    cur_weight = 0.0
    index = 0
    for weight in weight_list:
        cur_weight += weight
        if cur_weight / total_weight > p:
            return states[index]
        index += 1


def get_value(value, v=None):
    if utils.is_callable(value):
        return value()
    elif value == "$self":
        return v
    elif value == "$clock":
        return Clock.get()
    elif utils.is_string(value) and value.startswith("$"):
        return res_manager.get(value[1:])
    else:
        return value


def approach(value, step, target):
    target_value = get_value(target)
    if abs(target_value - value) < step:
        return target_value
    elif target_value > value:
        return value + step
    else:
        return value - step


def get(data, return_type=None):
    if type(data) is not dict or "method" not in data:
        if return_type is None:
            return data
        elif return_type == "lambda":
            return lambda: data
        else:
            return None

    method = data["method"]
    parameter = data["parameter"]

    if method.startswith(MATH_PREFIX):
        if method == METHOD_MATH_ADD:
            a = get(parameter["a"])
            b = get(parameter["b"])
            method = lambda value: get_value(a, value) + get_value(b, value)
        elif method == METHOD_MATH_DIVISION:
            a = get(parameter["a"])
            b = get(parameter["b"])
            method = lambda value: get_value(a, value) / get_value(b, value)
        elif method == METHOD_MATH_MINUS:
            a = get(parameter["a"])
            b = get(parameter["b"])
            method = lambda value: get_value(a, value) - get_value(b, value)
        elif method == METHOD_MATH_MULTIPLY:
            a = get(parameter["a"])
            b = get(parameter["b"])
            method = lambda value: get_value(a, value) * get_value(b, value)
        elif method == METHOD_MATH_MOD:
            a = get(parameter["a"])
            b = get(parameter["b"])
            method = lambda value: get_value(a, value) % get_value(b, value)
        elif method == METHOD_MATH_LINEAR:
            a = get(parameter["a"])
            b = get(parameter["b"])
            x = get(parameter["x"])
            method = lambda value: get_value(a, value) * get_value(x, value) + get_value(b, value)
        elif method == METHOD_MATH_SIN:
            a = get(parameter["a"])
            b = get(parameter["b"])
            x = get(parameter["x"])
            method = lambda value: get_value(a, value) * math.sin(get_value(x, value)) + get_value(b, value)
        elif method == METHOD_MATH_LOG:
            a = get(parameter["a"])
            b = get(parameter["b"])
            x = get(parameter["x"])
            method = lambda value: get_value(a, value) * math.log(get_value(x, value)) + get_value(b, value)
        elif method == METHOD_MATH_MEAN:
            terms = parameter["term"]
            method = lambda value: 1.0 * sum([get_value(term, value) for term in terms]) / len(terms)
        elif method == METHOD_MATH_SUM:
            terms = parameter["term"]
            #print terms
            method = lambda value: sum([get_value(term, value) for term in terms])
        else:
            print "not support method:", method
    elif method.startswith(PROBABILITY_PREFIX):
        if method == METHOD_PROBABILITY_MARKOV_CHAIN:
            state_set = parameter["state_set"]
            init_state = parameter["init_state"]
            trans_matrix = parameter["trans_matrix"]
            method = lambda value: markov_chain(value, state_set, init_state, trans_matrix)
        elif method == METHOD_PROBABILITY_NORMAL_VARIATE_RAND:
            mu = get(parameter["mu"])
            sigma = get(parameter["sigma"])
            method = lambda value: normalvariate(get_value(mu, value), get_value(sigma, value))
        elif method == METHOD_PROBABILITY_SIMPLE_RAND:
            min_value = get(parameter["min"])
            max_value = get(parameter["max"])
            method = lambda value: randint(get_value(min_value, value), get_value(max_value, value))
        else:
            print "not support method:", method
    else:
        if method == METHOD_OTHERS_COMBINE:
            sections = parameter["section"]
            # print "sections:", sections
            method = lambda value: dict((section, get_value(section, value)) for section in sections)
        elif method == METHOD_OTHERS_DATA_LIST:
            data_list = parameter["data_list"]
            method = lambda value: data_list[Clock.get() % len(data_list)]
        elif method == METHOD_OTHERS_APPROACH:
            step = parameter["step"]
            target = parameter["target"]
            method = lambda value: approach(value, step, target)
        else:
            print "not support method:", method
    return method


