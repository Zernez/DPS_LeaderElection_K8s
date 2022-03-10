from time import perf_counter
import time
import json
import requests
from random import randint
import sys
import os
import logging
from threading import Thread, current_thread

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
                if service_register_status== 500:
                    return 500
                id_num += 1

        self.start()
        
        return 200

    def start(self):

        self.metrics["time_start"]= perf_counter()

        detail=self.get_details()
        
        high_IDs= self.get_higher_nodes(detail, self.ID_local)

        winner= self.election(high_IDs, self.ID_local)

        if winner != "Redirect":

            self.announce(winner)

            self.metrics["time_finish"]= perf_counter()

            self.get_metrics()
            
        self.election_local= False     
        return 200
    
    def go_deep(self, candidates):

        if not self.hosts_ports:
            self.hosts_ports= self.define_ports()

        if not self.ids_nodes:
            self.ids_nodes= self.define_ids()

        detail=self.get_details(candidates)
        
        high_IDs= self.get_higher_nodes(detail, self.ID_local)

        for thread in self.threads:
            if thread is not current_thread():
                thread.join()          

        if high_IDs is not None:
            winner= self.election(high_IDs, self.ID_local)
        else:
            winner= self.ID_local      

        if winner != "Redirect":

            self.announce(winner)

            self.metrics["time_finish"]= perf_counter()

            self.get_metrics()
        
        self.election_local= False
        return 200
    
    def define_ports(self):
        count= self.number_of_hosts
        first= 7070
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
        if host == port_id:
            tempID= node_id
        else:
            tempID= None      
       
        data = {
            "ID": node_id,
            "port": port_id,
            "coordinator": None,
            "election": True,
            "seq": n,
            "ID_local": tempID
        }

        url = self.url_local + str(host) + "/register"           
        
        if host == self.port_local:
            if port_id == self.port_local:
                self.ID_local= node_id
            self.register[n].update(data)
            return 200
        else: 
            try:
                post_response = requests.post(url, json=data)
            except:
                print("Post request fail")  
                return 500

        return post_response.status_code

    def get_details(self, port_range= []):
        details= []
        if port_range== []:
            port_range= self.hosts_ports
        for host in self.register:
            if host['port'] in port_range:
                if host['port'] != self.port_local:
                    id = host['ID']
                    port = host['port']
                    election = host['election']
                    detail = {'ID': id, 'port': port,'election': election}
                    details.append(detail)
        return details

    def get_higher_nodes(self, node_details, IDlocal):
        higher_node_array = []
        for each in node_details:
            if each['ID'] > IDlocal:
                higher_node_array.append(each['port'])
        return higher_node_array

    def election(self, higher_nodes_array, IDlocal):
        status_code_array = []
        if not higher_nodes_array:
            return IDlocal

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
                status_code_array.append(500) 

        if not 200 in status_code_array:
            return IDlocal
             
        return "Redirect"
   
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
                    code= requests.post(url, json=data)
                except:
                    print("Post request fail")                    

        return 200

    def get_metrics(self):
        details = []
        for each_port in self.hosts_ports:
            if each_port != self.port_local: 
                url = self.url_local + str(each_port) + '/performance'
                data = requests.get(url).json()          
                if data['time'] != 0:          
                    self.metrics['time_finish'] = self.metrics['time_finish'] - data['time']  
                self.metrics['size'] += data['size']
                self.metrics['messages'] += data['messages']
            else:
                if self.metrics['time_start'] != 0:                            
                    self.metrics['time_finish'] = self.metrics['time_finish'] - self.metrics['time_start']

        logging.basicConfig(filename='app.log', filemode='w', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        logging.info('Metrics for test with %s machine', self.number_of_hosts)                
        logging.info('Time elspased for find the coordinator is %s seconds', self.metrics['time_finish'])
        logging.info('Total size of messages exchanged are %s bytes', self.metrics['size'])
        logging.info('Total number of messages exchanged are %s', self.metrics['messages'])
        logging.info('%s,%s,%s', self.metrics['time_finish'], self.metrics['size'], self.metrics['messages'])
        logging.shutdown()
        os.system('mkdir /app/python/static')
        os.system('mv /app/app.log /app/python/static')
        return details
