from time import perf_counter
import time
import json
import requests
from random import randint
import sys
import os
import logging

class logic:

    url_local = "http://" + os.environ["ELECTION_SERVICE_SERVICE_HOST"] +":"
    port_local= int(os.environ["PORT_CONFIG"])
    ID_local= None
    election_local= False
    coordinator_local= None
    port_coordinator_local= None
    ids_nodes= []
    hosts_ports= []
    number_of_hosts= int(os.environ["NUM_HOST"])
    threads= []
    register= [dict() for x in range(number_of_hosts)]
    metrics = {
            "time_start": 0,
            "time_finish": 0,
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
                service_register_status = self.register_service(host, port_id,self.ids_nodes[id_num], id_num)
                id_num += 1

        self.start()
        
        return service_register_status

    def start(self):

        self.metrics["time_start"]= perf_counter()

        detail=self.get_details(self.hosts_ports)
        
        high_IDs= self.get_higher_nodes(detail)

        winner= self.election(high_IDs)

        if winner != "Redirect":

            self.announce(winner)

            self.metrics["time_finish"]= perf_counter()

            self.get_metrics()
        
        return
    
    def go_deep(self, high_IDs):

        if not self.hosts_ports:
            self.hosts_ports= self.define_ports()

        if not self.ids_nodes:
            self.ids_nodes= self.define_ids()
        
#        for thread in self.threads:
#           thread.join()
        
        if self.election_local== False:
            return

        if high_IDs is not None:
            winner= self.election(high_IDs)
        else:
            winner= self.ID_local

        if winner != "Redirect":

            self.announce(winner)

            self.metrics["time_finish"]= perf_counter()

            self.get_metrics()
        
        self.election_local= False
        return
    
    def define_ports(self):
        count= self.number_of_hosts
        first= 5010
        data_port=[]
        while count> 0:
            data_port.append(first)
            first+= 1
            count-= 1
        return data_port

    def define_ids(self):
        data= []  
        for ids in self.register:
            if ids['port']== self.port_local:
                self.ID_local= ids['ID']    
            data.append(ids['ID'])
        return data     
    
    def generate_node_id(self):
        millis = int(round(time.time()))
        node_id = millis + randint(0, 20000)
        return node_id

    def register_service(self, host, port_id, node_id, n):
#        status= self.check_health_of_the_service(port_id)
#        if status == "Failed":
#            return status
        if host == port_id:
            tempID= node_id
        else:
            tempID= None      
       
        data = {
            "ID": node_id,
            "port": port_id,
            "coordinator": None,
            "election": self.election_local,
            "seq": n,
            "ID_local": tempID
        }

        url = self.url_local + str(host) + "/register"           
        
        if host == self.port_local:
            if port_id == self.port_local:
                self.ID_local= node_id
            self.register[n].update(data)
            return {'Response': 'OK'}, 200
        else: 
            try:
                post_response = requests.post(url, json=data)
            except:
                print("Post request fail")
            else:
                code = 500   

        return post_response.status_code

    def get_details(self, ports_of_all_nodes):
        details= []
        for host in self.register:
            if host['port'] != self.port_local:
                id = host['ID']
                port = host['port']
                election = host['election']
                detail = {'ID': id, 'port': port,'election': election}
                details.append(detail)
        return details

    def get_higher_nodes(self, node_details):
        higher_node_array = []
        for each in node_details:
            if each['ID'] > self.ID_local:
                higher_node_array.append(each['port'])
        return higher_node_array

    def election(self, higher_nodes_array):
        status_code_array = []
        if not higher_nodes_array:
            return self.ID_local

        for each_port in higher_nodes_array:
            url = self.url_local + str(each_port) + '/redirect'
            candidates= higher_nodes_array
            candidates.remove(each_port)
            if not candidates:
                candidates= None
            
            data = {
                "candidate_port": candidates
                }
            self.metrics['size']+= sys.getsizeof(data)
            self.metrics['messages']+= 1

            try:
                post_response = requests.post(url, json=data)
                status_code_array.append(post_response.status_code)
            except:
                print("Post request fail")
            else:
                status_code_array.append(500) 

        if not 200 in status_code_array:
            return self.ID_local
             
        return "Redirect"

#    def check_health_of_the_service(port):
#        print('Checking for host stay-alive')   
#        url = self.url_local + 'port' + '/services/health'
#        response = requests.get(url)
#        if response.status_code != 200:
#            service_status = 'Failed'
#        print('Service status: %s' % service_status)
#        return service_status
   
    def announce(self, coordinator):
        status_code_array = []
        data = {
            'ID_coordinator': coordinator,
            'port_coordinator': self.port_local
        }
        for each_node in self.hosts_ports:
            if each_node == self.port_local:
                n= 0  
                for host in self.register:
                    self.register[n]['coordinator']= coordinator
                    self.register[n]['election']= False
                    n+= 1
                self.election_local= False
                self.coordinator_local= coordinator
                self.port_coordinator_local= self.port_local
            else:
                self.metrics['size']+= sys.getsizeof(data)
                self.metrics['messages']+= 1
                url = self.url_local + str(each_node) + '/announce'

                try:
                    requests.post(url, json=data)
                except:
                    print("Post request fail")
                else:
                    code = 500

        return {'Response': 'OK'}, 200

    def get_metrics(self):
        details = []
        for each_port in self.hosts_ports:
            if each_port != self.port_local: 
                url = self.url_local + str(each_port) + '/performance'
                data = requests.get(url).json()          
                self.metrics['time_finish'] = self.metrics['time_finish'] - self.metrics['time_start']
                self.metrics['size'] += data['size']
                self.metrics['messages'] += data['messages']
        logging.basicConfig(filename='app.log', filemode='w', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        logging.info('Metrics for test with %s machine', self.number_of_hosts)                
        logging.info('Time elspased for find the coordinator is %s', self.metrics['size'])
        logging.info('Total size of messages exchanged are %s', self.metrics['messages'])
        logging.info('Total number of messages exchanged are %s', self.metrics['messages'])
        logging.shutdown()
        os.system('mkdir /app/python/static')
        os.system('mv /app/app.log /app/python/static')
        return details
