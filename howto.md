celery -A celery_tasks.app worker --loglevel=DEBUG --logfile=log.log --pool=solo -n 4545 -E -Q xyz & - запускает worker

docker run --name my-redis -p 6379:6379 -d redis - запуск контейнера, создание
docker start 2d33b59d874a - загрузка существующего контейнера

