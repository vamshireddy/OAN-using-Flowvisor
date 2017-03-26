import subprocess
import sys

def add_qos_on_non_edge_switch_ifaces(switches, max_rate_of_interface, qmaxrates):
    for switch in switches:
        for iface in switch.intfList():
            if iface.name == "lo":
                continue
            add_qos_on_iface(iface.name, max_rate_of_interface, len(qmaxrates), qmaxrates)

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
