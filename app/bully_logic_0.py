from asyncio.windows_events import NULL
import time
from time import sleep
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
    ids_nodes= []
    hosts_ports= []
    number_of_hosts= int(os.environ["NUM_HOST"])
    register={}
    metrics = {
            "time": 0,
            "size": 0,
            "messages": 0
            }

    def preamble():

        service_register_status= None

        logic.hosts_ports= logic.define_ports()

        for host in logic.hosts_ports:
            candidate= logic.generate_node_id()
            while candidate in logic.ids_nodes: 
                candidate = logic.generate_node_id()

            logic.ids_nodes.append(candidate)


        for host in logic.hosts_ports:
            id_num= 0
            for port_id in logic.hosts_ports:
                service_register_status = logic.register_service(host, port_id,logic.ids_nodes[id_num])
                id_num += 1

        logic.start()
        
        return service_register_status

    def start():

        logic.metrics["time"]= time.clock()

        detail=logic.get_details(logic.hosts_ports)
        
        high_ID= logic.get_higher_nodes(detail,logic.ID_local)

        winner= logic.election(high_ID, logic.ID_local)

        if winner != "Redirect":

            logic.announce(winner)

            logic.metrics["time"]= time.clock() - logic.metrics["time"]

            logic.get_metrics()
    
    def go_deep(try_port):

        detail=logic.get_details(try_port)
        
        high_ID= logic.get_higher_nodes(detail,logic.ID_local)

        winner= logic.election(high_ID, logic.ID_local)

        if winner != "Redirect":

            logic.announce(winner)

            logic.metrics["time"]= time.clock() - logic.metrics["time"]

            logic.get_metrics()

        return winner
    
    def define_ports():
        count= logic.number_of_hosts
        first= 5010
        data_port=[]
        while count> 0:
            data_port.append(first)
            first+= 1
            count-= 1
        return data_port    
    
    def generate_node_id():
        millis = int(round(time.time() * 10))
        node_id = millis + randint(0, 2000)
        return node_id

    def register_service(host, port_id, node_id):
        status= logic.check_health_of_the_service(port_id)
        if status == "Failed":
            return status        
        data = {
            "ID": node_id,
            "port": port_id,
            "coordinator": None,
            "election": logic.election_local,
        }    
        if port_id == logic.port_local:
            logic.ID_local= data["ID"]
        url = logic.url_local + host + "/register"
        put_request = requests.post(url, json=data)              
        return put_request.status_code

    def get_details(ports_of_all_nodes):
        details= []
        for host in logic.register:
            if logic.register[host]['port'] in ports_of_all_nodes:
                id = logic.register[host]['ID']
                port = logic.register[host]['port']
                election = logic.register[host]['election']
                detail = {'ID': id, 'port': port,'election': election}
                details.append(detail)
        return details

    def get_higher_nodes(node_details, node_id):
        higher_node_array = []
        for each in node_details:
            if each['ID'] > node_id:
                higher_node_array.append(each['port'])
        return higher_node_array

    def election(higher_nodes_array, node_id):
        status_code_array = []
        if not higher_nodes_array:
            return node_id

        for each_port in higher_nodes_array:
            higher_nodes= higher_nodes_array
            higher_nodes.remove(each_port)
            url = logic.url_local + '%s/proxy' % each_port
            data = {
                "candidate_port": higher_nodes
            }
            logic.metrics.size+= sys.getsizeof(data)
            logic.metrics.messages+= 1
            post_response = requests.post(url, json=data)
            status_code_array.append(post_response.status_code)
        
        if not 200 in status_code_array:
            return node_id
             
        return "Redirect"

    def check_health_of_the_service(port):
        print('Checking for host stay-alive')   
        url = logic.url_local + port + '/services/health'
        response = requests.get(url)
        if response.status_code != 200:
            service_status = 'Failed'
        print('Service status: %s' % service_status)
        return service_status

    def announce(coordinator):
        all_nodes = logic.hosts_ports
        data = {
            'ID_coordinator': coordinator
        }
        for each_node in all_nodes:
            logic.metrics.size+= sys.getsizeof(data)
            logic.metrics.messages+= 1
            url = logic.url_local +'%s/announce' % all_nodes[each_node]
            requests.post(url, json=data)

    def get_metrics():
        details = []
        for each_port in logic.hosts_ports:
            url = logic.url_local + '%s/performance' % each_port
            data = requests.get(url)
            data.append(data.json())

        for host in data:
                logic.register['time'] += data[host]['time']
                logic.register['size'] += data[host]['size']
                logic.register['messages'] += data[host]['messages']
        return details
