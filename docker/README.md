# Useful docker commands

Create Docker image app
```
docker build . -f Dockerfile -t app:latest
docker run -d --name app-1 -p 127.0.0.1:2222:22 -t app:latest
```
Build and start containers with docker-compose
```
docker-compose up --build -d
```
Stop and remove all containers
```
docker stop $(docker ps -q)
docker rm -f $(docker ps -aq)
```
Remove all images
```
docker system prune -af
```