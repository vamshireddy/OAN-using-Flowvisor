sudo -u flowvisor fvconfig generate /etc/flowvisor/config.json
sudo /etc/init.d/flowvisor start
sleep 5
fvctl -f /dev/null set-config --enable-topo-ctrl
sudo /etc/init.d/flowvisor restart
sleep 10
fvctl -f /dev/null get-config
fvctl -f /dev/null add-slice comcast tcp:localhost:11001 comcast@comcast
fvctl -f /dev/null add-slice verizon tcp:localhost:11002 verizon@verizon
