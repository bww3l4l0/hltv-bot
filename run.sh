#!/bin/bash

trap ctrl_c INT

function ctrl_c(){
    pkill -P $$

}

celery -A celery_tasks.app worker --loglevel=DEBUG --logfile=log.log --pool=solo -n 4545 -E -Q xyz &
celery -A celery_tasks.app worker --loglevel=DEBUG --logfile=log.log --pool=solo -n 4546 -E -Q xyz &

sudo docker start 2d33b59d874a 

"/home/sasha/Documents/vscode/hltv v2 bot/.venv/bin/python" "/home/sasha/Documents/vscode/hltv v2 bot/main.py" &
"/home/sasha/Documents/vscode/hltv v2 bot/.venv/bin/python" "/home/sasha/Documents/vscode/hltv v2 bot/sch.py" &

wait