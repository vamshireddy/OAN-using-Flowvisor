import subprocess
import sys

def find_sw_ifs():
    command1 = ['ovs-vsctl', 'list', 'port']
    process1 = subprocess.Popen(command1,stdout=subprocess.PIPE)
    
    command2 = ['grep', 'name']
    process2 = subprocess.Popen(command2,stdin=process1.stdout,stdout=subprocess.PIPE)
    
    command3 = ['grep', 'eth']
    process3 = subprocess.Popen(command3,stdin=process2.stdout,stdout=subprocess.PIPE)

    command4 = ['awk', '{print $3}']
    process4 = subprocess.Popen(command4,stdin=process3.stdout,stdout=subprocess.PIPE)
    (out,err) = process4.communicate()
    
    l = out.split("\n")
    res = []
    for i in l:
        if i == "":
            continue
        res.append(i.strip("\""))
    return res

def find_switches():
    command1 = ['fvctl', '-f', '/dev/null', 'list-datapaths']
    process1 = subprocess.Popen(command1,stdout=subprocess.PIPE)
    (out,err) = process1.communicate()

    res = []
    lines = out.split("\n")[1:-1]
    for line in lines:
        res.append(line.split(":")[0].strip())
    return res

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

def clean_flowvisor_config():
    command = ['fvctl', '-f', '/dev/null', 'remove-flowspace', 'isp1'];
    process = subprocess.Popen(command)
    command = ['fvctl', '-f', '/dev/null', 'remove-flowspace', 'isp2'];
    process = subprocess.Popen(command)

def create_slice(slice_name, email, ip, port):
    command = ['fvctl', '-f', '/dev/null', 'add-slice', slice_name, 'tcp:%s:%s'%(ip, port), email]
    print "slice: "+" ".join(command)
    process = subprocess.Popen(command,stdout=subprocess.PIPE)

def enable_stp(switches):
    print "Enabling STP on "+str(switches)
    for i in switches:
        command = ["ovs-vsctl", "set", "bridge", i, "stp-enable=true"]
        process = subprocess.Popen(command)

def create_fv_flow(switch_dpid, slice_name, queue, match_str, priority, permissions):
    command = ['fvctl', '-f', '/dev/null',
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

def add_fv_flows(fvslices, edge_switch_dpids, switch_dpids):
    for slicename in fvslices:
        fvslice = fvslices[slicename]
        for sdpid in switch_dpids:
            rules = fvslice['rules']
            for rule in rules:
                if rule['sw_type'] == 'non-edge':
                    print "Intalling non-edge rule on "+str(sdpid)
                    create_fv_flow(sdpid, slicename, rule['queue_id'], rule['match_str'], rule['priority'], rule['permissions'])
        for sdpid in edge_switch_dpids:
            rules = fvslice['rules']
            for rule in rules:
                if rule['sw_type'] == 'edge' and rule['sw_dpid'] == sdpid :
                    print "Intalling edge rule on "+str(sdpid)
                    create_fv_flow(sdpid, slicename, rule['queue_id'], rule['match_str'], rule['priority'], rule['permissions'])
