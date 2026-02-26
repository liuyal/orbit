# ORBIT

Contianerized web service using Angular + Nginx, FastAPI, and Mongodb.

![ORBIT Architecture](assets/orbit.drawio.svg)

# Setup ENV
Run cert generation script
```
certs\generate-ssl-certs.bat
```
or
```
certs/generate-ssl-certs.sh
```
Create .env file under env/ (All fields below are optional). GITHUB ENV variables are required for Runner status fetch otherwise optional.
```
MONGODB_HOST=
MONGODB_PORT=
MONGODB_USER=
MONGODB_PASSWORD=

GITHUB_API_URL=
GITHUB_OWNER=
GITHUB_REPOSITORY=
GITHUB_TOKEN=
```

# Build & Start Containers
Under docker folder run build script
```
cd docker
./setup --build
```
Start containser
```
./setup --start
```
Containers should be up as following
```
Loading environment variables from .env file...
Starting Docker containers...
[+] up 4/4
 ✔ Container mongodb-app  Recreated 3.2s
 ✔ Container apache-app   Recreated 3.7s
 ✔ Container backend-app  Recreated 1.9s
 ✔ Container frontend-app Recreated 1.5s
```

```
docker ps
CONTAINER ID   IMAGE                 COMMAND                  CREATED         STATUS         PORTS                                                                                NAMES
0677d6b1b84a   frontend-app:latest   "/docker-entrypoint.…"   6 minutes ago   Up 6 minutes   0.0.0.0:80->80/tcp, [::]:80->80/tcp, 0.0.0.0:443->443/tcp, [::]:443->443/tcp         frontend-app
36e96089f5e0   backend-app:latest    "/usr/bin/supervisor…"   6 minutes ago   Up 6 minutes   0.0.0.0:5000->5000/tcp, [::]:5000->5000/tcp                                          backend-app
df18b85294c5   apache-app:latest     "httpd-foreground"       6 minutes ago   Up 6 minutes   0.0.0.0:8080->80/tcp, [::]:8080->80/tcp, 0.0.0.0:8443->443/tcp, [::]:8443->443/tcp   apache-app
f9ad57f1ae43   mongodb-app:latest    "docker-entrypoint.s…"   6 minutes ago   Up 6 minutes   0.0.0.0:27017->27017/tcp, [::]:27017->27017/tcp                                      mongodb-app
```