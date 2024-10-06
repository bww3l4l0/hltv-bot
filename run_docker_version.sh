#!/bin/bash

trap ctrl_c INT

function ctrl_c(){
    pkill -P $$

}

/py/bin/python /parser/proxy_maker.py

# sudo docker start 2d33b59d874a 

n=$(wc -l < proxies.txt)
n=$((n+2))

echo workers:$n

# xvfb-run celery -A celery_tasks.app worker --loglevel=DEBUG --logfile=log.log --pool=prefork -n hltv -E -Q xyz --concurrency=$n &
/py/bin/celery -A celery_tasks.app worker --loglevel=DEBUG --logfile=log.log --pool=prefork -n hltv -E -Q xyz --concurrency=$n &

/py/bin/python "/main.py" &
/py/bin/python "/sch.py" &

wait