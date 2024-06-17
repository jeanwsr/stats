#!/usr/bin/env python
import tomli
import shelve
import sys
from statutil import suDataDB, to_unit
import numpy as np

#LABELS = ['suhf', 'pbe', 'pbe0', 'pbe02']
LABELS = ['pbe02', 'ent5']
LABELS_c = ['suhf', 'pbe02', 
            ('pbe', 'p3', 0.25, 0.0, 0.40),
            ('pbe', 'p3', 0.35, 0.0, 0.55),
            ('pbe', 'p3', 0.40, 0.0, 0.65)]

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
        equations = tomli.load(f)[domain]
    return equations

def get_eq_energy(shelf, toml, mode='label', labels=LABELS):
    params = FitParam()
    params.__dict__.update(toml_load(toml, 'param'))
    equations = toml_load(toml, 'spc')
    print(equations)
    ref = toml_load(toml, 'ref')
    print(ref)
    e_data = {}
    with shelve.open(shelf) as f:
        items = f.keys()
        #print(items[0])
        for serie in items:
            if 'spc' not in serie:
                    continue
            #print(serie)
            data = f[serie]
            name = data['name']
            #print(data)
            e_data[name] = data
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
        if eq not in e_data:
            raise ValueError('eq %s not in e_data'%eq)
        left_data = e_data[eq]
        right_data = [e_data[s] for s in right_spc]
        eq_data = sub_eq(left_data, right_data, labels=labels, unit='kcal')
        #print(eq_data)
        eq_energy[eq] = eq_data
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

def get_curve_eq(shelf, toml, mode='curve', labels=LABELS_c):
    equations = {'n2': 'n+n'}
    e_serie = {}
    e_spc = {}
    with shelve.open(shelf) as f:
        items = f.keys()
        for eq in equations:
            e_serie[eq] = f['serie_'+eq.upper()+'.none']
        for serie in items:
            if 'spc' not in serie or 'ref' in serie:
                continue
            name = f[serie]['name']
            e_spc[name] = f[serie]
        print(e_serie)
        print(e_spc['n'])
    e_serie = update_elabel(e_serie, labels=labels)
    print(e_serie)
    e_spc = update_elabel(e_spc, labels=labels)
    eq_energy = {}
    for eq in equations:
        left_spc = eq
        right_spc = parse_eq(equations[eq])
        print(left_spc, right_spc) 
        left_data = sanit(e_serie[left_spc])  
        print(left_data)
        right_data = [e_spc[s] for s in right_spc]   
        eq_data = sub_eq(left_data, right_data, labels=labels, unit='kcal', scale=-1.0)
        eq_data['x'] = left_data['x']
        print(eq_data)  
        plot(eq_data)
        eq_energy[eq] = eq_data

    return eq_energy

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
    if sys.argv[3] == 'curve':
        get_curve_eq(sys.argv[1], sys.argv[2])
    else:
        get_eq_energy(sys.argv[1], sys.argv[2], sys.argv[3])