#!/usr/bin/env python

"""
stats_spc.py -t 'task*' -f PBE02 [-l ref] [--save ../shelf]

-l ref for reference minimum, e.g. sio_151.3.out
-l none (default) for out without x, e.g. sio_si.out
"""

import argparse
import numpy as np
from statutil import suData, get_param, runcmd, to_unit   
import db

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
    parser.add_argument("-m","--mode",dest='mode',metavar='mode',type=str,
                        default='supddd',
                        required=False,)
    parser.add_argument("-l","--label",dest='label',metavar='label',type=str,
                        default="none")
    parser.add_argument("-s","--rscale",dest='rscale',metavar='rscale',type=int,
                        default=100,
                        required=False,)
    parser.add_argument("--save", type=str, dest='save', metavar='save',
                        default = '', required=False, help='')
    return parser

parser = argument_parse()


if __name__ == '__main__':
    args=parser.parse_args()
    
    mode = args.mode
    do_ent = False
    h, k = get_param(args.fun)[:2] #float(sys.argv[2])
    #float(sys.argv[3])
    task = args.task
    rscale = args.rscale 
    #sub = bool(args.sub) #bool(sys.argv[5])
    label = args.label
    save = len(args.save) > 0
    if save:
        shelfname = args.save
        if len(shelfname) < 1:
            raise ValueError('invalid shelfname')
    
    filelist = runcmd("ls %s" % task).strip().split('\n')
    print(filelist)

    #e_dd = []
    #e_pd = []
    #e_su = []
    #e_supdh = []
    #e_supdk = []
    #raw_ys = []
    for s in filelist:
        #r = s.replace(task, '').replace('.out', '')
        name0, name1 = s.split('.out')[0].split('_')
        if label == 'none':
            spc = name1 # sio_si.out -> si
            x = None
        elif label == 'ref':
            # sio_151.3.out -> sio, 151.3
            spc = name0
            x = float(name1)/rscale
        else:
            raise ValueError('invalid label')
        
        #spc = to_(spc)
        #print(s, r)
        runcmd("cp %s tmp" % s)
        runcmd("sed -i 's/://' tmp")
        p = runcmd("grep ^E_ tmp | awk '{print $2}'")
        data = p.split('\n')
        if do_ent:
            p2a = runcmd("grep '^SUHF NO occ alpha' tmp")
            p2b = runcmd("grep '^SUHF NO occ beta' tmp")
            occdata = p2a.split('alpha')[1].split()[:-1], p2b.split('beta')[1].split()[:-1]
        else:
            occdata = None
        #print(occdata)
        su = suData(data, mode, occdata=occdata)
        if save:
            raw_ys = su.res()
        print('%s  %6.6f %6.6f %6.6f %6.6f %6.6f'%('_'.join((name0, name1)), su.sudd(0.0), su.supd(0.0), su.suhf, su.supd(h), su.supd_k(h,k)))
        if do_ent:
            print('natocc_a:', su.natocc_a, 'ent:', su.ent)
        #if r[0].isdigit():
        #    x.append(float(r)/rscale)
        #else:
        #    x.append(-1)
        #e_dd.append(su.sudd(0.0))
        #e_pd.append(su.supd(0.0))
        #e_su.append(su.suhf)
        #e_supdh.append(su.supd(h))
        #e_supdk.append(su.supd_k(h,k))
        if save:
            ys = np.array(raw_ys)
            #print(ys, su.series())
            molname = spc
            db.save_spc(ys, su.series(), shelfname, molname, tag=label, x=x)
    