#!/bin/bash
sh ./skyspace/run-tuplespace.sh &
python ./ResPool/res_pool.py &
python ./test_agent.py &