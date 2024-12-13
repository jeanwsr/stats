#!/usr/bin/env python
import csv
import sys
import matplotlib.pyplot as plt

csvfile = sys.argv[1]
name = csvfile.split('.')[0]
ylabels = []
y = []
with open(csvfile, 'r') as f:
    reader = csv.reader(f)
    x = next(reader)[1:]
    for row in reader:
        ylabels.append(row[0])
        y.append(list(map(float, row[1:])))

plt.rc('font', size=12)
fig, ax = plt.subplots()
for i in range(len(y)):
    ax.plot(x, y[i], label=ylabels[i])
ax.legend()
fig.savefig('%s.png'%name)