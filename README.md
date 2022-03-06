# DPS-Assignment 1

# --05/03 Update! The main files bully_logic.py and main_server.py are finished in v2 branch (will merge in main) with metrics harvesting feature, system test ok with 5 hosts!!

--For create the images (only the first time or when modifiy the code of container), inside the folder "app", firstly:

(`$docker build -f Dockerfile_host_0 -t leader-election-python-0:latest .` -----In development, not to run this command at now)

`$docker build -f Dockerfile_host_1 -t leader-election-python-1:latest .`

`$docker build -f Dockerfile_host_2 -t leader-election-python-2:latest .`

--For deploy the system run inside the app folder:

`$kubectl apply -f deployment.yaml`

--Check if is all ok:

`$kubectl get pods`

if the output contains ErrImageNeverPull:

Try this command and then rebuild the docker image

`eval $(minikube docker-env)`

--The servers respond at:

`http:\\\localhost:<any_port_do_you_want>`

--For stop running containers and kubernetes system:

`$kubectl delete deployment leader-election-python --grace-period=2`

--In the deployment.yaml, in "data: mutex: 5011" a little below "kind: ConfigMap", is possible to change where the program start the bully election for the first time.

--In the deployment.yaml, in "data: num_host: 5" a little below "kind: ConfigMap", is obligatory to set when change the number of container 

--The program will return the result and metrics on http:\\\localhost:<any_port_do_you_want>, the winner will show the metrics









