from sklearn import metrics
from sqlalchemy import false
from flask import Flask, jsonify, request, render_template
import os
import sys
import threading
import requests
from multiprocessing import Value
import logging
from bully_logic_0 import logic


if logic.port_local == int(os.environ["MUTEX"]):
    logic.election_local= True

if logic.election_local== True:
    logic.preamble()

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello from Python!"

@app.route('/services', methods=['GET'])
def get_node_details():
    metrics = jsonify({'ID': logic.ID_local, 'port': logic.port_local,'election': logic.election_local})
    logic.messages_size_local+= sys.getsizeof(metrics)
    logic.messages_local+= 1
    return metrics, 200

@app.route('/response', methods=['POST'])
def response_node():
    data = request.get_json()
    incoming_node_id = data['node_id']
    if logic.ID_local > incoming_node_id:
        threading.Thread(target=init, args=[False]).start()
        election = False
    return jsonify({'Response': 'OK'}), 200

@app.route('/announce', methods=['POST'])
def announce_coordinator():
    data = request.get_json()
    coordinator = data['coordinator']
    logic.coordinator = coordinator
    print('Coordinator is %s ' % coordinator)
    return jsonify({'response': 'OK'}), 200

@app.route('/proxy', methods=['POST'])
def proxy():
    with counter.get_lock():
        counter.value += 1
        unique_count = counter.value

    url = 'http://localhost:%s/response' % port_number
    if unique_count == 1:
        data = request.get_json()
        requests.post(url, json=data)

    return jsonify({'Response': 'OK'}), 200

@app.route('/performance', methods=['POST'])
def get_performance():

    return 

@app.route("/")
def resume():

    coordinator_result= None
    return render_template('index.html', winner= coordinator_result, timelapsed= logic.metrics.time, totalsize= logic.metrics.size, totalmessages= logic.metrics.messages)

def check_coordinator_health():
    threading.Timer(60.0, check_coordinator_health).start()
    health = logic.check_health_of_the_service(coordinator)
    if health == 'failed':
        logic.start()
    else:
        print('Coordinator is alive')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port= int(os.environ["INTERNAL_PORT"]))


