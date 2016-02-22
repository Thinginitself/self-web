from time import sleep
import logging.config
__author__ = 'admin'


import agent
import ResPool.client as client
import ResPool.default_condition
client.init_listener()
client.register_listener([],ResPool.default_condition.CONDITION_CLOCK_TICK, agent.run)

while True:
    #print "clock:",ResPool.client.get_clock()
    sleep(10)
