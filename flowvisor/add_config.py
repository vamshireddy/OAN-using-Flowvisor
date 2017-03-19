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
    process = subprocess.Popen(command,stdout=subprocess.PIPE)
    command = ['ovs-vsctl', '--all', 'destroy', 'qos']
    process = subprocess.Popen(command,stdout=subprocess.PIPE)

def create_slice(slice_name, email, ip, port):
    command = ['fvctl', '-f', '/dev/null', 'add-slice', slice_name, 'tcp:%s:%s'%(ip, port), email]
    print "slice: "+" ".join(command)
    process = subprocess.Popen(command,stdout=subprocess.PIPE)

def create_flowspace(slice_queues, switch_dpid, slice_name, ip, prefix, priority):
    command = ['fvctl', '-f', '/dev/null',
                'add-flowspace', '%s%s%s'%(slice_name, ip, prefix),
                '%s'%switch_dpid,
                '%s'%priority,
                'nw_src=%s/%s'%(ip, prefix),
                '%s=7'%(slice_name),
                '-q', '%s'%slice_queues[slice_name], 
                '-f', '%s'%slice_queues[slice_name]]
    print command
    print "fs: "+" ".join(command)
    process = subprocess.Popen(command)

interfaces = find_sw_ifs()
switches = find_switches()

qmaxrates = {1: 1000000, 2: 200}
slice_queues = {'isp1': 1, 'isp2': 2}
slices = {
        'isp1': { 
                    'email' : 'vamshi@slice', 
                    'ip': 'localhost', 
                    'port' : '11001', 
                    'ipmatch': '10.0.0.0',
                    'ipnm': '24'
                }, 
        'isp2': { 
                    'email' : 'prashasthi@slice', 
                    'ip' : 'localhost', 
                    'port' : '11002', 
                    'ipmatch': '192.168.0.0', 
                    'ipnm': '24'
                }
        }
max_rate = 1000000000

if len(sys.argv) > 1:
    if sys.argv[1] == "clean":
        clean_qos_config()
        sys.exit(0)

# Add queues for all the interfaces in the switch.
for iface in interfaces:
    add_qos_on_iface(iface, max_rate, len(qmaxrates), qmaxrates)

# Create slices
for s in slices:
    dic = slices[s]
    # Create flowspaces
    for sdpid in switches:
        create_flowspace(slice_queues, sdpid, s, dic['ipmatch'], dic['ipnm'], 100)
