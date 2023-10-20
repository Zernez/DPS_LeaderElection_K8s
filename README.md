# Bully algorithm improved implemented with Docker-Kubernetes

--For create the images (only the first time or when modifiy the code of container), inside the folder "app" for each of the dockerfile, firstly:

`$docker build -f Dockerfile_host_<number_of_the:container> -t leader-election-python-<number_of_the:container>:latest .`

--For deploy the system run inside the app folder:

`$kubectl apply -f deployment.yaml`

--Check if is all ok:

`$kubectl get pods`

--The servers respond at:

http:\\\localhost:<any_port_do_you_want>

--For stop running containers and kubernetes system:

`$kubectl delete deployment leader-election-python --grace-period=2`

--The unit-test start with this command in the app folder:

`$pip install pytest` (only one time for install the dependency)

`$pytest test/test_bully_logic.py`

--In the deployment.yaml, in "data: mutex: 5011" a little below "kind: ConfigMap", is possible to change where the program start the bully election for the first time.

--In the deployment.yaml, in "data: num_host: 20" a little below "kind: ConfigMap", is obligatory to set when change the number of container 

--The program will return the result and metrics on http:\\\localhost:<any_port_do_you_want>, the winner will show the metrics

![K8s](kubernetes.png)









