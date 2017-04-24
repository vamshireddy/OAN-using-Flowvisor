iperf -c $1 -u -b $2 -t 10000 > /dev/null &
IPERF_PID=$!
echo $IPERF_PID
