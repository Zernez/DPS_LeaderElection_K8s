from asyncio.windows_events import NULL
import time
import json
import requests
from random import randint

class logic:

    url_local = "http://127.0.0.1:"
    port_local= 5010
    ID_local= None
    network= {}

    def __init__(self):
        self.register_service()
    
    def __init__(self):
        self.check_health_of_the_service()
    
    def __init__(self):
        self.election()

    def __init__(self):
        self.announce()

    def generate_node_id():
        millis = int(round(time.time() * 1000))
        node_id = millis + randint(0, 200)
        return node_id


    def register_service(self, port_id, node_id):

        data = {
            "ID": node_id,
            "port": port_id,
            "coordinator": None,
            "election": None
        }
        
        ports= self.get_ports_of_nodes()
        
        for port in ports:

            status= self.check_health_of_the_service(port)
            url = self.url_local + port +'/services'
            if status != "Failed":
                put_request = requests.put(url, json=data)
            else:
                restart()                

        url = self.url_local + port +'/services'
        put_request = requests.put(url, json=data)        
        
        if port == self.port_local:
            self.ID_local= node_id

        return put_request.status_code


    def check_health_of_the_service(self, port):
        print('Checking for host stay-alive')   
        url = self.url_local + port + '/services/alive'
        response = requests.get(url)
        if response.status_code != 200:
            service_status = 'Failed'
        print('Service status: %s' % service_status)
        return service_status

    def get_ports_of_nodes(self):
        ports_list = []
        response = requests.get(self.url_local + self.port_local + '/services')
        nodes = json.loads(response.text)
        for host in nodes:
            port = host['port']
            ports_list.append(port)
        return ports_list

    def get_higher_nodes(node_details, node_id):
        higher_node_array = []
        for each in node_details:
            if each['ID'] > node_id:
                higher_node_array.append(each['port'])
        return higher_node_array

    def election(self, higher_nodes_array, node_id):
        status_code_array = []
        for each_port in higher_nodes_array:
            url = self.url_local + '%s/proxy' % each_port
            data = {
                "node_id": node_id
            }
            post_response = requests.post(url, json=data)
            status_code_array.append(post_response.status_code)
        if 200 in status_code_array:
            return 200

    def ready_for_election(self, ports_of_all_nodes, self_election, self_coordinator):
        coordinator_array = []
        election_array = []
        node_details = self.get_details(ports_of_all_nodes)

        for each_node in node_details:
            coordinator_array.append(each_node['coordinator'])
            election_array.append(each_node['election'])
        coordinator_array.append(self_coordinator)
        election_array.append(self_election)

        if True in election_array or True in coordinator_array:
            return False
        else:
            return True

    def get_details(ports_of_all_nodes):
        node_details = []
        for each_node in ports_of_all_nodes:
            url = 'http://127.0.0.1:%s/services' % ports_of_all_nodes[each_node]
            data = requests.get(url)
            node_details.append(data.json())
        return node_details

    def announce(self, coordinator):
        all_nodes = self.get_ports_of_nodes()
        data = {
            'coordinator': coordinator
        }
        for each_node in all_nodes:
            url =self.url_local +'%s/announce' % all_nodes[each_node]
            print(url)
            requests.post(url, json=data)