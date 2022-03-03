from asyncio.windows_events import NULL
import time
import json
import requests
from random import randint
import sys
import os

class logic:

    url_local = "http://127.0.0.1:"
    port_local= int(os.environ["PORT_CONFIG"])
    ID_local= None
    election_local= False
    time_local= None
    messages_size_local= 0
    messages_local= 0
    time_elepsed_local= 0
    hosts_ports= [5010,5011,5012,5013,5014,5015]
    ids_nodes= []
    metrics = {
            "time": 0,
            "size": 0,
            "messages": 0
        }

    def preamble():

        service_register_status= None

        for host in logic.hosts_ports:
            candidate= logic.generate_node_id()
            while candidate in logic.ids_nodes: 
                candidate = logic.generate_node_id()

            logic.ids_nodes.append(candidate)

#To be modified, is wrong

#        for host in logic.hosts_ports:
#            for node_id in logic.ids_nodes:
#                service_register_status = logic.register_service(host, node_id)

        logic.start()
        
        return service_register_status

    def start():

        logic.time_elepsed_local= time.clock()

        detail=logic.get_details(logic.hosts_ports)
        
        high_ID= logic.get_higher_nodes(detail,logic.ID_local)

        logic.election(high_ID, logic.ID_local)

        logic.time_elepsed_local= time.clock() - logic.time_elepsed_local

    def generate_node_id():
        millis = int(round(time.time() * 10))
        node_id = millis + randint(0, 2000)
        return node_id

    def register_service(port_id, node_id):

        status= logic.check_health_of_the_service(port_id)
        if status == "Failed":
            return   
        
        url = logic.url_local + "/jsonservice/register"
        
        data = {
            "ID": node_id,
            "port": port_id,
            "coordinator": None,
            "election": logic.election_local,
        }
    
        ports= logic.get_ports_of_nodes()
        ids= logic.get_all_ids()
               
        if port_id == logic.port_local:
            logic.ID_local= data["ID"]       

        put_request = requests.put(url, json=data)              
        return put_request.status_code


    def check_health_of_the_service(port):
        print('Checking for host stay-alive')   
        url = logic.url_local + port + '/services/health'
        response = requests.get(url)
        if response.status_code != 200:
            service_status = 'Failed'
        print('Service status: %s' % service_status)
        return service_status

    def get_ports_of_nodes():
        ports_list = []
        response = requests.get(logic.url_local + logic.port_local + '/services')
        nodes = json.loads(response.text)
        for host in nodes:
            port = host['port']
            ports_list.append(port)
        return ports_list

    def get_all_ids():
        id_list = []
        response = requests.get(logic.url_local + logic.port_local + '/services')
        nodes = json.loads(response.text)
        for host in nodes:
            id = host['ID']
            id_list.append(id)
        return id_list

    def get_higher_nodes(node_details, node_id):
        higher_node_array = []
        for each in node_details:
            if each['ID'] > node_id:
                higher_node_array.append(each['port'])
        return higher_node_array

    def election(higher_nodes_array, node_id):
        status_code_array = []
        for each_port in higher_nodes_array:
            url = logic.url_local + '%s/proxy' % each_port
            data = {
                "node_id": node_id
            }
            post_response = requests.post(url, json=data)
            status_code_array.append(post_response.status_code)
        if 200 in status_code_array:
            return 200

    def ready_for_election(ports_of_all_nodes, self_election, self_coordinator):
        coordinator_array = []
        election_array = []
        node_details = logic.get_details(ports_of_all_nodes)

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

    def announce(coordinator):
        all_nodes = logic.get_ports_of_nodes()
        data = {
            'coordinator': coordinator
        }
        for each_node in all_nodes:
            url =logic.url_local +'%s/announce' % all_nodes[each_node]
            print(url)
            requests.post(url, json=data)