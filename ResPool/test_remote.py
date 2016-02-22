from time import sleep
from ResPool import default_condition
from ResPool.clock import Clock
from res_manager import *

import default_functions

__author__ = 'jason'
import client
from random import random
import logging.config

logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': True,  # this fixes the problem

    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': True
        }
    }
})


def log():
    return logging.getLogger(__name__)


client.reset_res_pool()


def test_xml_load():
    print "testing xml load"
    names = client.add_res_from_file("../res_list.xml")
    sleep(2)
    log().info("clock:%d", client.get_clock())
    #client.init_listener()
    #client.register_listener([], default_condition.CONDITION_CLOCK_TICK, action)
    for i in range(10):
        client.ticktock(1)
        sleep(1)
        log().info("clock:%d", client.get_clock())
        for name in names:
            log().info("%s = %s", name, client.get_res_value(name))

log().info("clock:%d", client.get_clock())


def action():
    print "HELLO world, @CLOCK:", client.get_clock()

test_xml_load()


def test_old():
    client.ticktock(1)
    print client.get_clock()
    temp = "temperature"
    # def update(value, delta):
    # print type(value)
    # print type(delta)
    #     return value + delta
    update = {
        "method": default_functions.METHOD_RANDINT,
        "min": 11,
        "max": 20
    }
    client.add_res(temp, 20, update)
    # def humidity_update(value):
    #     if Clock.get() % 2 == 0:
    #         return value + random() * 0.1
    #     else:
    #         return value - random() * 0.1
    hum = "humidity"
    client.add_res(hum, "S1", {
        "method": default_functions.METHOD_MARKOV_CHAIN,
        "states": ["S1", "S2", "S3"],
        "transform": [
            [0.2, 0.5, 0.3],
            [0.2, 0.5, 0.3],
            [0.2, 0.5, 0.3],
        ]
    })

    sen = "sensor"
    client.add_res(sen, {'humidity': 0.5, 'temperature': 20}, {
        "method": default_functions.METHOD_TIME,
        "format": "%H%M%S"
    })
    # lambda: {'humidity': get('humidity'), 'temperature': get('temperature')})

    client.ticktock(1)
    client.update_res(temp, 2, 3)
    client.update_res(hum, 1)
    client.update_res(sen, 1)

    for i in range(100):
        client.ticktock(1)
        print "clock:", client.get_clock()
        print temp, ":", client.get_res_value(temp)
        print hum, ":", client.get_res_value(hum)
        print sen, ":", client.get_res_value(sen)
        print


        # def alert():
        # print "WARNING!!!!!!temp=", get(temp), "humidity:", get(hum)
        #
        # lid = client.add_listener(["temp", "hum"],
        # lambda: get(temp) > 30 or get(hum) < 0.4,
        # alert)
        # tock()


        #
        # for i in range(10):
        #     tick()
        #     tock()
        #
        # res_manager.report_xml()
