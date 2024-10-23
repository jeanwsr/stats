#!/usr/bin/env python

import argparse
import numpy as np
from statutil import suData, get_param, runcmd, to_unit   
import db
import shelve
from interp import spline, findmin

def argument_parse():
    parser=argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                               description='')
    parser.add_argument("input",type=str,#default='dump',
                        help='')
    # parser.add_argument("-p","--parse",dest='type',metavar='type',type=str,default='dump',
    #                     required=False, #choices=['dh','scf'],
    #                     help='')
    # parser.add_argument("-f","--fun",dest='fun',metavar='fun',type=str,
    #                     default='suhf',
    #                     required=True,
    #                     )
    # parser.add_argument("-t","--task",dest='task',metavar='task',type=str,
    #                     default='dump',
    #                     required=True,)
    # parser.add_argument("-m","--mode",dest='mode',metavar='mode',type=str,
    #                     default='supddd',
    #                     required=False,)
    #parser.add_argument("--out", type=str, dest='save', metavar='save',
    #                     default = '', required=False, help='')
    parser.add_argument("-i", "--interp", action='store_true', required=False)
    parser.add_argument("-S", "--sub", action='store_true', required=False)
    parser.add_argument("-p", "--param", dest='param', metavar='param', type=str, default='param.txt', required=False)
    return parser

parser = argument_parse()

def to_index(x, start, end):
    if len(start.strip())>0:
        s_f =  float(start)
        s_index = x.index(s_f)
    else:
        s_index = None
    if len(end.strip())>0:
        e_f =  float(end)
        e_index = x.index(e_f) + 1
    else:
        e_index = None
    return s_index, e_index

def interp(f, param):
    items = f.keys()
    for item in items:
        if 'serie' in item:
            serie = f[item]
            x = serie['x']
            print('x', x)
            name = serie['name']
            if name in param:
                _, range, refmin = param[name]
                start, end = range.split(':')
                index = to_index(x, start, end)
                refmin = float(refmin)
            else:
                index = None, None
            print(name, index)

            x_noatom = [xi for xi in x if xi > 0.0]
            x_main = x_noatom[index[0]:index[1]]
            for k in serie.keys():
                if k not in ['name', 'tag', 'x']:
                    y = serie[k]
                    y_noatom = [yi for xi, yi in zip(x, y) if xi > 0.0]
                    y_main = y_noatom[index[0]:index[1]]
                    if not isinstance(y_main[0], float):
                        continue
                    #print(x_main, y_main)
                    yfunc = spline(x_main, y_main)
                    k_refmin = yfunc(refmin)
                    print(k, k_refmin)
                    #xmin, ymin = findmin(yfunc, x_main)
                    #print(xmin, ymin)
            #db.save_spc(ys, su.series(), shelfname, molname)

def load_param(paramfile):
    with open(paramfile) as f:
        lines = f.readlines()
    param = {}
    for line in lines:
        if len(line.strip()) > 0:
            name, range, refmin = line.split()
            param[name] = (None, range, refmin)
    print(param)
    return param

if __name__ == '__main__':
    args=parser.parse_args()
    with shelve.open(args.input) as f:
        param = load_param(args.param)
        interp(f, param)
                

