sudo mn -c
fvctl -f /dev/null remove-flowspace comcast
fvctl -f /dev/null remove-flowspace verizon
sudo ovs-vsctl --all destroy queue
sudo ovs-vsctl --all destroy qos

