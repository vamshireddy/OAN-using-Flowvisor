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

TIME_BEFORE_SWITCHOVER = 30
TIME_AFTER_SWITCHOVER = 30

"""
Test 1.2, 1.3, 1.4: Switchover all the nodes in a zone
"""
def perform_switchover(net, dir_name, HOME_LINK_SLICE_BW, switching_nodes):
    # Start traffic on h1 and h2. 
    # 10 Mbps constant rate UDP traffic to towards h3, h4, h5, h6
    traffic_rate = HOME_LINK_SLICE_BW / (qos.MB_IN_KB * qos.KB_IN_B) #Mbps
    target_hosts = ['h3', 'h4', 'h5', 'h6', 'h7', 'h8', 'h9', 'h10'] # Hosts in Zone 1 and Zone 2
    comcast_hosts = ['h3', 'h5', 'h7', 'h9']
    verizon_hosts = ['h4', 'h6', 'h8', 'h10']
    comcast_ixp = net.get('h1')
    verizon_ixp = net.get('h2')
    new_isp = verizon_ixp # After switchover ISP
    old_isp = comcast_ixp # Before switch.
    kill_pids = {}
    kill_server_pids = {}

    # Start monitoring the interfaces of all hosts
    for host in target_hosts:
        h = net.get(host)
        print "Starting bwm on "+host
        h.cmd("bwm-ng -t 100 -o csv -u bits -T rate -C ',' > %s &"%(dir_name+host))
    
    # Start UDP traffic towards the comcast hosts. 
    for h in comcast_hosts:
        host = net.get(h)
        print "Starting traffic for "+h
        serverout = host.cmd("sh iperf_server.sh")
        out = comcast_ixp.cmd("sh iperf_client.sh %s %s"%(str(host.IP()), str(traffic_rate)+"M"))
        if h in switching_nodes.keys():
            kill_pids[h] = out
            kill_server_pids[h] = serverout
            print "KILL "+h+": "+kill_pids[h]+" "+kill_server_pids[h]
    # Start traffic towards the comcast hosts. 
    for h in verizon_hosts:
        host = net.get(h)
        print "Starting traffic for "+h
        serverout = host.cmd("sh iperf_server.sh")
        out = verizon_ixp.cmd("sh iperf_client.sh %s %s"%(str(host.IP()), str(traffic_rate)+"M"))
        if h in switching_nodes.keys():
            kill_pids[h] = out
            kill_server_pids[h] = serverout
            print "KILL "+h+": "+kill_pids[h]+" "+kill_server_pids[h]

    # Wait for sometime.
    print "Sleeping before ISP switch. Switch happens at 20th second."
    time.sleep(TIME_BEFORE_SWITCHOVER)
    
    for n in switching_nodes.keys():
        swnode = net.get(n)
        swnode.cmd("kill -9 %s"%(kill_server_pids[n]))
        old_isp.cmd("kill -9 %s"%(kill_pids[n]))
        swnode.cmd("ifconfig %s-eth0 %s"%(n, switching_nodes[n]))
        # Start traffic again for this host.
        time.sleep(0.2)
        swnode.cmd("sh iperf_server.sh")
        time.sleep(0.2)
        new_isp.cmd("sh iperf_client.sh %s %s"%(switching_nodes[n], str(traffic_rate)+"M"))

    print swnode.cmd("ps aux | grep iperf")

    print "Switch done. Waiting.."
    time.sleep(TIME_AFTER_SWITCHOVER)
    print "Experiment done"
    for i in range(len(target_hosts)):
        if i%2 != 0:
            continue
        infile1 = dir_name+target_hosts[i]
        infile2 = dir_name+target_hosts[i+1]
        outfile = dir_name+target_hosts[i]+"_"+target_hosts[i+1]
        title = "Throughput-when-h3-switches-ISP"
        utils.plot_two_graphs(infile1, infile2, outfile, title, str(int(traffic_rate)+10), target_hosts[i], target_hosts[i+1])

"""
Test 1.1: Switchover one node in a zone
This function is specifically tied to this topology. 
"""
def start_ISP_switchover_expt_within_zone(net, dir_name, HOME_LINK_SLICE_BW):
    
    # Start traffic on h1 and h2. 
    # 10 Mbps constant rate UDP traffic to towards h3, h4, h5, h6
    
    traffic_rate = HOME_LINK_SLICE_BW / (qos.MB_IN_KB * qos.KB_IN_B) #Mbps
    target_hosts = ['h3', 'h4', 'h5', 'h6', 'h7', 'h8', 'h9', 'h10'] # Hosts in Zone 1 and Zone 2
    comcast_hosts = ['h3', 'h5', 'h7', 'h9']
    verizon_hosts = ['h4', 'h6', 'h8', 'h10']
    switching_node = 'h3'
    comcast_ixp = net.get('h1')
    verizon_ixp = net.get('h2')
    new_isp = verizon_ixp # After witchover ISP
    old_isp = comcast_ixp # Before switch.
    new_ip = "192.168.0.40"
    kill_pid = 0

    # Start monitoring the interfaces.
    for host in target_hosts:
        h = net.get(host)
        print "Starting bwm on "+host
        h.cmd("bwm-ng -t 100 -o csv -u bits -T rate -C ',' > %s &"%(dir_name+host))
    
    # Start traffic towards the comcast hosts. 
    for h in comcast_hosts:
        host = net.get(h)
        print "Starting traffic for "+h
        host.cmd("iperf -s -u &")
        out = comcast_ixp.cmd("sh iperf_client.sh %s %s"%(str(host.IP()), str(traffic_rate)+"M"))
        if h == switching_node:
            kill_pid = out
            print "KILL: "+kill_pid
    # Start traffic towards the comcast hosts. 
    for h in verizon_hosts:
        host = net.get(h)
        print "Starting traffic for "+h
        host.cmd("iperf -s -u &")
        out = verizon_ixp.cmd("sh iperf_client.sh %s %s"%(str(host.IP()), str(traffic_rate)+"M"))

    # Wait for sometime.
    print "Sleeping before ISP switch. Switch happens at 20th second."
    time.sleep(TIME_BEFORE_SWITCHOVER)

    swnode = net.get(switching_node)
    old_isp.cmd("kill -9 %s"%(kill_pid))
    swnode.setIP(new_ip)
    print "Changed IP"

    # Start traffic again for this host.
    new_isp.cmd("sh iperf_client.sh %s %s"%(new_ip, str(traffic_rate)+"M"))

    print "Switch done. Waiting.."
    time.sleep(TIME_AFTER_SWITCHOVER)
    print "Experiment done"

    print "Plotting graphs"
    utils.plot_two_graphs(dir_name+"h3", dir_name+"h4", dir_name+"h3_h4.png", "Throughput-when-h3-switches-ISP", traffic_rate, "h3", "h4")
    utils.plot_two_graphs(dir_name+"h5", dir_name+"h6", dir_name+"h5_h6.png", "Throughput-when-h3-switches-ISP", traffic_rate, "h5", "h6")
    utils.plot_two_graphs(dir_name+"h7", dir_name+"h8", dir_name+"h7_h8.png", "Throughput-when-h3-switches-ISP", traffic_rate, "h7", "h8")
    utils.plot_two_graphs(dir_name+"h9", dir_name+"h10", dir_name+"h9_h10.png", "Throughput-when-h3-switches-ISP", traffic_rate, "h9", "h10")
