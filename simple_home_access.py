""" 
    Simple topology for Home Access Network.
"""
import utils
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
FLOW_VISOR_PORT = 6633
NO_OF_HOMES_PER_AREA = 2
NO_OF_ISPS = 2 
MAX_DATARATE_OF_INTERFACE = 1000000
SLICES = {
        'comcast': { 
                    'email' : 'comcast.net', 
                    'ip': 'localhost', 
                    'port' : '11001', 
                    'queue_id' : '1',
                    'hosts': ['h3', 'h4', 'h9', 'h10', 'h1'],
                    'ip_mappings': {'h3': '10.0.0.3', 'h4': '10.0.0.4','h9': '10.0.0.9','h10': '10.0.0.10','h1': '10.0.0.1'},
                    'rules': 
                    [
                    {'name': 'comcast', 'match_str': 'nw_src=10.0.0.0/24', 'priority':'100', 'sw_type': 'non-edge', 'queue_id': '1',
                            'permissions': '7'}
                    ]
                }, 
        'verizon': { 
                    'email' : 'verizon.net', 
                    'ip' : 'localhost', 
                    'port' : '11002', 
                    'queue_id' : '2', 
                    'hosts': ['h5', 'h6', 'h7', 'h8', 'h2'],
                    'ip_mappings': {'h5': '192.168.0.5', 'h6': '192.168.0.6','h7': '192.168.0.7','h8': '192.168.0.8','h2': '192.168.0.2'},
                    'rules': 
                    [
                    {'name': 'verizon', 'match_str': 'nw_src=192.168.0.0/24', 'priority':'100', 'sw_type': 'non-edge', 'queue_id': '2',
                            'permissions': '7'}
                    ]
                }
        }
QUEUE_MAX_RATES = {1: 10000000, 2: 1000000}

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

    def __init__(self, num_homes_per_zone, num_isps):    
        self.switch_name_cntr = 0
        self.host_name_cntr = 0

        # Initialize topology
        Topo.__init__( self )

        home_link_config = {}
        isp_link_config = {}
        core_link_config = {}
        home_core_link_config = {}
        home_inside_link_config = {}
        
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

def create_topology():
    topo = HomeAccessTopo(NO_OF_HOMES_PER_AREA, NO_OF_ISPS)
    remote = partial(RemoteController, ip=FLOW_VISOR_IP, port=FLOW_VISOR_PORT)
    net = Mininet(topo=topo, host=CPULimitedHost, link=TCLink, autoSetMacs=True, controller=remote)
    return net

if __name__ == '__main__':
    
    #1. Create mininet topology
    net = create_topology()
    net.start()
    
    # Set IPs
    utils.set_static_ips(SLICES, net)

    #2. Enable STP on the switches
    utils.enable_stp(net.switches)

    edge_result_list = utils.get_edge_ints(net)
    edge_sw_dpids = edge_result_list[0]
    edge_sw_names = edge_result_list[1]
    edge_sw_host_mappings = edge_result_list[2]

    print "edge_sw_dpids"+str(edge_sw_dpids)
    print "edge_sw_dpids"+str(edge_sw_names)

    non_edge_result_list = utils.get_other_ints(net, edge_sw_names)
    non_edge_sw_dpids = non_edge_result_list[0]
    non_edge_sw_names = non_edge_result_list[1]
    
    print "non-edge_sw_dpids"+str(non_edge_sw_dpids)
    print "non-edge_sw_dpids"+str(non_edge_sw_names)

    #3. Create flowspaces.
    flowvisor.add_fv_flows(SLICES, edge_sw_dpids, edge_sw_dpids + non_edge_sw_dpids)
    
    #4. Create QOS
    qos.add_qos_on_non_edge_switch_ifaces(net.switches, MAX_DATARATE_OF_INTERFACE, QUEUE_MAX_RATES)
    CLI(net)
    net.stop()
