import subprocess
import sys
import time

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

def clean_flowvisor_config(host_ip):
    command = ['fvctl', '-h', host_ip ,'-f', '/dev/null', 'remove-flowspace', 'isp1'];
    process = subprocess.Popen(command)
    command = ['fvctl', '-h', host_ip ,'-f', '/dev/null', 'remove-flowspace', 'isp2'];
    process = subprocess.Popen(command)

def create_slice(host_ip, slice_name, email, ip, port):
    command = ['fvctl', '-h', host_ip ,'-f', '/dev/null', 'add-slice', slice_name, 'tcp:%s:%s'%(ip, port), email]
    print "slice: "+" ".join(command)
    process = subprocess.Popen(command,stdout=subprocess.PIPE)

def enable_stp(switches):
    print "Enabling STP on "+str(switches)
    for i in switches:
        command = ["ovs-vsctl", "set", "bridge", i, "stp-enable=true"]
        process = subprocess.Popen(command)

def create_fv_flow(host_ip, switch_dpid, slice_name, queue, match_str, priority, permissions):
    command = ['fvctl', '-h', host_ip ,'-f', '/dev/null',
                'add-flowspace', '%s'%(slice_name),
                '%s'%switch_dpid,
                '%s'%priority,
                '%s'%(match_str),
                '%s=%s'%(slice_name, permissions),
                '-q', '%s'%queue, 
                '-f', '%s'%queue]
    print command
    print "fs: "+" ".join(command)
    process = subprocess.Popen(command)
    time.sleep(1)

"""     
    Add flowvisor flowspace rules.
    fvslices: description of slices.
    switch_dpids: dpids of all the switches.
"""
def add_fv_flows(host_ip, fvslices, switch_dpids):
    for slicename in fvslices:
        fvslice = fvslices[slicename]
        # Install flow rules on the switches
        for sdpid in switch_dpids:
            rules = fvslice['rules']
            for rule in rules:
                if rule['sw_type'] == 'non-edge':
                    print "Intalling non-edge rule on "+str(sdpid)
                    create_fv_flow(host_ip, sdpid, slicename, rule['queue_id'], rule['match_str'], rule['priority'], rule['permissions'])
