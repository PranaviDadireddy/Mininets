"""
Example topology of Quagga routers
"""

import inspect
import os
from mininext.topo import Topo
from mininext.services.quagga import QuaggaService
from mininext.node import Host
from mininet.log import info, debug

from collections import namedtuple

#QuaggaHost = namedtuple("QuaggaHost", "name ip loIP")
net = None

QUAGGA_RUN_DIR = '/var/run/quagga'
CONFIG_DIR = 'configs'

class MyHost(Host):
    def __init__(self, name, ip, route, quaggaConfFile, zebraConfFile, *args, **kwargs):
        Host.__init__(self, name, ip=ip, *args, **kwargs)

        self.route = route
	self.quaggaConfFile = quaggaConfFile
        self.zebraConfFile = zebraConfFile

    def config(self, **kwargs):
        Host.config(self, **kwargs)

        debug("configuring route %s" % self.route)

        self.cmd('ip route add default via %s' % self.route)

	self.cmd('/usr/lib/quagga/zebra -d -f %s -z %s/zebra%s.api -i %s/zebra%s.pid' % (self.zebraConfFile, QUAGGA_RUN_DIR, self.name, QUAGGA_RUN_DIR, self.name))
        self.cmd('/usr/lib/quagga/ripd -d -f %s -z %s/zebra%s.api -i %s/ripd%s.pid' % (self.quaggaConfFile, QUAGGA_RUN_DIR, self.name, QUAGGA_RUN_DIR, self.name))

    def terminate(self):
        self.cmd("ps ax | egrep 'ripd%s.pid|zebra%s.pid' | awk '{print $1}' | xargs kill" % (self.name, self.name))

        Host.terminate(self)

class MyRouter(Host):
    def __init__(self, name, quaggaConfFile, zebraConfFile, intfDict, *args, **kwargs):
        Host.__init__(self, name, *args, **kwargs)

        self.quaggaConfFile = quaggaConfFile
        self.zebraConfFile = zebraConfFile
        self.intfDict = intfDict

    def config(self, **kwargs):
        Host.config(self, **kwargs)
        self.cmd('sysctl net.ipv4.ip_forward=1')

        for intf, attrs in self.intfDict.items():
            self.cmd('ip addr flush dev %s' % intf)
            if 'mac' in attrs:
                self.cmd('ip link set %s down' % intf)
                self.cmd('ip link set %s address %s' % (intf, attrs['mac']))
                self.cmd('ip link set %s up ' % intf)
            for addr in attrs['ipAddrs']:
                self.cmd('ip addr add %s dev %s' % (addr, intf))

        self.cmd('/usr/lib/quagga/zebra -d -f %s -z %s/zebra%s.api -i %s/zebra%s.pid' % (self.zebraConfFile, QUAGGA_RUN_DIR, self.name, QUAGGA_RUN_DIR, self.name))
        self.cmd('/usr/lib/quagga/ripd -d -f %s -z %s/zebra%s.api -i %s/ripd%s.pid' % (self.quaggaConfFile, QUAGGA_RUN_DIR, self.name, QUAGGA_RUN_DIR, self.name))

    def terminate(self):
        self.cmd("ps ax | egrep 'ripd%s.pid|zebra%s.pid' | awk '{print $1}' | xargs kill" % (self.name, self.name))

        Host.terminate(self)	

class QuaggaTopo(Topo):

    "Creates a topology of Quagga routers"

    def __init__(self):
        """Initialize a Quagga topology with 5 routers, configure their IP
           addresses, loop back interfaces, and paths to their private
           configuration directories."""
        Topo.__init__(self)

        # Directory where this file / script is located"
        selfPath = os.path.dirname(os.path.abspath(
            inspect.getfile(inspect.currentframe())))  # script directory

        # Initialize a service helper for Quagga with default options
        quaggaSvc = QuaggaService(autoStop=False)

	zebraConf = '%s/zebra.conf' % CONFIG_DIR

	#Adding Host 1
	quaggaConf = '%s/quagga-host1.conf' % CONFIG_DIR
	h1 = self.addHost('h1', cls=MyHost, ip = '192.168.1.1/24', route = '192.168.1.12', quaggaConfFile = quaggaConf, zebraConfFile = zebraConf)

	#Adding Host 2
	quaggaConf = '%s/quagga-host2.conf' % CONFIG_DIR
	h2 = self.addHost('h2', cls=MyHost, ip = '192.168.6.12/24', route = '192.168.6.1', quaggaConfFile = quaggaConf, zebraConfFile = zebraConf)

	#Adding Router 1
	eth0 = { 'ipAddrs' : ['192.168.1.12/24'] }
	eth1 = { 'ipAddrs' : ['192.168.2.1/24'] }
	eth2 = { 'ipAddrs' : ['192.168.4.1/24'] }

	intfs = { 'r1-eth0' : eth0,
		  'r1-eth1' : eth1,
		  'r1-eth2' : eth2 }

	quaggaConf = '%s/quagga1.conf' % CONFIG_DIR

	r1 = self.addHost( 'r1', cls=MyRouter, quaggaConfFile = quaggaConf, zebraConfFile = zebraConf, intfDict = intfs)

	#Adding Router 2
        eth0 = { 'ipAddrs' : ['192.168.2.12/24'] }
        eth1 = { 'ipAddrs' : ['192.168.3.1/24'] }

        intfs = { 'r2-eth0' : eth0,
                  'r2-eth1' : eth1 }

        quaggaConf = '%s/quagga2.conf' % CONFIG_DIR

        r2 = self.addHost( 'r2', cls=MyRouter, quaggaConfFile = quaggaConf, zebraConfFile = zebraConf, intfDict = intfs)

	#Adding Router 3
        eth0 = { 'ipAddrs' : ['192.168.4.12/24'] }
        eth1 = { 'ipAddrs' : ['192.168.5.1/24'] }

        intfs = { 'r3-eth0' : eth0,
                  'r3-eth1' : eth1 }

        quaggaConf = '%s/quagga3.conf' % CONFIG_DIR

        r3 = self.addHost('r3', cls=MyRouter, quaggaConfFile = quaggaConf, zebraConfFile = zebraConf, intfDict = intfs)


	#Adding Router 4
        eth0 = { 'ipAddrs' : ['192.168.3.12/24'] }
        eth1 = { 'ipAddrs' : ['192.168.5.12/24'] }
        eth2 = { 'ipAddrs' : ['192.168.6.1/24'] }

        intfs = { 'r4-eth0' : eth0,
                  'r4-eth1' : eth1,
                  'r4-eth2' : eth2 }

        quaggaConf = '%s/quagga4.conf' % CONFIG_DIR
	
	r4 = self.addHost('r4', cls=MyRouter, quaggaConfFile = quaggaConf, zebraConfFile = zebraConf, intfDict = intfs)

	self.addLink(h1, r1)
	self.addLink(r1, r2)
	self.addLink(r1, r3)
	self.addLink(r2, r4)
	self.addLink(r3, r4)
	self.addLink(r4, h2)

