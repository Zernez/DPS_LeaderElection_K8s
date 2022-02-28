from flask import Flask
app = Flask(__name__)
from bully_logic_0 import logic

node_id = generate_node_id()
service_register_status = register_service(port_local, node_id)

@app.route("/")
def hello():
    return "Hello from Python!"

@app.route('/nodeDetails', methods=['GET'])
def get_node_details():
    return jsonify({'node_id': node_id, 'coordinator': coordinator,
                    'election': election, 'port': port_number}), 200

@app.route('/response', methods=['POST'])
def response_node():
    data = request.get_json()
    incoming_node_id = data['node_id']
    self_node_id = node_id
    if self_node_id > incoming_node_id:
        threading.Thread(target=init, args=[False]).start()
        election = False
    return jsonify({'Response': 'OK'}), 200

@app.route('/announce', methods=['POST'])
def announce_coordinator():
    data = request.get_json()
    coordinator = data['coordinator']
    bully.coordinator = coordinator
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

def check_coordinator_health():
    threading.Timer(60.0, check_coordinator_health).start()
    health = check_health_of_the_service(coordinator)
    if health == 'failed':
        init()
    else:
        print('Coordinator is alive')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port= 5000)


