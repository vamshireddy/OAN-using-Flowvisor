export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8
python plot_rate.py --rx \
        --title $4 \
        --legend $6 $7\
        --maxy $5 \
        --xlabel 'Time (s)' \
        --ylabel 'Throughput (Mbps)' \
        -i 'h.*-eth0' \
        -f $1 $2 \
        -o $3
