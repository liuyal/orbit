#!/usr/bin/env bash

docker build . -f Dockerfile_backend -t web-client-app:latest
docker build . -f Dockerfile_frontend -t server-app:latest
docker build . -f Dockerfile_mongodb -t mongodb-app:latest


docker run -d -p 27017:27017 --name mongo-container mongodb-app