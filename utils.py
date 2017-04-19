import subprocess
import sys
import os

def create_folder_if_not_exists(directory):
    print "Creating folder "+str(directory)
    if not os.path.exists(directory):
        os.makedirs(directory)

def clean_up_ovs_config():
    commands += ["sudo ovs-vsctl --all destroy queue"]
    commands += ["sudo ovs-vsctl --all destroy qos"]
    for i in commands:
        print "Executing" + str(i.split(" "))
        process = subprocess.Popen(i.split(" "))

def clean_up_config(fv_host, slices):
    commands = []
    for i in slices:
        commands += ["fvctl -h "+fv_host+" -f /dev/null remove-flowspace "+i]
    commands += ["sudo ovs-vsctl --all destroy queue"]
    commands += ["sudo ovs-vsctl --all destroy qos"]

    for i in commands:
        print "Executing" + str(i.split(" "))
        process = subprocess.Popen(i.split(" "))

def enable_stp(switches):
    for switch in switches:
        command = ["ovs-vsctl", "set", "bridge", switch.name, "stp-enable=true"]
        process = subprocess.Popen(command)

def get_host_interfaces(hosts):
    all_interfaces = []
    for host in hosts:
        intlist = host.intfList()
        for iface in intlist:
            all_interfaces += [iface.name]
    return all_interfaces

"""
    Get edge switch details.
    Returns 3 lists.
    List1: Contains edge switch dpids.
    List2: Contains edge switch names.
    List3: Contains edge interface tuples (<switch_dpid>, <port_on_the_switch>, <host_name_connected_to_the_port>)
"""
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
        print "Assigned "+lookup_ip(host.name, slices)+" for "+host.name
        host.setIP(lookup_ip(host.name, slices))

def get_ifaces_of_link(net, switch1, switch2):
    s1 = net.getNodeByName(switch1)
    s2 = net.getNodeByName(switch2)
    s1_ifaces = s1.intfList()
    s2_ifaces = s2.intfList()
    for iface in s1_ifaces:
        if iface.link:
            print iface.link.intf1.name, iface.link.intf2.name
            this_switch = iface.link.intf1.name.split("-")[0]
            other_switch = iface.link.intf2.name.split("-")[0]
            if this_switch == switch2 or other_switch == switch2:
                    return (iface.link.intf1.name, iface.link.intf2.name)
    return None
