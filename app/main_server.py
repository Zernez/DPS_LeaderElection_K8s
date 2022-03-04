from flask import Flask, jsonify, request, render_template
import os
import sys
import requests
import time
import json
from bully_logic import logic

bully = logic()

if bully.port_local == int(os.environ["MUTEX"]):
    bully.election_local= True

if bully.election_local== True:
    bully.preamble()

app = Flask(__name__)

@app.route('/register', methods=['POST'])
def preamble_register():
    data = request.get_json()
#    data = json.load(str(data))
    bully.register[data["seq"]].update(data)
    return jsonify({'Response': 'OK'}), 200

@app.route('/announce', methods=['POST'])
def announce_coordinator():
    data = request.get_json()
    coordinator = data['ID_coordinator']
    n= 0
    for host in bully.register:
        bully.register[n]['coordinator']= coordinator
        bully.register[n]['election']= False
        n+= 1
    bully.election_local= False
    bully.coordinator_local= coordinator
    return jsonify({'Response': 'OK'}), 200

@app.route('/proxy', methods=['POST'])
def proxy():
    data = request.get_json()
    candidate = data['candidate_port']
#    if len(candidate)> 1:
    bully.go_deep()
#    else:
#        bully.announce(bully.ID_local)
#        bully.metrics["time"]= time.clock()-bully.metrics["time"]
#        bully.get_metrics()        
    return jsonify({'Response': 'OK'}), 200

@app.route('/performance', methods=['GET'])
def get_performance():
    return jsonify({'time': bully.metrics['time'], 'size': bully.metrics['size'], 'messages': bully.metrics['messages']}), 200

@app.route("/")
def resume():
    if bully.coordinator_local == None:
        coordinator_result= "No coordinator for now..."
    else:
        coordinator_result= bully.coordinator_local
    return render_template('index.html', winner= coordinator_result, partecipants= bully.number_of_hosts, timelapsed= bully.metrics["time"], totalsize= bully.metrics["size"], totalmessages= bully.metrics["messages"])

if __name__ == "__main__":
    app.run(host='0.0.0.0', port= int(os.environ["INTERNAL_PORT"]))


