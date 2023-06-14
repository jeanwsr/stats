#!/usr/bin/env python

import matplotlib.pyplot as plt
#import sys
import numpy as np

import argparse

def argument_parse():
    parser=argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                               description='')
    parser.add_argument("input",type=str,#default='dump',
                        help='')
    parser.add_argument("-x","--show", action="store_true",
                        required=False, 
                        help='')
    parser.add_argument("-l","--loc", type=str, dest='loc', metavar='loc', default='lower right',
                        required=False, 
                        help='')
    args=parser.parse_args()
    return parser, args

parser, args = argument_parse()
datafile = args.input
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

from scipy.interpolate import make_interp_spline as spl
from scipy.optimize import root
def spline(x, y):
    f = spl(x, y, k=3)
    deriv = f.derivative()
    res = root(deriv, x[2])
    print('root:    %.6f' %res.x)
    print('y(root): %.6f' %f(res.x))
    return f, (res.x, f(res.x))

def plot(x, y):
    samp = np.linspace(x[0], x[-1], 100)
    func, point = spline(x, y)
    y_samp = func(samp)
    #print(samp)
    l, = plt.plot(samp, y_samp )
    plt.plot([point[0]], [point[1]], 'ro', markersize=3)
    return l

plt.rc('font', size=12)
plt_lines = []
for i in range(1,5):
    l = plot(x, y[:,i])
    plt_lines.append(l)
plt.xlabel('R / $\AA$')
plt.ylabel('E / a.u.')
plt.ylim(None, 1.0)
plt.legend(handles = plt_lines, labels = ['SU-tPBE', 'SUHF', 'SU-tPBE0', 'SU-tPBE(0.25,2)'], loc=args.loc)
if args.show:
    plt.show()
plt.savefig(datafile+'.png')
