# BaaS
BaaS For Access Networks

### Dependencies
1. Flowvisor
2. Mininet
3. bwm-ng
4. POX
5. OVS (Also, run the openvswitch server on TCP - Used for JSON RPCs)
7. Matplotlib - python

### Common problems and their solutions
* While adding new flow rules, if `list-flowspaces` shows only two entries, then delete /etc/flowvisor/config.json and regenerate it.

### Commands
#### 1. FlowVisor
Start flowvisor and initialize the Database.

`sudo -u flowvisor fvconfig generate /etc/flowvisor/config.json`

`sudo /etc/init.d/flowvisor start`

`fvctl -f /dev/null set-config --enable-topo-ctrl`

`sudo /etc/init.d/flowvisor restart`

ensure that FlowVisor is running by getting its configuration:
`fvctl -f /dev/null get-config`

#### 3. Create slices for ISP1 and ISP2
`fvctl -f /dev/null add-slice isp1 tcp:localhost:11001 abc@abc`
`fvctl -f /dev/null add-slice isp2 tcp:localhost:11002 abc@abc`

Check if the slices are created.
`fvctl -f /dev/null list-slices`

#### 4. Run the ISP controllers
* Copy the `isp1_controller` and `isp1_controller` to `~/pox/pox/forwarding`
* Run these commands in ~/pox/ directory in a seperate terminals.sfaf
`./pox.py samples.pretty_log log.level --DEBUG openflow.of_01 --port=11001 openflow.spanning_tree --no-flood --hold-down forwarding.isp1_controller`
`./pox.py samples.pretty_log log.level --DEBUG openflow.of_01 --port=11002 openflow.spanning_tree --no-flood --hold-down forwarding.isp2_controller`

#### 3. Start Mininet script 

* if running for the first time `sudo python simple_home_access.py fv`
* else `sudo python simple_home_access.py`

#### 4. Now if you want to set bandwidth to a link between two switches a, b for a slice.
`mininet> set_bw s1 s2 <bandwidth in bytes> <queue_id_of_the_slice>
