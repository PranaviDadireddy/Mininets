#!/usr/bin/env python
 
import socket
import sys
import os
import pickle
import time

CONFIG_DIR = "neighbours" 
ROUTING_DIR = "routing"
neighs = {}
routing_table = {}
def connectSocket(ip, port, message):
	TCP_IP = ip
	TCP_PORT = port
	BUFFER_SIZE = 1024
	#MESSAGE = "Hello, World!"
	 
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((TCP_IP, TCP_PORT))
	s.send(message)
	data = s.recv(BUFFER_SIZE)
	s.close()
	 
	print "received data:", data


def neighbours(f,name):
	neigh = open(f,"r")
	for line in neigh:
		ip,weight = line.rstrip().split(",")
		neighs[ip] = weight
	pickle.dump(neighs,open(CONFIG_DIR + "/" + name + ".pkl","wb"))

def broadcast(name):
	routers = pickle.load(open("routers.pkl","rb"))
	while True:
		print "Wating for 30 sec. to broadcast table.."
		time.sleep(20)		
		#routing_table = pickle.load(open(conf + "_route.pkl","rb"))
		for key,val in neighs.items():
			path = os.path.join(ROUTING_DIR, name)
			print "Broadcasting routing table to Client: ", key
			ips = routers[key]
			
			for ip in ips:
				flag = True
				try:
					connectSocket(ip,60,path)
				except Exception,e:
					flag = False
					print "socket error for ip\t", ip
		
				if flag:
					break
if __name__ == "__main__":
	
	if len(sys.argv) != 2:
		print 'Invalid Usage! Use: python client.py <IP> <PORT> \n'
		sys.exit(0)	
	'''	
	ip = str(sys.argv[1])
	port = int(sys.argv[2])
	print 'IP: %s' % ip 
	print 'Port: %d' % port
	'''
	conf = str(sys.argv[1])
	path = os.path.join(CONFIG_DIR,conf)
	'''
	neigh = open(path,"r")
	for line in neigh:
		ip, weight = line.split(",")
		print ip, weight
		connectSocket(ip, 60)
	'''
	neighbours(path,conf)
	broadcast(conf)
