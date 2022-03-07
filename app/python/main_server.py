from flask import Flask, jsonify, request, render_template, send_file, send_from_directory
import time
from time import perf_counter
from threading import Thread
import os
from bully_logic import logic

app = Flask(__name__)

bully = logic()

if bully.port_local == int(os.environ["MUTEX"]):
    bully.election_local= True
    time.sleep(5)

if bully.election_local== True:
    bully.preamble()

@app.route('/register', methods=['POST'])
def preamble_register():
    data = request.get_json()
    n= data["seq"]
    if data["ID_local"] is not None:
        bully.ID_local= data["ID_local"]
    data.pop('seq', None)
    data.pop('ID_local', None)
    bully.register[n].update(data)
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
    bully.port_coordinator_local= data['port_coordinator']
    return jsonify({'Response': 'OK'}), 200

@app.route('/redirect', methods=['POST'])
def redirecting_election():
    data = request.get_json()
    candidate = data['candidate_port']
    bully.election_local= True
    thread= Thread(target=bully.go_deep, args=[candidate])
    bully.threads.append(thread)
    thread.start()    
    return jsonify({'Response': 'OK'}), 200

@app.route('/performance', methods=['GET'])
def get_performance():
    return jsonify({'time': bully.metrics['time_start'], 'size': bully.metrics['size'], 'messages': bully.metrics['messages']}), 200

@app.route('/')
def resume():
    if bully.coordinator_local is None:
        coordinator_result= "No coordinator for now..."
        return render_template('index.html', winner= coordinator_result, port_winner= coordinator_result, partecipants= bully.number_of_hosts, timelapsed= 0, totalsize= bully.metrics["size"], totalmessages= bully.metrics["messages"])
    else:
        coordinator_result= bully.coordinator_local
        if coordinator_result== bully.ID_local:
            return render_template('indexDownload.html', winner= coordinator_result, port_winner= "This machine", partecipants= bully.number_of_hosts, timelapsed= bully.metrics["time_finish"], totalsize= bully.metrics["size"], totalmessages= bully.metrics["messages"])
        else:
            return render_template('index.html', winner= coordinator_result, port_winner= bully.port_coordinator_local, partecipants= bully.number_of_hosts, timelapsed= 0, totalsize= 0, totalmessages= 0)            

@app.route('/download')
def download():
        return app.send_static_file('app.log')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port= int(os.environ["INTERNAL_PORT"]))


