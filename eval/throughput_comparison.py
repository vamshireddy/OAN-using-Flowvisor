import numpy as np
import matplotlib.pyplot as plt
 
# data to plot
n_groups = 7
means_frank = (97.2, 183, 269, 338, 422, 502, 556)
means_guido = (94.7, 176, 252, 336, 418, 511, 652)
 
# create plot
fig, ax = plt.subplots()
index = np.arange(n_groups)
bar_width = 0.35
opacity = 0.8
 
rects1 = plt.bar(index, means_frank, bar_width,
                 alpha=opacity,
                 color='b',
                 label='Dedicated Links')
 
rects2 = plt.bar(index + bar_width, means_guido, bar_width,
                 alpha=opacity,
                 color='g',
                 label='Network Slice')
 
plt.xlabel('Link/Slice Bandwidth in Mb/sec')
plt.ylabel('Latency in seconds')
plt.title('Throughput seen on dedicated links')
plt.xticks(index + bar_width, ('100', '200', '300', '400', '500', '600', '700'))
plt.legend()
 
plt.tight_layout()
plt.show()
