#!/usr/bin/env python
"""
Parse SUPDFT output;
Interpolate dissociation curve

stats -t 'task*' -f PBE -m 'pddd'
"""

import argparse
import numpy as np
from statutil import suData, get_param, runcmd, to_unit   

def argument_parse():
    parser=argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                               description='')
    parser.add_argument("-p","--parse",dest='type',metavar='type',type=str,default='dump',
                        required=False, #choices=['dh','scf'],
                        help='')
    parser.add_argument("-f","--fun",dest='fun',metavar='fun',type=str,
                        default='suhf',
                        required=True,
                        )
    parser.add_argument("-t","--task",dest='task',metavar='task',type=str,
                        default='dump',
                        required=True,)
    parser.add_argument("-s","--rscale",dest='rscale',metavar='rscale',type=int,
                        default=100,
                        required=False,)
    parser.add_argument("-S","--sub", action='store_true',
                        required=False,)
    parser.add_argument("-m","--mode",dest='mode',metavar='mode',type=str,
                        default='supddd',
                        required=False,)
    parser.add_argument("-i","--interp", action='store_true',
                        required=False,)
    parser.add_argument("-r","--range",dest='range',metavar='range',type=str,
                        default='-1000,1000',
                        required=False,)
    parser.add_argument("-u","--unit", type=str, dest='unit', metavar='unit', default='kcal')
    parser.add_argument("--save", type=str, dest='save', metavar='save',
                        default = '', required=False, help='')
    return parser

parser = argument_parse()


if __name__ == '__main__':
    args=parser.parse_args()
    
    mode = args.mode
    h, k = get_param(args.fun) #float(sys.argv[2])
    #float(sys.argv[3])
    task = args.task
    rscale = args.rscale #float(sys.argv[4])
    sub = bool(args.sub) #bool(sys.argv[5])
    save = len(args.save) > 0
    shelfname, molname = args.save.split(':')
    if (len(shelfname) < 1 or len(molname) < 1) and save:
        raise ValueError('invalid shelfname or molname')
    
    filelist = runcmd("ls %s" % task).strip().split('\n')
    print(filelist)
    
    lim = [0,0]
    r_range = args.range.split(',')
    lim[0] = float(r_range[0])
    lim[1] = float(r_range[1])
    
    print("        SUDD       SUPD       SUHF       SUPD(h)      SUPD(h,k)")
    #exit()
    
    x = []
    e_dd = []
    e_pd = []
    e_su = []
    e_supdh = []
    e_supdk = []
    raw_ys = []
    for s in filelist:
        #r = s.replace(task, '').replace('.out', '')
        r = s.split('_')[-1].split('.')[0]
        if r[0].isdigit():
            if float(r)/rscale < lim[0] or float(r)/rscale > lim[1]:
                continue
        #print(s, r)
        runcmd("cp %s tmp" % s)
        runcmd("sed -i 's/://' tmp")
        p = runcmd("grep ^E_ tmp | awk '{print $2}'")
        data = p.split('\n')
        #print(data)
        su = suData(data, mode)
        if save:
            raw_ys.append(su.res())
        print('%s  %6.6f %6.6f %6.6f %6.6f %6.6f'%(r, su.sudd(0.0), su.supd(0.0), su.suhf, su.supd(h), su.supd_k(h,k)))
        if r[0].isdigit():
            x.append(float(r)/rscale)
        else:
            x.append(-1)
        e_dd.append(su.sudd(0.0))
        e_pd.append(su.supd(0.0))
        e_su.append(su.suhf)
        e_supdh.append(su.supd(h))
        e_supdk.append(su.supd_k(h,k))
    
    if save:
        ys = np.array(raw_ys).T
        db.save(x, ys, su.series(), shelfname, molname)
    #exit()
    def sub_atom(lst):
        array = np.array(lst)
        return array[:-2] - array[-1] - array[-2]
    
    scal = to_unit(args.unit)
    if sub:
        print("subtract by atom e. in %s"%args.unit)
        print("     SUDD    SUPD    SUHF    SUPD(h)   SUPD(h,k)")
        x_sub = np.array(x)[:-2]
        e_dd_sub = sub_atom(e_dd)*scal
        e_pd_sub = sub_atom(e_pd)*scal
        e_su_sub = sub_atom(e_su)*scal
        e_supdh_sub = sub_atom(e_supdh)*scal
        e_supdk_sub = sub_atom(e_supdk)*scal
        for i in range(len(x_sub)):
            print('%s  %6.3f %6.3f %6.3f %6.3f %6.3f'%(x_sub[i], 
                  e_dd_sub[i], e_pd_sub[i], e_su_sub[i], e_supdh_sub[i], e_supdk_sub[i]))
    
    #exit()
    from interp import spline_findmin
    if args.interp:
        for y in [e_dd_sub, e_pd_sub, e_su_sub, e_supdh_sub, e_supdk_sub]:
            spline_findmin(x_sub, y)
