#!/bin/bash

trap ctrl_c INT

function ctrl_c(){
    pkill -P $$

}

sudo docker start 2d33b59d874a 

n=$(wc -l < proxies.txt)
n=$((n+2))

celery -A celery_tasks.app worker --loglevel=DEBUG --logfile=log.log --pool=prefork -n hltv -E -Q xyz --concurrency=$n &

"/home/sasha/Documents/vscode/hltv v2 bot/.venv/bin/python" "/home/sasha/Documents/vscode/hltv v2 bot/main.py" &
"/home/sasha/Documents/vscode/hltv v2 bot/.venv/bin/python" "/home/sasha/Documents/vscode/hltv v2 bot/sch.py" &

wait