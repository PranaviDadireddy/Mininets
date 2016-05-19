#!/usr/bin/env python
 
import socket
from threading import Thread
from SocketServer import ThreadingMixIn
import sys
import os
import pickle

CONFIG_DIR = "neighbours"
ROUTING_DIR = "routing"
neighs = {}
routing_table = {}
routers = {}
def createSockConnection(conf):
	class ClientThread(Thread):
	 
		def __init__(self,ip,port):
			Thread.__init__(self)
			self.ip = ip
			self.port = port
			print "[+] New thread started for "+ip+":"+str(port)
	 
	 
		def run(self):
			while True:
				data = conn.recv(2048)
				if not data: break
				print "Routing Table Received:", data
				node = resolve(self.ip)
				update_routing(node,data,conf)
				conn.send(data)  # echo
	 
	#TCP_IP = ip
	TCP_PORT = 60
	BUFFER_SIZE = 20  # Normally 1024, but we want fast response
	 
	 
	tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	#tcpsock.bind((TCP_IP, TCP_PORT))
	tcpsock.bind(('', TCP_PORT))
	threads = []
	init_routing(conf) 
	while True:
		tcpsock.listen(4)
		print "Waiting for incoming connections..."
		(conn, (ip,port)) = tcpsock.accept()
		newthread = ClientThread(ip,port)
		newthread.start()
		threads.append(newthread)
		
	for t in threads:
		t.join()

def resolve(ip):
	for key,val in routers.items():
		if ip in val:
			return key

	return null

def show_dict():
	print "Destination\tNext Hop\tCost"
	for key,value in routing_table.items():
		print key, "\t\t", value[0], "\t\t", value[1]
			
def init_routing(name):
	cons = pickle.load(open(CONFIG_DIR + "/" + name + ".pkl","rb"))
	for key,val in cons.items():
		routing_table[key] = (key,int(val))	

	print "Initial Routing Table: \n", show_dict()
	pickle.dump(routing_table, open(ROUTING_DIR + "/" + name, "wb"))

def update_routing(ip,recv,self_name):
	new_table = pickle.load(open( recv,"rb"))
	#print "recieved table:\n", new_table
	weight = int(new_table[self_name][1])
	
	print "Old Table: \n", show_dict()

	for key,val in new_table.items():
		next_hop = val[0]
		new_weight = int(val[1])
		if key != self_name:
			if key not in routing_table.keys():
				routing_table[key] = (ip,new_weight + weight)
				print "key:" , key , "entry:" , routing_table[key]
			else:
				row = routing_table[key]
				old_hop = row[0]
				old_weight = int(row[1])
				if new_weight + weight < old_weight :
					routing_table[key] = (ip, new_weight + weight)
	if ip not in routing_table.keys():
		routing_table[ip] = (ip,weight)
	print "Updated Table: \n" , show_dict()
	pickle.dump(routing_table, open(ROUTING_DIR + "/" + self_name, "wb"))
	#print ROUTING_DIR + "/" + self_name
	#print "dumped:" , pickle.load(open(recv,"rb"))			
		
	
def neighbours(f,name):
        neigh = open(f,"r")
        for line in neigh:
                ip,weight = line.rstrip().split(",")
                neighs[ip] = weight
        pickle.dump(neighs,open(f + ".pkl","wb"))
	
if __name__ == "__main__":
	if len(sys.argv) != 2:
		print 'Invalid Usage! Use: python server.py <IP> <PORT> \n'
		sys.exit(0)	
	'''	
	ip = str(sys.argv[1])
	port = int(sys.argv[2])
	print 'IP: %s' % ip 
	print 'Port: %d' % port
	'''
	
	with open("globalCnf","r") as r:
		for line in r:
			router,ip = line.rstrip().split(",")
			if router in routers.keys():
				list = routers[router]
				list.append(ip)
				routers[router] = list
			else:
				routers[router] = [ip]
	pickle.dump(routers,open("routers.pkl","wb")) 
	conf = str(sys.argv[1])
        path = os.path.join(CONFIG_DIR,conf)
	neighbours(path,conf)
	createSockConnection(conf)
		
