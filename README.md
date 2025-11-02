# tm_project

## postgres database setup
```

```

## Useful docker commands
Create Docker image app
```
docker build . -f Dockerfile.app -t app:latest
docker run -d --name app-1 -p 127.0.0.1:2222:22 -t app
docker run -d --name app-2 -p 127.0.0.1:2223:22 -t app
```
Start PostgreSQL database
```
docker build . -f Dockerfile.postgres -t db:latest
docker rm -f postgres-db
docker volume prune -f
docker run -d --name postgres-db -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=postgres -e PGDATA=/var/lib/postgresql/data/pgdata -p 5432:5432 db:latest
```
Connect to postgres database
```
psql postgresql://postgres:postgres@localhost:5432/postgres
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
