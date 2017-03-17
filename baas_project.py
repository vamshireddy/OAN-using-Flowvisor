"""Custom topology example

Two directly connected switches plus a host for each switch:

   host --- switch --- switch --- host

Adding the 'topos' dict with a key/value pair to generate our newly defined
topology enables one to pass in '--topo=mytopo' from the command line.
"""

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.node import CPULimitedHost
from mininet.link import TCLink

class MyTopo( Topo ):
    "Simple topology example."

    def __init__( self, num_homes_per_zone, num_isps):
        "Create custom topo."

        # Initialize topology
        Topo.__init__( self )

        home_link_config = {'bw': 25, 'delay' :'5ms', 'loss' : 2, 
                'max_queue_size' : 1000, 'use_htb' : True}
        isp_link_config = {'bw': 200, 'delay' :'5ms', 'loss' : 2, 
                'max_queue_size' : 1000, 'use_htb' : True}
        core_link_config = {'bw': 100, 'delay' :'5ms', 'loss' : 2, 
                'max_queue_size' : 1000, 'use_htb' : True}
        home_core_link_config = {'bw': 50, 'delay' :'5ms', 'loss' : 2, 
                'max_queue_size' : 1000, 'use_htb' : True}


        #create isps and connect to core switch
        core1 = self.addSwitch('core1')
        for i in range(num_isps):
            isp = self.addHost('H%s' % (i + 1))
            self.addLink( core1, isp, **isp_link_config )

        
        #Create home switches for zone A
        aggrSw1 = self.addSwitch('aggrSw1')
        for i in range(num_homes_per_zone):
            home_switch = self.addSwitch('A%s' % (i + 1))
            self.addLink( aggrSw1, home_switch, **home_link_config)

        #Create home switches for zone B
        aggrSw2 = self.addSwitch('aggrSw2')
        for i in range(num_homes_per_zone):
            home_switch = self.addSwitch('B%s' % (i + 1))
            self.addLink( aggrSw2, home_switch, **home_link_config )

        #Connect zone A and Zone B to core switch
        core2 = self.addSwitch('core2')
        self.addLink( core2, aggrSw1, **home_core_link_config )
        self.addLink( core2, aggrSw2, **home_core_link_config )

        #Create home switches for zone C
        aggrSw3 = self.addSwitch('aggrSw3')
        for i in range(num_homes_per_zone):
            home_switch = self.addSwitch('C%s' % (i + 1))
            self.addLink( aggrSw3, home_switch, **home_link_config)

        #Create home switches for zone D
        aggrSw4 = self.addSwitch('aggrSw4')
        for i in range(num_homes_per_zone):
            home_switch = self.addSwitch('D%s' % (i + 1))
            self.addLink( aggrSw4, home_switch, **home_link_config)

        #Connect zone C and Zone D to core switch
        core3 = self.addSwitch('core3')
        self.addLink( core3, aggrSw3, **home_core_link_config )
        self.addLink( core3, aggrSw4, **home_core_link_config )

        #connect the cores
        self.addLink( core1, core2, **core_link_config )
        self.addLink( core2, core3, **core_link_config )
        self.addLink( core3, core1, **core_link_config )            

mytopo = MyTopo(2, 2)
#topos = { 'mytopo': ( lambda: MyTopo(2, 2) ) }
net = Mininet( topo=mytopo, host=CPULimitedHost, link=TCLink)
net.start()
CLI( net )
net.stop()
