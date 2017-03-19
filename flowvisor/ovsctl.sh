ovs-vsctl set port $1 qos=@newqos -- \
  --id=@newqos create qos type=linux-htb \
      other-config:max-rate=100000000 \
      queues:1=@queue1 \
      queues:2=@queue2 -- \
  --id=@queue1 create queue other-config:max-rate=$2 -- \
  --id=@queue2 create queue other-config:max-rate=$3
