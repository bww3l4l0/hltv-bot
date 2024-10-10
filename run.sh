#!/bin/bash

trap ctrl_c INT

function ctrl_c(){
    pkill -P $$

}

python3 ./parser/proxy_maker.py

sudo docker start 167f1798a5b4 

n=$(wc -l < proxies.txt)
n=$((n+2))

echo workers:$n

# xvfb-run celery -A celery_tasks.app worker --loglevel=DEBUG --logfile=log.log --pool=prefork -n hltv -E -Q xyz --concurrency=$n &
celery -A celery_tasks.app worker --loglevel=INFO --logfile=./.logs/log.log --pool=prefork -n hltv -E -Q xyz --concurrency=$n &

"/home/sasha/Documents/vscode/hltv v2 bot/.venv/bin/python" "/home/sasha/Documents/vscode/hltv v2 bot/main.py" &
"/home/sasha/Documents/vscode/hltv v2 bot/.venv/bin/python" "/home/sasha/Documents/vscode/hltv v2 bot/sch.py" &

wait