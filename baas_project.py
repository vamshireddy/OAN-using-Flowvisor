""" Simple topology for Home Access Network.
"""
from mininet.topo import Topo
from mininet.node import RemoteController
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from functools import partial

class MyTopo( Topo ):

    def __init__( self, num_homes_per_zone, num_isps):
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
        home_inside_link_config = {'bw': 50, 'delay' :'5ms', 'loss' : 2, 
				'max_queue_size' : 1000, 'use_htb' : True}
        switch_cnt = 1
        #create isps and connect to core switch
        core1 = self.addSwitch('core-sw1', dpid="%d" % (switch_cnt))
        
        for i in range(num_isps):
            isp = self.addHost('coreH%s' % (i + 1))
            self.addLink( core1, isp, **isp_link_config )
        
        #Create home switches for zone A
        aggrSw1 = self.addSwitch('aggr-sw1', dpid="%d" % (switch_cnt))
        for i in range(num_homes_per_zone):
            switch_cnt += 1
            home_switch = self.addSwitch('hm-swA-%s' % (i + 1), dpid="%d" % (switch_cnt))
            self.addLink( aggrSw1, home_switch, **home_link_config)
            home_host = self.addHost('hostA%s' % (i + 1))
            self.addLink( home_switch, home_host, **home_inside_link_config )
   
        #Create home switches for zone B
        switch_cnt += 1
        aggrSw2 = self.addSwitch('aggr-sw2', dpid="%d" % (switch_cnt))
        for i in range(num_homes_per_zone):
            switch_cnt += 1
            home_switch = self.addSwitch('hm-swB-%s' % (i + 1), dpid="%d" % (switch_cnt))
            self.addLink( aggrSw2, home_switch, **home_link_config )
            home_host = self.addHost('hostB%s' % (i + 1))
            self.addLink( home_switch, home_host, **home_inside_link_config )
        
        #Connect zone A and Zone B to core switch
        switch_cnt += 1
        core2 = self.addSwitch('core-sw2', dpid="%d" % (switch_cnt))
        
        self.addLink( core2, aggrSw1, **home_core_link_config )
        self.addLink( core2, aggrSw2, **home_core_link_config )

        #Create home switches for zone C
        switch_cnt += 1
        aggrSw3 = self.addSwitch('aggr-sw3', dpid="%d" % (switch_cnt))
        for i in range(num_homes_per_zone):
            switch_cnt += 1
            home_switch = self.addSwitch('hm-swC-%s' % (i + 1), dpid="%d" % (switch_cnt))
            self.addLink( aggrSw3, home_switch, **home_link_config)
            home_host = self.addHost('hostC%s' % (i + 1))
            self.addLink( home_switch, home_host, **home_inside_link_config )

        #Create home switches for zone D
        switch_cnt += 1
        aggrSw4 = self.addSwitch('aggr-sw4', dpid="%d" % (switch_cnt))
        for i in range(num_homes_per_zone):
            switch_cnt += 1
            home_switch = self.addSwitch('hm-swD-%s' % (i + 1), dpid="%d" % (switch_cnt))
            self.addLink( aggrSw4, home_switch, **home_link_config)
            home_host = self.addHost('hostD%s' % (i + 1))
            self.addLink( home_switch, home_host, **home_inside_link_config )

        #Connect zone C and Zone D to core switch
        switch_cnt += 1
        core3 = self.addSwitch('core-sw3', dpid="%d" % (switch_cnt))
        self.addLink( core3, aggrSw3, **home_core_link_config )
        self.addLink( core3, aggrSw4, **home_core_link_config )
        
        #connect the cores
        self.addLink( core1, core2, **core_link_config )
        self.addLink( core2, core3, **core_link_config )
        self.addLink( core3, core1, **core_link_config )            

topos = { 'fvtopo': ( lambda: MyTopo(2, 2) ) }
