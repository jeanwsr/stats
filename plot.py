#!/usr/bin/env python

import matplotlib.pyplot as plt
#import sys
import numpy as np

import argparse

def argument_parse():
    parser=argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                               description='')
    parser.add_argument("-i","--input",dest='input',metavar='input',type=str,#default='dump',
                        required=True, #choices=['dh','scf'],
                        help='')
    parser.add_argument("-x","--show",dest='show',metavar='show',type=int,default=0,
                        required=False, #choices=['dh','scf'],
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

plt.plot(x, y[:,1])
plt.plot(x, y[:,2])
plt.plot(x, y[:,3])
plt.plot(x, y[:,4])
if args.show:
    plt.show()
plt.savefig(datafile+'.png')