# DPS-Assignment 1

# --05/03 Update! The main files bully_logic.py and main_server.py are finished in v2 branch (will merge in main) with metrics harvesting feature, system test ok with 5 hosts!!

Try this command:

`$bash lunch.sh`

and

`$bash halt.sh`

to start and terminate the clusters.

--Check if is all ok:

`$kubectl get pods`

--The servers respond at:

`http:\\\localhost:<any_port_do_you_want>`

--In the deployment.yaml, in "data: mutex: 5011" a little below "kind: ConfigMap", is possible to change where the program start the bully election for the first time.

--In the deployment.yaml, in "data: num_host: 5" a little below "kind: ConfigMap", is obligatory to set when change the number of container 

--The program will return the result and metrics on http:\\\localhost:<any_port_do_you_want>, the winner will show the metrics









