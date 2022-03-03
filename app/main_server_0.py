from dataclasses import dataclass
from sklearn import metrics
from sqlalchemy import false
from flask import Flask, jsonify, request, render_template
import os
import sys
import requests
import time
from bully_logic_0 import logic


if logic.port_local == int(os.environ["MUTEX"]):
    logic.election_local= True

if logic.election_local== True:
    logic.preamble()

app = Flask(__name__)

@app.route('/register', methods=['POST'])
def preamble_register():
    data = request.get_json()
    json = json.loads(logic.register)
    json.update(data)
    return 200

@app.route('/announce', methods=['POST'])
def announce_coordinator():
    data = request.get_json()
    coordinator = data['ID_coordinator']
    for host in logic.register:
        logic.register[host]['coordinator']= coordinator
        logic.register[host]['election']= False
        logic.election_local= False
    return 200

@app.route('/proxy', methods=['POST'])
def proxy():
    data = request.get_json()
    candidate = data['candidate_port']
    if len(candidate)> 1:
        logic.go_deep(candidate)
    else:
        logic.announce(candidate)
        logic.metrics["time"]= time.clock()-logic.metrics["time"]
        logic.get_metrics()        
    return 200

@app.route('/performance', methods=['GET'])
def get_performance():
    return jsonify({'time': logic.metrics['time'], 'size': logic.metrics['size'], 'messages': logic.metrics['messages']}), 200

@app.route("/")
def resume():
    coordinator_result= logic.register[0]['coordinator']
    return render_template('index.html', winner= coordinator_result, timelapsed= logic.metrics.time, totalsize= logic.metrics.size, totalmessages= logic.metrics.messages)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port= int(os.environ["INTERNAL_PORT"]))


