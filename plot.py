#!/usr/bin/env python

import matplotlib.pyplot as plt
#import sys
import numpy as np

import argparse

def plot_parse():
    p=argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                               description='plot')
    p.add_argument("input",type=str,#default='dump',
                        help='')
    p.add_argument("-x","--show", action="store_true",
                        required=False, 
                        help='')
    p.add_argument("-l","--loc", type=str, dest='loc', metavar='loc', default='lower right',
                        required=False, 
                        help='')
    p.add_argument("-p","--point", type=float, dest='point', metavar='point', default=None,
                        required=False, 
                        help='')
    p.add_argument("-n","--noplot", action="store_true", required=False, help='')
#    p.add_argument("-s","--save", action="store_true", required=False, help='')
    p.add_argument("-u","--unit", type=str, dest='unit', metavar='unit', default='kcal')
    return p
p = plot_parse()

def get_unit(line):
    unit = None
    if 'ev' in line.lower():
        unit = 'eV'
    elif 'kcal' in line.lower():
        unit = 'kcal'
    else:
        print("unit not recognized in res file, use kcal")
        unit = 'kcal'
    return unit

def get_curves(resfile):
    f = open(resfile, 'r')
    x = []
    y = []
    while(True):
        line = f.readline()
        if line[:3] == 'sub':
            unit = get_unit(line)
            seriesline = f.readline()
            series = seriesline.split()
            while(True):
                line = f.readline()
                if line[0].isdigit():
                    #print(line)
                    raw = line.split()
                    #print(raw)
                    data = [float(k) for k in raw]
                    x.append(data[0])
                    #y.append([data[1], data[2], data[3], data[4], data[5]])
                    y.append(data[1:])
                else:
                    break
            break
        elif not line:
            break
    f.close()
    
    x = np.array(x)
    ys = np.array(y)
    return x, ys, series, unit

from interp import spline_findmin
spline = spline_findmin

def interp(x, y, label='', scal=1.0):
    func, point = spline(x, y)
    xmin, ymin = point
    print('%20s root: %.6f  y(root): %.6f' %(label, xmin[0], ymin[0]*scal))
    return func, point


def interp_all(x, ys, labels=[], point=None, scal=1.0):
    funcs = []
    minpoints = []
    for i in range(ys.shape[1]):
        if len(labels[i]) > 0:
            func, minpoint = interp(x, ys[:,i], label=labels[i], scal=scal)
        else:
            func = None
            minpoint = None
        funcs.append(func)
        minpoints.append(minpoint)
    if point is not None:
        for i in range(ys.shape[1]):
            if len(labels[i]) > 0:
                print('%20s point: %.6f  y(point): %.6f' %(labels[i], point, funcs[i](point)*scal))
    return funcs, minpoints

def plot(x, func, minpoint, label=''):
    #print(x, y)
    samp = np.linspace(x[0], x[-1], 100)
    #func, point = interp(x, y)
    y_samp = func(samp)
    #print(samp)
    l, = plt.plot(samp, y_samp )
    plt.plot([minpoint[0]], [minpoint[1]], 'ro', markersize=3)
    return l


def plot_all(x, funcs, minpoints, labels, loc, show, datafile):
    plt.rc('font', size=12)
    plt_lines = []
    #print(ys)
    for i in range(ys.shape[1]):
        if len(labels[i]) > 0:
            l = plot(x, funcs[i], minpoints[i], label=labels[i])
            plt_lines.append(l)
    plt.xlabel('R / $\AA$')
    plt.ylabel('E / a.u.')
    plt.ylim(None, 1.0)
    plt.legend(handles = plt_lines, labels = labels, loc=loc)
    if show:
        plt.show()
    print("save figure to %s.png" % datafile)
    plt.savefig(datafile+'.png')
    
def scal_factor(dataunit, target_unit):
    if dataunit == target_unit:
        return 1.0
    elif dataunit == 'eV' and target_unit == 'kcal':
        return 23.0605
    elif dataunit == 'kcal' and target_unit == 'eV':
        return 1.0/23.0605
    else:
        raise NotImplementedError("unit not supported")

if __name__ == "__main__":
    args = p.parse_args()
    datafile = args.input
    x, ys, series, dataunit = get_curves(datafile)
#    if args.save:
#        import db
#        db.save(x, ys, series, unit=dataunit)
    n_curves = ys.shape[1]
    print(series)
    scal = scal_factor(dataunit, args.unit)
    print("perform unit convertion: %s -> %s, factor: %.6f" % (dataunit, args.unit, scal))
    labels = ['', 'SU-tPBE', 'SUHF', 'SU-tPBE0', 'SU-tPBE(0.25,2)']
    
    funcs, minpoints = interp_all(x, ys, labels=labels[-n_curves:], point=args.point, scal=scal)
    if not args.noplot:
        plot_all(x, funcs, minpoints, labels[-n_curves:], args.loc, args.show, datafile)