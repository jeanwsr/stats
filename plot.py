#!/usr/bin/env python

import matplotlib.pyplot as plt
import sys
import numpy as np

datafile = sys.argv[1]
f = open(datafile, 'r')

x = []
y = []
while(True):
    line = f.readline()
    if line[:3] == 'sub':
        f.readline()
        while(True):
            line = f.readline()
            if line[0].isdigit():
                print(line)
                raw = line.split()
                print(raw)
                data = [float(k) for k in raw]
                x.append(data[0])
                y.append([data[1], data[2], data[3], data[4], data[5]])
            else:
                break
        break
f.close()

x = np.array(x)
y = np.array(y)

plt.plot(x, y[:,1])
plt.plot(x, y[:,2])
plt.plot(x, y[:,3])
plt.plot(x, y[:,4])
plt.savefig(datafile+'.png')