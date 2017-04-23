import time
import subprocess
import socket
import json
import sys
import pprint

MB_IN_KB = 1000
KB_IN_B = 1000

"""
To run OVSDB on TCP port, do the following.
1. Edit /usr/share/openvswitch/scripts/ovs-ctl
2. Under #Start ovsdb-server add a line:
    set "$@" --remote=ptcp:6632
3. Then restart ovs
    sudo service openvswitch-switch restart
"""

OVSDB_IP = '127.0.0.1'
OVSDB_PORT = 6632

list_ports_param = ["Open_vSwitch","",{"Port":{"columns":["bond_downdelay","bond_fake_iface","bond_mode","bond_updelay","external_ids","fake_bridge","interfaces","lacp","mac","name","other_config","qos","statistics","status","tag","trunks","vlan_mode"]},"QoS":{"columns":[]},"Interface":{"columns":[]},"Open_vSwitch":{"columns":["cur_cfg"]}}]

#list_qos_param = ["Open_vSwitch","",{"Port":{"columns":[]},"QoS":{"columns":["external_ids","other_config","queues","type"]},"Queue":{"columns":[]},"Open_vSwitch":{"columns":["cur_cfg"]}}]

list_qos_param = ["Open_vSwitch","",{"Port":{},"QoS":{"columns":["queues","type"]},"Queue":{},"Open_vSwitch":{"columns":["cur_cfg"]}}]

list_queue_param = ["Open_vSwitch","", {"Open_vSwitch":{"columns":["cur_cfg"]},"Queue":{"columns":["dscp","external_ids","other_config"]}}] 

def add_qos_on_non_edge_switch_ifaces(switches, max_rate_of_interface, qmaxrates):
    for switch in switches:
        for iface in switch.intfList():
            if iface.name == "lo":
                continue
            add_qos_on_iface(iface.name, max_rate_of_interface, len(qmaxrates), qmaxrates)
            time.sleep(0.5)

def add_qos_on_iface(iface, max_rate, queue_count, qmaxrates):
    command = ['ovs-vsctl', 'set', 'port', iface]
    command1 = command + ['qos=@newqos']
    command1.append('--')
    command2 = command1 + ['--id=@newqos', 'create',
        'qos', 'type=linux-htb', 'other-config:max-rate=%s'%max_rate]
    for i in range(1, queue_count+1):
        command2.append('queues:%s=@queue%s'%(i, i))

    for i in range(1, queue_count+1):
        command2.append("--")
        command2 += ['--id=@queue%s'%i, 'create', 'queue', 'other-config:max-rate=%s'%qmaxrates[i]]
    print "Executing command\n"+" ".join(command2)
    process = subprocess.Popen(command2,stdout=subprocess.PIPE)

def clean_qos_config():
    command = ['ovs-vsctl', '--all', 'destroy', 'queue']
    process = subprocess.Popen(command)
    command = ['ovs-vsctl', '--all', 'destroy', 'qos']
    process = subprocess.Popen(command)

def list_ports():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((OVSDB_IP, OVSDB_PORT))
    list_dbs_query =  {"method":"monitor", "params":list_ports_param, "id": 0}
    sock.send(json.dumps(list_dbs_query))
    response = sock.recv(40096*1024)
    sock.close()
    return response

def list_qos():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((OVSDB_IP, OVSDB_PORT))
    list_dbs_query =  {"method":"monitor", "params":list_qos_param, "id": 0}
    sock.send(json.dumps(list_dbs_query))
    response = sock.recv(40096*1024)
    sock.close()
    return response

def list_queues():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((OVSDB_IP, OVSDB_PORT))
    list_dbs_query =  {"method":"monitor", "params":list_queue_param, "id": 0}
    sock.send(json.dumps(list_dbs_query))
    response = sock.recv(40096*1024)
    sock.close()
    return response

def get_qos_of_iface(ifacename):
    port_str = list_ports()
    if port_str == "":
        print "Cannot perform JSON query!"
        return None
    ports_json = json.loads(port_str)
    ports_parsed = ports_json["result"]["Port"]
    qos_id = 0
    for key in ports_parsed.keys():
        if ports_parsed[key]["new"]["name"] == ifacename:
            return ports_parsed[key]["new"]["qos"][1]
    return None

def get_queue_id_of_qos(qos, queue_number):
    ports_json = json.loads(list_qos())
    qos_parsed = ports_json["result"]["QoS"]
    if qos in qos_parsed.keys():
        queue_map = qos_parsed[qos]['new']['queues'][1:][0]
        for queue in queue_map:
            if str(queue_number) == str(queue[0]):
                return queue[1][1]
    return None

def set_data_rate_on_iface_q(iface, queue_number, data_rate):
    data_rate = str(data_rate)
    queue_number = str(queue_number)
    print "Setting data rate: "+str(iface)+" queue: "+str(queue_number)+" Datarate: "+str(data_rate)
    qos = get_qos_of_iface(iface)
    print "QOS:"+str(qos)
    if qos:
        queue_id = get_queue_id_of_qos(qos, queue_number)
        print "Queue:"+str(queue_id)
        if queue_id:
            command = ("sudo ovs-vsctl set queue %s other_config={max-rate=%s}"%(queue_id, data_rate)).split(" ")
            process = subprocess.Popen(command,stdout=subprocess.PIPE)
        else:
            print "Cannot find a link"

