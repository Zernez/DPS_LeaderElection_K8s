# DPS-Assignment 1

--For create the images (only the first time or when modifiy the code of container), inside the folder "app", firstly:

(`$docker build -f Dockerfile_host_0 -t leader-election-python-0:latest .` -----In development, not to run this command at now)

`$docker build -f Dockerfile_host_1 -t leader-election-python-1:latest .`

`$docker build -f Dockerfile_host_2 -t leader-election-python-2:latest .`

--For deploy the system run inside the app folder:

`$kubectl apply -f deployment.yaml`

--Check if is all ok:

`$kubectl get pods`

--The servers respond at:

(http:\\localhost:5010 -----In development, not available at now)

http:\\localhost:5011

http:\\localhost:5012

For stop running containers and kubernetes system:

`$kubectl delete deployment leader-election-python --grace-period=5`

--Decided for classic Flask server with JSON as messages

--Attention!!!!!!!!!!!!!!!!! Host 0 is in development and is not running!!!!!!! The only two available is Host 1 and Host 2


