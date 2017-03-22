# BaaS
BaaS For Access Networks

### Commands
#### 1. Run mininet
`sudo mn --custom <script_name> --topo <topo_name> --link tc --controller remote --mac --arp`
for running baas script
`sudo mn --custom baas_project.py --topo fvtopo --link tc --controller remote --mac --arp`

#### 2. FlowVisor
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

#### 4. Run the flowvisor configuration script.

Goto `flowvisor` directory and run `add_config.py`
This script adds queues on every switch port. 

`sudo python add_config.py`

For cleaning up (not required here)
`sudo python add_config.py clean`

#### 5. Setup STP on the switches

`sudo python add_config.py enablestp`



