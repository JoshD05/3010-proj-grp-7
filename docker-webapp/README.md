# ECU CS Dashboard Docker Setup

This guide explains how to build, run, and manage the ECU CS Dashboard web application using Docker.

## Prerequisites
- Docker installed on your system (https://docs.docker.com/get-docker/)

## 1. Build the Docker Image
Navigate to the directory containing the Dockerfile:

```bash
cd docker-webapp
```

Build the Docker image and tag it (e.g., `webapp`):

```bash
docker build -t webapp .
```

## 2. Run the Docker Container
Run the container, mapping the necessary ports. For example, to map:
- Host port 80 to container port 80 (web server)
- Host port 5432 to container port 5432 (PostgreSQL)

I had issues mapping 80:80 and 5432:5432, so I used:
- Host port 8080 to container port 80 (web server)
- Host port 5433 to container port 5432 (PostgreSQL)

And set the container to always restart on boot:

```bash
docker run -d --name webapp --restart=always -p 80:80 -p 5432:5432 webapp
```
OR
```bash
docker run -d --name webapp --restart=always -p 8080:80 -p 5433:5432 webapp
```

- `-d` runs the container in detached mode
- `--restart=always` ensures the container starts on system boot or if it crashes
- `-p` maps host ports to container ports

## 3. Access the Application
- Web interface: [http://localhost:8080/cgi-bin/csdashboard.py](http://localhost:8080/cgi-bin/csdashboard.py)

## 4. Stopping and Restarting the Container
To stop the container:
```bash
docker stop webapp
```

To start it again:
```bash
docker start webapp
```