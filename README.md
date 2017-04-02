# BaaS
BaaS For Access Networks

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

#### 3. Start Mininet
`sudo python simple_home_access.py`
