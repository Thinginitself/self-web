sh ./skyspace/run-tuplespace.sh &
sleep 3
python ./ResPool/res_pool.py &
sleep 1
python ./test_agent.py &