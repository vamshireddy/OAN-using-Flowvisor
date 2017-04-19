""" 
    Simple topology for Home Access Network.
"""
import utils
import pprint
import qos
import sys
import flowvisor
from mininet.topo import Topo
from mininet.node import RemoteController
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from functools import partial
from mininet.util import dumpNodeConnections
import time
import os

class SingleSwitchTopo(Topo):
    "Single switch connected to n hosts."
    def build(self, n=2):
        switch = self.addSwitch('s1')
        # Python's range(N) generates 0..N-1
        for h in [2, 3]:
            host = self.addHost('h%s' % (h + 1))
            self.addLink(host, switch)

FLOW_VISOR_IP = "127.0.0.1"
FLOW_VISOR_PORT = 6633
NO_OF_HOMES_PER_AREA = 2
NO_OF_ISPS = 2 
MAX_DATARATE_OF_INTERFACE = 1000 * qos.MB_IN_KB * qos.KB_IN_B
SLICES = {
        'comcast': { 
                    'email' : 'comcast.net', 
                    'ip': 'localhost', 
                    'port' : '11001', 
                    'queue_id' : '1',
                    # These are the hosts that are directly connected to the ISP.
                    'hosts': ['h3', 'h4', 'h9', 'h10', 'h1'],
                    # Static IP mappings.
                    'ip_mappings': {'h3': '10.0.0.3', 'h4': '10.0.0.4','h9': '10.0.0.9','h10': '10.0.0.10','h1': '10.0.0.1'},
                    # These rules are installed on all of the switches.
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
                    # These are the hosts that are directly connected to the ISP.
                    'hosts': ['h5', 'h6', 'h7', 'h8', 'h2'],
                    # Static IP mappings.
                    'ip_mappings': {'h5': '192.168.0.5', 'h6': '192.168.0.6','h7': '192.168.0.7','h8': '192.168.0.8','h2': '192.168.0.2'},
                    # These rules are installed on all of the switches.
                    'rules': 
                    [
                        {'name': 'verizon', 'match_str': 'nw_src=192.168.0.0/24', 'priority':'100', 'sw_type': 'non-edge', 'queue_id': '2',
                        'permissions': '7'}
                    ]
                }
        }


QUEUE_MAX_RATES = {1: 100 * qos.MB_IN_KB * qos.KB_IN_B, 2: 100 * qos.MB_IN_KB * qos.KB_IN_B} #MB

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
    net = Mininet(topo=topo, link=TCLink, autoSetMacs=True, controller=remote)
    return net

def create_1_sw_topology():
    topo = SingleSwitchTopo(n=2)
    remote = partial(RemoteController, ip=FLOW_VISOR_IP, port=FLOW_VISOR_PORT)
    net = Mininet(topo=topo, link=TCLink, autoSetMacs=True, controller=remote)
    return net

def start_ISP_switchover_experiment(net, dirname):
    # Start traffic on h1 and h2. 
    # 10 Mbps constant rate UDP traffic to towards h3, h4, h5, h6
    traffic_rate = "10M" #Mbps
    target_hosts = ['h3', 'h4', 'h5', 'h6']
    
    # Start monitoring the interfaces.
    for host in target_hosts:
        h = net.get(host)
        h.cmd("bwm-ng -t 100 -o csv -u bits -T rate -C ',' > %s &"%(dir_name+"_"+host))
    
    i = 1
    # Wait for sometime.
    for isp in SLICES.keys():
        server = net.get('h%s'%(i))
        hosts = SLICES[isp]['hosts']
        for host in hosts:
            if host in target_hosts:
                print "Starting traffic for "+host
                h = net.get(host)
                h.cmd("iperf -s -u &")
                server.cmd("iperf -c "+net.get(host).IP()+" -u -b "+traffic_rate+" -t 10000 &")
        i+=1
    CLI(net)

    # Wait for sometime.
    print "Sleeping before ISP switch"
    time.sleep(10)

    # Switchover the h5 from ISP 2 to ISP 1.
    node = net.get('h5')
    server = net.get('h2')
    server.cmd("pkill "+node.IP())

    new_ip = "10.0.0.40"
    node.setIP(new_ip)
    print "Changed IP"
    print node.cmd("ifconfig")

    # Start traffic again for this host.
    new_server = net.get('h1')
    new_server.cmd("iperf -c "+node.IP()+" -u -b "+traffic_rate)

    print "Switch done"
    print new_server.cmd("ps aux | grep iperf")
    time.sleep(10)
    print "Experiment done"

def set_bw(self, line):
    "set_bw <sw_name> <sw_name> <bytes> <queue_id>"
    words = line.split(" ")
    if len(words) != 4:
        print 'set_bw <sw_name> <sw_name> <bytes> <queue_id>'
        return
    s1 = words[0]
    s2 = words[1]
    datarate = words[2]
    queue_id = words[3]
    print "Given "+s1+" "+s2+" "+datarate+" "+queue_id
    ifaces = utils.get_ifaces_of_link(self.mn, s1, s2)
    qos.set_data_rate_on_iface_q(ifaces[0], queue_id, datarate)
    qos.set_data_rate_on_iface_q(ifaces[1], queue_id, datarate)
    

if __name__ == '__main__':
    
    flow_visor_config = False
    if len(sys.argv) > 1 and sys.argv[1] == "fv":
        print "Adding flowvisor"
        flow_visor_config = True

    #1. Create mininet topology
    net = create_topology()
    net.start()
    #2. Set IPs
    utils.set_static_ips(SLICES, net)

    #3. Enable STP on the switches to avoid loops.
    utils.enable_stp(net.switches)

    edge_result_list = utils.get_edge_ints(net)
    edge_sw_dpids = edge_result_list[0] # Edge switch data path ids.
    edge_sw_names = edge_result_list[1] # Edge switch names (Ex: s1, s2, etc.)
    edge_sw_host_mappings = edge_result_list[2] # Edge switch host mappings.

    print "edge_sw_dpids"+str(edge_sw_dpids)
    print "edge_sw_dpids"+str(edge_sw_names)

    non_edge_result_list = utils.get_other_ints(net, edge_sw_names)
    non_edge_sw_dpids = non_edge_result_list[0] # Core switch data path ids.
    non_edge_sw_names = non_edge_result_list[1] # Core switch names. 
    
    print "non-edge_sw_dpids"+str(non_edge_sw_dpids)
    print "non-edge_sw_dpids"+str(non_edge_sw_names)

    #3. Create flowspaces on all the switches.
    if flow_visor_config:
        flowvisor.add_fv_flows(FLOW_VISOR_IP, SLICES, edge_sw_dpids + non_edge_sw_dpids)
    
    #4. Create QOS
    qos.add_qos_on_non_edge_switch_ifaces(net.switches, MAX_DATARATE_OF_INTERFACE, QUEUE_MAX_RATES)
    
    CLI.do_set_bw = set_bw

    print "Waiting 60 secs for STP to converge"
    # Sleep for STP
    CLI(net)

    timestamp = time.time()
    dir_name = "tests/switchover1.1-"+str(timestamp)+"/"
    utils.create_folder_if_not_exists(dir_name)
    print "Starting switchover experiment"
    start_ISP_switchover_experiment(net, dir_name)
    net.stop()

