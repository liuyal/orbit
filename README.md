# orbit

## Useful docker commands
Create Docker image app
```
docker build . -f Dockerfile.app -t app:latest
docker run -d --name app-1 -p 127.0.0.1:2222:22 -t app
docker run -d --name app-2 -p 127.0.0.1:2223:22 -t app
```
Stop and remove all containers
```
docker stop $(docker ps -q)
docker rm -f $(docker ps -aq)
```
Start all services with docker-compose
```
docker-compose up
```
