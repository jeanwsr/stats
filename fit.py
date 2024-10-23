#!/usr/bin/env python
'''
~/stats/fit.py shelf spc.toml label
'''
import tomli
import shelve
import sys
from statutil import suDataDB, to_unit
from plot import interp_all
import numpy as np
import argparse

def fit_parse():
    p=argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                               description='plot')
    p.add_argument("input",type=str,#default='dump',
                        help='')
    p.add_argument("-m","--mode",type=str, dest='mode', metavar='mode', 
                   default='curve',)
    p.add_argument("-t","--toml",type=str, dest='toml', metavar='toml',
                   default='spc.toml',)
    #p.add_argument("-x","--show", action="store_true",
    #                    required=False, 
    #                    help='')
    #p.add_argument("-l","--loc", type=str, dest='loc', metavar='loc', default='lower right',
    #                    required=False, 
    #                    help='')
    #p.add_argument("-p","--point", type=float, dest='point', metavar='point', default=None,
    #                    required=False, 
    #                    help='')
    p.add_argument("-n","--noplot", action="store_true", required=False, help='')
#    p.add_argument("-s","--save", action="store_true", required=False, help='')
    p.add_argument("-u","--unit", type=str, dest='unit', metavar='unit', 
                   default='kcal')
    p.add_argument("-v","--verbose", type=int, dest='verbose', metavar='verbose',
                   default=3)
    return p
p = fit_parse()

#LABELS = ['suhf', 'pbe', 'pbe0', 'pbe02']
#LABELS = ['pbe02', 'ent5']
LABELS_c = ['suhf', 'pbe', 'pbe0', 'pbe02', 
            ('pbe', 0.10, 2),
            ('pbe', 'p3', 0.25, 0.0, 0.40),
            ('pbe', 'p3', 0.35, 0.0, 0.55),
            ('pbe', 'p3', 0.40, 0.0, 0.65)]
LABELS = LABELS_c

class FitParam:
    def __init__(self):
        self.hmin = 0.15
        self.hmax = 0.5
        self.kmin = 1.5
        self.kmax = 3.5
        self.potk = 0.0
        self.potcmin = 0.25
        self.potcmax = 0.75
        self.hstep = 0.05
        self.kstep = 0.5
        self.cstep = 0.05
        self.theta = 0.00

    def gen_labels(self):
        labels = []
        for h in np.arange(self.hmin, self.hmax+0.01, self.hstep):
            for k in np.arange(self.kmin, self.kmax+0.01, self.kstep):
                labels.append(('pbe', h, k, self.theta))
        return labels

    def gen_labels_potc(self):
        labels = []
        print(f"hmin: {self.hmin}, hmax: {self.hmax}, hstep: {self.hstep}")
        print(f"potcmin: {self.potcmin}, potcmax: {self.potcmax}, cstep: {self.cstep}")
        for h in np.arange(self.hmin, self.hmax+0.01, self.hstep):
           for potc in np.arange(self.potcmin, self.potcmax+0.01, self.cstep):
                labels.append(('pbe', h, 0.0, 0.0, (self.potk, potc)))
        return labels


def toml_load(toml, domain):
    with open(toml, 'rb') as f:
        e = tomli.load(f)
        if domain in e:
            return e[domain]
        else:
            return None

def get_elabel(shelf, mode='label', labels=LABELS, name='full'):
    #params = FitParam()
    #params.__dict__.update(toml_load(toml, 'param'))
    #equations = toml_load(toml, 'spc')
    #print(equations)
    #ref = toml_load(toml, 'ref')
    #print(ref)
    e_data = {}
    with shelve.open(shelf) as f:
        items = f.keys()
        #print(items[0])
        for serie in items:
            if 'spc' not in serie:
                    continue
            #print(serie)
            data = f[serie]
            n = data['name']
            if name == 'full':
                n = serie
            #print(data)
            e_data[n] = data
    print(e_data.keys())
    #print(e_data)
    if mode == 'label':
        pass
        labels = LABELS
    #elif mode == 'scan':
    #    labels = params.gen_labels()
    #elif mode == 'scan3':
    #    labels = params.gen_labels()
    #    print(labels)
    #elif mode == 'scan_potc':
    #    labels = params.gen_labels_potc()
    e_data = update_elabel(e_data, labels=labels)
    print(e_data)
    dump_dev(e_data, None, mode)

def get_eq_energy(shelf, toml, mode='label', labels=LABELS, name='full'):
    
    equations = toml_load(toml, 'spc')
    print(equations)
    ref = toml_load(toml, 'ref')
    print(ref)
    toml_param = toml_load(toml, 'param')
    if toml_param is not None:
        params = FitParam()
        params.__dict__.update(toml_load(toml, 'param'))
    e_data = {}
    with shelve.open(shelf) as f:
        items = f.keys()
        #print(items[0])
        for serie in items:
            if 'spc' not in serie:
                    continue
            #print(serie)
            data = f[serie]
            n = data['name']
            if name == 'full' and '.' in data['tag']:
                n = data['name']+data['tag']
            #print(data)
            e_data[n] = data
    print(e_data.keys())
    #print(e_data)
    if mode == 'label':
        pass
        #labels = LABELS
    elif mode == 'scan':
        labels = params.gen_labels()
    elif mode == 'scan3':
        labels = params.gen_labels()
        print(labels)
    elif mode == 'scan_potc':
        labels = params.gen_labels_potc()
    e_data = update_elabel(e_data, labels=labels)
    eq_energy = {}
    for eq in equations:
        left_spc = eq
        right_spc = parse_eq(equations[eq])
        print(left_spc, right_spc)
        if eq in e_data:
            matches = [eq]
        else:
            matches = [s for s in e_data if eq in s]
            #raise ValueError('eq %s not in e_data'%eq)
        for m in matches:
            print(m)
            left_data = e_data[m]
            right_data = [e_data[s] for s in right_spc]
            eq_data = sub_eq(left_data, right_data, labels=labels, unit='kcal')
            #print(eq_data)
            eq_energy[m] = eq_data
    if ref is None:
        print(eq_energy)
        return eq_energy
    print(eq_energy)
    eq_deviation = sub_ref(eq_energy, ref, mode)
    #print(eq_deviation)
    for eq in eq_deviation:
        print(eq)
        dump_dev(eq_deviation[eq], params, mode)
    mad, maxd = get_mad(eq_deviation, labels)
    print('MAD')
    dump_dev(mad, params, mode)
    print('MaxD')
    dump_dev(maxd, params, mode)
    return eq_energy

def get_curve_eq(shelf, toml, mode='curve', labels=LABELS_c, unit='kcal', verbose=3):
    equations = toml_load(toml, 'spc')
    print(equations)
    #equations = {'n2': 'n+n'}
    e_serie = {}
    e_spc = {}
    with shelve.open(shelf) as f:
        items = f.keys()
        for eq in equations:
            if 'serie_'+eq+'.none' not in items:
                continue
            e_serie[eq] = f['serie_'+eq+'.none']
        for serie in items:
            if 'spc' not in serie or 'ref' in serie:
                continue
            name = f[serie]['name']
            e_spc[name] = f[serie]
        #print(e_serie)
        #print(e_spc)
    e_serie = update_elabel(e_serie, labels=labels)
    #print(e_serie)
    if len(e_spc) == 0:
        return e_serie
    e_spc = update_elabel(e_spc, labels=labels)
    eq_energy = {}
    for eq in e_serie:
        left_spc = eq
        right_spc = parse_eq(equations[eq])
        print(left_spc, right_spc) 
        left_data = sanit(e_serie[left_spc])  
        #print(left_data)
        right_data = [e_spc[s] for s in right_spc]   
        eq_data = sub_eq(left_data, right_data, labels=labels, unit=unit#, scale=-1.0
                         )
        eq_data['x'] = left_data['x']
        if verbose > 3:
            print('eq_data', eq_data)
        #interp
        interp_all_wrap(eq_data)
        #plot(eq_data)
        eq_energy[eq] = eq_data

    return eq_energy

def interp_all_wrap(eq_data):
    labels = []
    ys0 = []
    for label in eq_data:
        if label == 'x':
            continue
        labels.append(label)
        y = eq_data[label]
        ys0.append(y)
        ys = np.asarray(ys0).T

    funcs, minpoints = interp_all(eq_data['x'], ys, labels)
    return funcs, minpoints

def sanit(data):
    data['x'] = np.array(data['x'])
    x = data['x']
    for item in data:
        if item == 'name' or item == 'tag':
            continue
        data[item] = data[item][x>0.0]
    return data


def parse_eq(eq):
    spc = eq.split('+')
    return spc

def sub_eq(left, right, labels=['suhf'], unit='au', scale=1.0):
    '''
    left: dict
    right: list of dict
    '''
    #print(left)
    eq_data = {}
    scal = to_unit(unit)*scale
    for label in labels:
        left_e = left[label]
        right_es = [r[label] for r in right]
        right_e = sum(right_es)
        if 'ent' in label:
            print('ent5', left_e, right_es)
        eq_e = right_e - left_e
        eq_data[label] = eq_e*scal
    return eq_data

def sub_ref(eq_e, ref, mode):
    '''
    data: dict
    ref: dict
    '''
    eq_deviation = {}
    for eq in eq_e:
        e = eq_e[eq]
        ref_e = ref[eq]
        eq_dev = {}
        for label in e:
            eq_dev[label] = e[label] - ref_e
        eq_deviation[eq] = eq_dev
        #print(eq)
        #dump_dev(eq_dev, mode)
    return eq_deviation

def update_elabel(e_data, labels=['suhf']):
    '''
    '''
    for name in e_data:
        data = e_data[name]
        su = suDataDB(data)
        elabels = su.get_elabels(labels)
        #print(name, elabels) 
        e_data[name].update(elabels)
    #print(e_data)
    return e_data



def dump_dev(dev, param, mode='scan'):
    if 'pbe02' in dev:
        for k, e in dev.items():
            print(k, " %.3f" % e)
    if mode == 'scan':
        for h in np.arange(param.hmin, param.hmax+0.01, param.hstep):
            for k in np.arange(param.kmin, param.kmax+0.01, param.kstep):
                t = param.theta
                print("%2.3f" % dev[('pbe', h, k, t)], end=' ')
            print()
    elif mode == 'scan_potc':
        print("   ", end=' ')
        for potc in np.arange(param.potcmin, param.potcmax+0.01, param.cstep):
            print("  &%.2f" % potc, end=' ')
        print('\\\\')
        for h in np.arange(param.hmin, param.hmax+0.01, param.hstep):
            print("%.2f" % h, end=' ')
            for potc in np.arange(param.potcmin, param.potcmax+0.01, param.cstep):
                print("&%2.3f" % dev[('pbe', h, 0.0, 0.0, (param.potk, potc))], end=' ')
            print('\\\\')

def get_mad(eq_deviation, labels):
    mad = {}
    maxd = {}
    for label in labels:
        m = 0.0
        mx = 0.0
        for eq in eq_deviation:
            dev = eq_deviation[eq][label]
            m += abs(dev)
            if abs(dev) > mx:
                mx = abs(dev)
        m /= len(eq_deviation)
        mad[label] = m
        maxd[label] = mx
    return mad, maxd

def plot(eq_data):
    import matplotlib.pyplot as plt
    plt.rc('font', size=12)
    plt_lines = []
    labels = []
    #print(ys)
    x = eq_data['x']
    for label in eq_data:
        if label != 'x':
            l, = plt.plot(x, eq_data[label])
            plt_lines.append(l)
            labels.append(label)
    plt.xlabel('R / $\AA$')
    plt.ylabel('E / kcal/mol')
    plt.ylim(None, 1.0)
    plt.legend(handles = plt_lines, labels = labels)
    #if show:
    #    plt.show()
    #print("save figure to %s.png" % datafile)
    plt.savefig('test.png')



if __name__ == '__main__':
    args = p.parse_args()
    shelf = args.input
    mode = args.mode
    toml = args.toml
    verbose = args.verbose
    if mode == 'curve':
        get_curve_eq(shelf, toml, mode, unit=args.unit, verbose=verbose)
    elif mode == 'none':
        get_elabel(shelf)
    else:
        get_eq_energy(shelf, toml, mode)
