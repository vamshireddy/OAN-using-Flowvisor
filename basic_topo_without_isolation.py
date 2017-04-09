""" 
    Simple topology for Home Access Network.
"""
import utils
import time
import pprint
import qos
import flowvisor
from mininet.topo import Topo
from mininet.node import RemoteController
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from functools import partial
from mininet.util import dumpNodeConnections

FLOW_VISOR_IP = "127.0.0.1"
FLOW_VISOR_PORT = 11001
NO_OF_HOMES_PER_AREA = 2
NO_OF_ISPS = 1
LINK_DATA_RATE = 50

class HomeAccessTopo(Topo):

    def add_mn_host(self):
        self.host_name_cntr += 1
        host_name = 'h%s' % (self.host_name_cntr)
        host = self.addHost(host_name)
        return host
    
    def add_mn_switch(self):
        self.switch_name_cntr += 1
        return self.addSwitch('s%d' % (self.switch_name_cntr), 
                dpid="%d" % (self.switch_name_cntr))

    def __init__(self, num_homes_per_zone, num_isps, link_bandwidth):    
        self.switch_name_cntr = 0
        self.host_name_cntr = 0

        # Initialize topology
        Topo.__init__( self )

        home_link_config = {'bw': link_bandwidth}
        isp_link_config = {'bw': link_bandwidth}
        core_link_config = {'bw': link_bandwidth}
        home_core_link_config = {'bw': link_bandwidth}
        home_inside_link_config = {'bw': link_bandwidth}
        
        #Create isps and connect to core switch
        core1 = self.add_mn_switch()
        
        for i in range(num_isps):
            isp = self.add_mn_host()
            self.addLink( core1, isp, **isp_link_config )
        
        #Create home switches for zone A
        aggrSw1 = self.add_mn_switch(); 

        for i in range(num_homes_per_zone):
            home_switch = self.add_mn_switch()
            self.addLink( aggrSw1, home_switch, **home_link_config)
            home_host = self.add_mn_host()
            self.addLink( home_switch, home_host, **home_inside_link_config )
   
        #Create home switches for zone B
        aggrSw2 = self.add_mn_switch()
        for i in range(num_homes_per_zone):
            home_switch = self.add_mn_switch()
            self.addLink( aggrSw2, home_switch, **home_link_config )
            home_host = self.add_mn_host()
            self.addLink( home_switch, home_host, **home_inside_link_config )
        
        #Connect zone A and Zone B to core switch
        core2 = self.add_mn_switch()

        self.addLink( core2, aggrSw1, **home_core_link_config )
        self.addLink( core2, aggrSw2, **home_core_link_config )

        #Create home switches for zone C
        aggrSw3 = self.add_mn_switch()
        for i in range(num_homes_per_zone):
            home_switch = self.add_mn_switch()
            self.addLink( aggrSw3, home_switch, **home_link_config)
            home_host = self.add_mn_host()
            self.addLink( home_switch, home_host, **home_inside_link_config )

        #Create home switches for zone D
        aggrSw4 = self.add_mn_switch()
        for i in range(num_homes_per_zone):
            home_switch = self.add_mn_switch()
            self.addLink( aggrSw4, home_switch, **home_link_config)
            home_host = self.add_mn_host()
            self.addLink( home_switch, home_host, **home_inside_link_config )

        #Connect zone C and Zone D to core switch
        core3 = self.add_mn_switch()
        self.addLink( core3, aggrSw3, **home_core_link_config )
        self.addLink( core3, aggrSw4, **home_core_link_config )
        
        #connect the cores
        self.addLink( core1, core2, **core_link_config )
        self.addLink( core2, core3, **core_link_config )
        self.addLink( core3, core1, **core_link_config )            

def create_topology(bandwidth):
    topo = HomeAccessTopo(NO_OF_HOMES_PER_AREA, NO_OF_ISPS, bandwidth)
    remote = partial(RemoteController, ip=FLOW_VISOR_IP, port=FLOW_VISOR_PORT)
    net = Mininet(topo=topo, link=TCLink, autoSetMacs=True, controller=remote)
    return net

if __name__ == '__main__':
    
    uplink = []
    downlink = []

    for i in [ 900, 1000]:
        net = create_topology(i)
        net.start()
        utils.enable_stp(net.switches)
        CLI(net)
        net.stop()

    print "Upload bandwidths: "+str(uplink)
    print "Download bandwidths: "+str(downlink)
