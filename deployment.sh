#!/bin/sh
git pull origin main
docker-compose down
docker-compose build --no-cache
docker-compose up -d
docker rmi $(docker images -f "dangling=true" -q)
docker ps -f "name=gestion_consultas"
