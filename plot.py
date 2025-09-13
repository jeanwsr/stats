#!/usr/bin/env python

try:
    import matplotlib.pyplot as plt
except:
    print('warn: matplotlib not found')
#import sys
import numpy as np
from labelset import *
from unit import scal_factor, get_unit

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
    p.add_argument("-m","--mode", type=str, dest='mode', metavar='mode', default='normal',)
    p.add_argument("-n","--noplot", action="store_true", required=False, help='')
#    p.add_argument("-s","--save", action="store_true", required=False, help='')
    p.add_argument("--xmin", type=float, dest='xmin', metavar='xmin', default=None)
    p.add_argument("--xmax", type=float, dest='xmax', metavar='xmax', default=None)
    p.add_argument("--ymin", type=float, dest='ymin', metavar='ymin', default=None)
    p.add_argument("--ymax", type=float, dest='ymax', metavar='ymax', default=None)
    p.add_argument("-u","--unit", type=str, dest='unit', metavar='unit', default='kcal')
    p.add_argument("--xunit", type=str, dest='xunit', metavar='xunit', default='angs')
    p.add_argument("-o","--output", type=str, dest='output', metavar='output', default='test')
    return p
p = plot_parse()

def get_curves(resfile):
    f = open(resfile, 'r')
    x = []
    y = []
    while(True):
        line = f.readline()
        if line[:3] == 'sub':
            unit = get_unit(line)
            seriesline = f.readline()
            if '#ilabel' in seriesline:
                ilabelset = int(seriesline.split('#ilabelset')[1].strip())
                series = labelset[ilabelset][1]
            else:
                series = seriesline.split()
            #print(series)
            while(True):
                line = f.readline().strip()
                #print(line)
                if len(line) < 1: break
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

    nseries = len(series) 
    x = np.array(x)
    ys = np.array(y)
    ys = ys[:,:nseries]
    if 'reffit' in series:
        print('remove reffit')
        idx = series.index('reffit')
        ys = np.delete(ys, idx, axis=1)
        series.remove('reffit')
    print('series', series)
    print('ys', ys)
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
    print('x', x)
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

FONTSIZE = 12

def plot(ax, x, func, minpoint, label='', scale=1.0, plotmin=True):
    #print(x, y)
    npoint = 400
    if x[-1] - x[0] > 10.0:
        npoint = 1000
    samp = np.linspace(x[0], x[-1], npoint)
    #func, point = interp(x, y)
    y_samp = func(samp)*scale
    #print(samp)
    l, = ax.plot(samp, y_samp )
    #print(minpoint)
    if plotmin:
        ax.plot(minpoint[0], minpoint[1]*scale, 'ro', markersize=3)
    return l

def label_legend(ax, unit, xunit, plt_lines, labels, 
                 loc='lower right', ):
    xunit_display = xunit
    if xunit == 'angs':
        xunit_display = '$\AA$'
        ax.set_xlabel('R / %s' % xunit_display)
    elif xunit == 'deg':
        #xunit_display = '$^\circ$'
        ax.set_xlabel('angle / degree')
    else:
        xunit_display = xunit
        ax.set_xlabel('R / %s' % xunit_display)
    unit_display = unit
    if unit == 'kcal':
        unit_display = 'kcal/mol'
    ax.set_ylabel('E / %s' % unit_display)
    ax.legend(handles = plt_lines, labels = labels, loc=loc)

def set_lim(ax, xlim=(None,None), ylim=(None,None)):
    ax.set_xlim(xlim[0], xlim[1])
    ax.set_ylim(ylim[0], ylim[1])


def plot_all(x, funcs, minpoints, labels, loc='lower right', 
             show=False, save=True, datafile='test', scale=1.0, unit='a.u.',
             xunit='angs', ylim=(None,None), plotmin=True, mode='normal',
             fig=None, ax=None, plt_lines=None):
    #if mode == 'child':
    #    plt.rc('font', size=FONTSIZE*2)
    #else:
    if plt_lines is None:
        plt_lines = []
    #print(ys)
    if fig is None:
        fig, ax = plt.subplots()
    for i in range(len(funcs)):
        #if 'reffit' in labels[i]:
        #    continue
        if len(labels[i]) > 0:
            l = plot(ax, x, funcs[i], minpoints[i], label=labels[i], scale=scale, plotmin=plotmin)
            plt_lines.append(l)
    if save:
        label_legend(ax, unit, xunit, plt_lines, labels, loc=loc, ylim=ylim)
    if show:
        plt.show()
    if save:
        print("save figure to %s.png" % datafile)
        fig.savefig(datafile+'.png')
    return fig, plt_lines
    
if __name__ == "__main__":
    args = p.parse_args()
    datafiles = args.input.split(',')
    plt.rc('font', size=FONTSIZE)
    fig, ax = plt.subplots(layout="constrained")
    if args.mode == 'child':
        fig.set_size_inches(6.4*0.4, 4.8*0.36)
        fig.set_facecolor((1,1,1,0))
        #ax.spines['bottom'].set_position(('axes',1))
        #print(ax.spines)
        ax.xaxis.set_ticks_position('top')
    if args.mode == 'nomin':
        plotmin = False
    else:
        plotmin = True
    plt_lines = []
    labels_all = []
    for datafile in datafiles:
        x, ys, series, dataunit = get_curves(datafile)
#    if args.save:
#        import db
#        db.save(x, ys, series, unit=dataunit)
        n_curves = ys.shape[1]
        print(series)
        scal = scal_factor(dataunit, args.unit)
        print("perform unit convertion: %s -> %s, factor: %.6f" % (dataunit, args.unit, scal))
        #labels = ['', 'SU-tPBE', 'SUHF', 'SU-tPBE0', 'SU-tPBE(0.25,2)']
        labels = series
        labels_all += labels
    
        funcs, minpoints = interp_all(x, ys, labels=labels, point=args.point, scal=scal)
        if not args.noplot:
            fig, plt_lines = plot_all(x, funcs, minpoints, labels=labels, #loc=args.loc, 
                     show=args.show, save=False, 
                     #datafile=datafile,
                     unit=args.unit, scale=scal, mode=args.mode, plotmin=plotmin,
                     fig=fig, ax=ax, plt_lines=plt_lines)
    set_lim(ax, xlim=(args.xmin, args.xmax), ylim=(args.ymin, args.ymax))
    if args.mode != 'child':
        label_legend(ax, args.unit, args.xunit, plt_lines, labels_all,
                     loc=args.loc, 
                 #xlim=(args.xmin, args.xmax), ylim=(args.ymin, args.ymax)
                 )
    fig.savefig('%s.png'%args.output, dpi=300)
