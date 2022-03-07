#!/bin/bash
docker build -f Dockerfile_host_0 -t leader-election-python-0:latest .
docker build -f Dockerfile_host_1 -t leader-election-python-1:latest .
docker build -f Dockerfile_host_2 -t leader-election-python-2:latest .
docker build -f Dockerfile_host_3 -t leader-election-python-3:latest .
docker build -f Dockerfile_host_4 -t leader-election-python-4:latest .

kubectl apply -f deployment.yaml
sleep 10
kubectl get pods