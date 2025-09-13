#!/usr/bin/env python
'''
~/stats/ex.py spc
'''
from statutil import runcmd
import numpy as np
import sys, os

ha2kcal = 627.509474

spc = sys.argv[1]
if spc == 'butad' or spc == 'pyrim':
    spin = 'spin'
else:
    spin = ''
targ = sys.argv[2]
#target_xc = 'SU-TBLYP)'
target_xc = 'SU-' + targ + ')'
out_dir = 'tune_blyp'

def get_e( tmpp ):
    p_final = runcmd("grep Final %s | awk '{print $4}'"%tmpp).strip('\n').strip(',')
    cmd = f"grep '{target_xc}' {tmpp}"+" | awk '{print $3}'"
    p_rssupd = runcmd(cmd).split('\n')[:1]
    print(cmd)
    print(p_rssupd)
    #print(p_final, p_rssupd)
    if len(p_final) > 0:
        e_final = float(p_final)
    else:
        e_final = -1
    e_rssupd = list(map(float, p_rssupd))
    #print(e_rssupd)
    return e_final, np.array(e_rssupd)

omega_list = [0.2, 
0.3, 
0.4, #0.5, 0.6
]
sr_list = [0.7, 0.6, 0.5, 0.4]
lam_list = [1.0]
nomega = len(omega_list)
nsr = len(sr_list)
nl = 1
est = np.zeros((nomega,nsr,nl,2))
for i1,o in enumerate(omega_list):
    if not os.path.exists(f"{out_dir}/{spc}_{spin}0.out.rs_o{o}_sr0.5"):
        continue
    for i2,sr in enumerate(sr_list):
        for i3,l in enumerate(lam_list):
        #echo $o $a $l
            e0_rs, e0_rssupd = get_e( f"{out_dir}/{spc}_{spin}0.out.rs_o{o}_sr{sr}" )
            e2_rs, e2_rssupd = get_e( f"{out_dir}/{spc}_{spin}2.out.rs_o{o}_sr{sr}" )
            #print(e0_rs, e2_rs)
            if e0_rs == -1 or e2_rs == -1:
                est_rs = 0
            else:
                est_rs = e2_rs - e0_rs
            est_rssupd = e2_rssupd - e0_rssupd
            est[i1,i2,i3,0] = est_rs*ha2kcal
            est[i1,i2,i3,1:] = est_rssupd*ha2kcal
    print('omega %.1f'%o)
    #print(est[i1,:,:,0])
    print(est[i1,:,0,1])

      
