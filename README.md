# DPS-Assignment 1

For create the images, firstly:
$docker build -f Dockerfile_host_0 -t leader-election-python-0:latest .
$docker build -f Dockerfile_host_1 -t leader-election-python-1:latest .

For deploy the system run inside the app folder:
$kubectl apply -f deployment.yaml

Check if is all ok:
$kubectl get pods

The server respond at:
 http:\\localhost:5010, 
http:\\localhost:5011

For developing the message we can use Flask-SocketIO as message exchanger using the same Flask library: https://flask-socketio.readthedocs.io/en/latest/getting_started.html
