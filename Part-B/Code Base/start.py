#!/usr/bin/python

"""
Example network of Quagga routers
(QuaggaTopo + QuaggaService)
"""

import sys
import atexit
import time
import re

# patch isShellBuiltin
import mininet.util
import mininext.util
mininet.util.isShellBuiltin = mininext.util.isShellBuiltin
sys.modules['mininet.util'] = mininet.util

from mininet.util import dumpNodeConnections
from mininet.node import OVSController
from mininet.log import setLogLevel, info, output

from mininext.cli import CLI
from mininext.net import MiniNExT

from topo import QuaggaTopo

net = None


def startNetwork():
    "instantiates a topo, then starts the network and prints debug information"

    info('** Creating Quagga network topology\n')
    topo = QuaggaTopo()

    info('** Starting the network\n')
    global net
    net = MiniNExT(topo, controller=OVSController)
    net.start()

    info('** Dumping host connections\n')
    dumpNodeConnections(net.hosts)

    info('** Testing network connectivity\n')
    #net.ping(net.hosts)
    myping(net.hosts)

    info('** Dumping host processes\n')
    for host in net.hosts:
        host.cmdPrint("ps aux")

    info('** Running CLI\n')
    CLI(net)


def stopNetwork():
    "stops a network (only called on a forced cleanup)"

    if net is not None:
        info('** Tearing down Quagga network\n')
        net.stop()

def parsePing( pingOutput ):
	"Parse ping output and return packets sent, received."
	# Check for downed link
	if 'connect: Network is unreachable' in pingOutput:
		return (1, 0)
	r = r'(\d+) packets transmitted, (\d+) received'
	m = re.search( r, pingOutput )
	if m is None:
		error( '*** Error: could not parse ping output: %s\n' %
			   pingOutput )
		return (1, 0)
	sent, received = int( m.group( 1 ) ), int( m.group( 2 ) )
	return sent, received



def myping(hosts=None, timeout=None ):
	"""Ping between all specified hosts.
	   hosts: list of hosts
	   timeout: time to wait for a response, as string
	   returns: ploss packet loss percentage"""
	# should we check if running?
	packets = 0
	lost = 0
	ploss = None
	'''
	if not hosts:
		hosts = self.hosts
		output( '*** Ping: testing ping reachability\n' )
	'''
	s1 = time.clock()
	s2 = None
	flag = False

	for node in hosts:
		output( '%s -> ' % node.name )
		for dest in hosts:
			if node != dest:
				opts = ''
				if timeout:
					opts = '-W %s' % timeout
				
				pingH2 = time.clock()
				result = node.cmd( 'ping -c1 %s %s' % (opts, dest.IP()) )
				sent, received = parsePing( result )
				packets += sent
				if node.name == 'h2' and dest.name == 'h1':
					s2 = time.clock()
					convergeTime = (s2-s1)
					pingTime = (s2-pingH2)
					flag = True
				if received > sent:
					error( '*** Error: received too many packets' )
					error( '%s' % result )
					node.cmdPrint( 'route' )
					exit( 1 )
				lost += sent - received
				output( ( '%s ' % dest.name ) if received else 'X ' )

		if node.name == 'h2' and flag:
			output( "\nConvergence Time: ", convergeTime,'\n')
			output( "Ping time (h1 -> h2):", pingTime)

		output( '\n' )
		ploss = 100 * lost / packets
	output( "*** Results: %i%% dropped (%d/%d lost)\n" %
			( ploss, lost, packets ) )
	return ploss

if __name__ == '__main__':
    # Force cleanup on exit by registering a cleanup function
    atexit.register(stopNetwork)

    # Tell mininet to print useful information
    #setLogLevel('info')
    startNetwork()

