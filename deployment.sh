#!/bin/sh
cd /home/roch_inventario/roch_python
eval $(ssh-agent -s) && ssh-add /home/acceso/llaves
git pull origin master
docker-compose down
docker-compose build --no-cache
docker-compose up -d
docker rmi $(docker images -f "dangling=true" -q)
docker ps -f "name=roch_python"
