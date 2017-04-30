# Run with sudo.
cd ../../
git clone git://github.com/mininet/mininet
cd mininet
git tag  # list available versions
git checkout -b 2.2.1  # or whatever version you wish to install
cd ..
mininet/util/install.sh -a
wget http://updates.onlab.us/GPG-KEY-ONLAB
sudo apt-key add GPG-KEY-ONLAB
sudo sed -i '1s/^/deb http:\/\/updates.onlab.us\/debian stable\/\n/' /etc/apt/sources.list
sudo apt-get update && sudo apt-get -y install flowvisor
sudo apt-get -y install python-matplotlib
sudo apt-get -y install bwm-ng
echo "To run OVSDB on TCP port, do the following."
echo "1. Edit /usr/share/openvswitch/scripts/ovs-ctl"
echo "2. Under #Start ovsdb-server add a line:"
echo "set \"$@\" --remote=ptcp:6632"
echo "3. Then restart ovs"
echo "sudo service openvswitch-switch restart"
