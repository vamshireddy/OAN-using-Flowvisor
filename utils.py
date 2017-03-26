import subprocess
import sys

def enable_stp(switches):
    print "Enabling STP on "+str(switches)
    for switch in switches:
        command = ["ovs-vsctl", "set", "bridge", switch.name, "stp-enable=true"]
        print "Executing: "+str(command)
        process = subprocess.Popen(command)

def get_host_interfaces(hosts):
    all_interfaces = []
    for host in hosts:
        intlist = host.intfList()
        for iface in intlist:
            all_interfaces += [iface.name]
    return all_interfaces

def get_edge_ints(net):
    edge_switches = []
    edge_interfaces = []
    edge_dpids = []
    hosts = net.hosts
    hifaces = get_host_interfaces(hosts)
    switches = net.switches
    # For each switch, get the ports on which the hosts are connected
    for switch in switches:
        swifaces = switch.intfList()
        for iface in swifaces:
            if iface.link:
                host_side_iface = iface.link.intf2
                # Check if this interfaces is connected to a host
                if host_side_iface.name in hifaces:
                    port = switch.ports[iface]
                    switch_name = iface.name.split("-")[0] 
                    switch_dpid = net.get(switch_name).dpid
                    edge_interfaces += [(switch_dpid, port, host_side_iface.name.split("-")[0])]
                    if switch_name not in edge_switches:
                        edge_switches += [switch_name]
                    if switch_dpid not in edge_dpids:
                        edge_dpids += [switch_dpid]
    return edge_dpids, edge_switches, edge_interfaces

def get_other_ints(net, edge_switches):
    switches = net.switches
    other_switches = []
    other_dpids = []
    for i in switches:
        if i.name not in edge_switches:
            other_switches += [i.name]
            other_dpids += [i.dpid]
    return other_dpids, other_switches

def get_host_owner(h, slices):
    for s in slices:
        isp = slices[s]
        if h in isp['hosts']:
            return s

def fill_edge_rules(slices, edge_sw_bindings, permissions, priority):
    for rule in edge_sw_bindings:
        port = rule[1]
        host_name = rule[2]
        switch_dpid = rule[0]
        isp_name = get_host_owner(host_name, slices)
        print isp_name
        isp_slice = slices[isp_name]
        queue = isp_slice['queue_id']
        isp_slice['rules'] += [{'name': isp_name, 'match_str': 'in_port=%s'%(port), 'priority':priority, 'sw_type': 'edge', 
            'queue_id': queue, 'permissions': permissions, 'sw_dpid':switch_dpid}]

def lookup_ip(host_name, slices):
    for s in slices:
        isp = slices[s]
        if host_name in isp['ip_mappings']:
            return isp['ip_mappings'][host_name]

def set_static_ips(slices, net):
    for host in net.hosts:
        print "Setting "+lookup_ip(host.name, slices)+" for "+host.name
        host.setIP(lookup_ip(host.name, slices))
