import time
import json
import requests
from random import randint
import sys
import os

class logic:

    url_local = "http://" + os.environ["ELECTION_SERVICE_SERVICE_HOST"] +":"
    port_local= int(os.environ["PORT_CONFIG"])
    ID_local= None
    election_local= False
    coordinator_local= None
    ids_nodes= []
    hosts_ports= []
    number_of_hosts= int(os.environ["NUM_HOST"])
    register={}
    metrics = {
            "time": 0,
            "size": 0,
            "messages": 0
            }

    def preamble(self):

        service_register_status= None

        self.hosts_ports= self.define_ports()

        for host in self.hosts_ports:
            candidate= self.generate_node_id()
            while candidate in self.ids_nodes: 
                candidate = self.generate_node_id()

            self.ids_nodes.append(candidate)


        for host in self.hosts_ports:
            id_num= 0
            for port_id in self.hosts_ports:
                service_register_status = self.register_service(host, port_id,self.ids_nodes[id_num])
                id_num += 1

        self.start()
        
        return service_register_status

    def start(self):

        self.metrics["time"]= time.clock()

        detail=self.get_details(self.hosts_ports)
        
        high_ID= self.get_higher_nodes(detail,self.ID_local)

        winner= self.election(high_ID, self.ID_local)

        if winner != "Redirect":

            self.announce(winner)

            self.metrics["time"]= time.clock() - self.metrics["time"]

            self.get_metrics()
        
        return
    
    def go_deep(self, try_port):

        detail=self.get_details(try_port)
        
        high_ID= self.get_higher_nodes(detail,self.ID_local)

        winner= self.election(high_ID, self.ID_local)

        if winner != "Redirect":

            self.announce(winner)

            self.metrics["time"]= time.clock() - self.metrics["time"]

            self.get_metrics()

        return winner
    
    def define_ports(self):
        count= self.number_of_hosts
        first= 5010
        data_port=[]
        while count> 0:
            data_port.append(first)
            first+= 1
            count-= 1
        return data_port    
    
    def generate_node_id(self):
        millis = int(round(time.time()))
        node_id = millis + randint(0, 20000)
        return node_id

    def register_service(self, host, port_id, node_id):
#        status= self.check_health_of_the_service(port_id)
#        if status == "Failed":
#            return status        
        data = {
            "ID": node_id,
            "port": port_id,
            "coordinator": None,
            "election": self.election_local
        }

        url = self.url_local + str(host) + "/register"           
        
        if host == self.port_local:
            self.ID_local= data["ID"]
            print("Same port.....................", file=sys.stdout)
            self.register.update(data)
            return "OK", 200
        else: 
            print("Directed to %d....................", host, file=sys.stdout)   
            put_request = requests.post(url, json=data)              
        
        print(self.register, file=sys.stdout)
        return put_request.status_code

    def get_details(self, ports_of_all_nodes):
        details= []
        for host in self.register:
            if self.register[host]['port'] in ports_of_all_nodes:
                id = self.register[host]['ID']
                port = self.register[host]['port']
                election = self.register[host]['election']
                detail = {'ID': id, 'port': port,'election': election}
                details.append(detail)
        return details

    def get_higher_nodes(self, node_details, node_id):
        higher_node_array = []
        for each in node_details:
            if each['ID'] > node_id:
                higher_node_array.append(each['port'])
        return higher_node_array

    def election(self, higher_nodes_array, node_id):
        status_code_array = []
        if not higher_nodes_array:
            return node_id

        for each_port in higher_nodes_array:
            higher_nodes= higher_nodes_array
            higher_nodes.remove(each_port)
            url = self.url_local + '%s/proxy' % each_port
            data = {
                "candidate_port": higher_nodes
            }
            self.metrics.size+= sys.getsizeof(data)
            self.metrics.messages+= 1
            post_response = requests.post(url, json=data)
            status_code_array.append(post_response.status_code)
        
        if not 200 in status_code_array:
            return node_id
             
        return "Redirect"

#    def check_health_of_the_service(port):
#        print('Checking for host stay-alive')   
#        url = self.url_local + port + '/services/health'
#        response = requests.get(url)
#        if response.status_code != 200:
#            service_status = 'Failed'
#        print('Service status: %s' % service_status)
#        return service_status
   
    def announce(self, coordinator):
        all_nodes = self.hosts_ports
        data = {
            'ID_coordinator': coordinator
        }
        for each_node in all_nodes:
            self.metrics.size+= sys.getsizeof(data)
            self.metrics.messages+= 1
            url = self.url_local +'%s/announce' % all_nodes[each_node]
            requests.post(url, json=data)
        return requests.status_code

    def get_metrics(self):
        details = []
        for each_port in self.hosts_ports:
            url = self.url_local + '%s/performance' % each_port
            data = requests.get(url)
            data.append(data.json())

        for host in data:
                self.register['time'] += data[host]['time']
                self.register['size'] += data[host]['size']
                self.register['messages'] += data[host]['messages']
        return details
