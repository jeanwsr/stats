#!/usr/bin/env python
'''
~/stats/fit.py shelf spc.toml label
'''
import tomli
import shelve
import sys
from statutil import suDataDB, to_unit
import matplotlib.pyplot as plt
from plot import interp_all, plot_all
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
    p.add_argument("-l","--labelset", type=int, dest='labelset', metavar='labelset', default=0)
    p.add_argument("-p","--plot", action="store_true", required=False, help='')
#    p.add_argument("-s","--save", action="store_true", required=False, help='')
    p.add_argument("-u","--unit", type=str, dest='unit', metavar='unit', 
                   default='kcal')
    p.add_argument("--xunit", type=str, dest='xunit', metavar='xunit', default='angs')
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

LABELS_p = ['suhf', 'pbe', 'pbe02', ('pbe', 'p3', 0.25, 0.0, 0.40)]
LABELS_display = ['SUHF', 'SU-tPBE', 'SU-tPBE($\lambda,k$)', 'SU-tPBE($\lambda,c$)']

LABELS_p1 = ['suhf', 'pbe', 'pbe02', ('pbe', 0.10, 2), ('pbe', 'p3', 0.25, 0.0, 0.40)]
LABELS_display1 = ['SUHF', 'SU-tPBE', 'SU-tPBE($\lambda,k$)', 'SU-tPBE($\lambda,k$)', 'SU-tPBE($\lambda,c$)']

LABELS_t = ['suhf', 'pbe', 'pbe02', ('pbe', 0.10, 2), ('pbe', 'p3', 0.25, 0.0, 0.40), 
            ('pbe', 't', 0.25, 0.0, 0.0),
            ('pbe', 't', 0.25, 0.0, -0.025), 
            # ('pbe', 't', 0.30, 0.0, -0.025),
            # ('pbe', 't', 0.30, 0.0, -0.005),
            # ('pbe', 't', 0.30, 0.10, -0.005),
            # ('pbe', 't', 0.30, 0.15, -0.005),
            # ('pbe', 't', 0.30, 0.20, -0.005),
            # ('pbe', 't', 0.30, 0.0, -0.020),
            # ('pbe', 't', 0.30, 0.05, -0.020),
            # ('pbe', 't', 0.30, 0.10, -0.020),
            # ('pbe', 't', 0.30, 0.15, -0.020),
            ]
for h in np.arange(0.40, 0.40+0.01, 0.05):
    for t in np.arange(-0.005, -0.030-0.001, -0.005):
        for c in np.arange(-0.10, 0.25+0.01, 0.05):
            LABELS_t.append(('pbe', 't', h, c, t))
LABELS_display_t = ['SUHF', 'SU-tPBE', 'SU-tPBE($\lambda,k$)', 'SU-tPBE($\lambda,c$)',
                    'SU-tPBE($\lambda,t=-0.005$)', 'SU-tPBE($\lambda,t=-0.010$)']

LABELS_t2 = ['suhf', 'pbe', ('pbe', 'p3', 0.25, 0.0, 0.40),
             ('pbe', 't', 0.25, 0.0, -0.025),
             ('pbe', 't', 0.30, 0.10, -0.010)
             ]
LABELS_display_t2 = ['SUHF', 'SU-tPBE', 'SU-tPBE($\lambda,c$)', 'SU-tPBE($\lambda,t=-0.025$)', 'SU-tPBE($\lambda,t=-0.010$)']

labelset = [[LABELS_p, LABELS_display], [LABELS_p1, LABELS_display1],
            [LABELS_t, LABELS_display_t], [LABELS_t2, LABELS_display_t2]]

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

def get_eq_energy(shelf, toml, mode='label', ilabelset=0, name='full'):
    if ':' in toml:
        toml, dset = toml.split(':')
    else:
        dset = 'spc'
    equations = toml_load(toml, dset)
    #equations = toml_load(toml, 'spc')
    print(equations)
    ref = toml_load(toml, 'ref')
    print(ref)
    toml_param = toml_load(toml, 'param')
    if toml_param is not None:
        params = FitParam()
        params.__dict__.update(toml_load(toml, 'param'))

    labels, LABELS_display = labelset[ilabelset]
    print(labels)
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
                if '.' in data['tag']:
                    n = data['name']+data['tag']
                else:
                    n = spc2name(serie, data)
            #print(data)
            e_data[n] = data
    print('e_data', e_data.keys())
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
    #print(e_data)
    eq_energy = {}
    for eq in equations:
        left_spc = eq
        right_spc = parse_eq(equations[eq])
        print(left_spc, right_spc)
        #has_eq, eq_in_shelf = has_eq_fuzzy(e_data.keys(), eq)
        #exit()
        if eq in e_data:
            matches = [eq]
        else:
            matches = [s for s in e_data if eq in s]
            #raise ValueError('eq %s not in e_data'%eq)
        for m in matches:
            print(m)
            left_data = e_data[m]
            right_data = [e_data[s] for s in right_spc]
            #right_data = []
            #for s in right_spc:
            #    has_s, s_in_shelf = has_eq_fuzzy(e_data.keys(), s)
            #    right_data.append(e_data[s_in_shelf])
            print(left_data)
            print(right_data)
            eq_data = sub_eq(left_data, right_data, labels=labels, unit='kcal')
            #print(eq_data)
            eq_energy[m] = eq_data
    if ref is None:
        print(eq_energy)
        return eq_energy
    #print(eq_energy)
    for eq in eq_energy:
        print(eq)
        #dump_dev(eq_energy[eq], params, mode)
    eq_deviation = sub_ref(eq_energy, ref, mode)
    if len(eq_deviation) == 0:
        return eq_energy
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

def has_eq_fuzzy(items, eq):
    if '(' in eq:
        t = eq.split('(')[1].split(')')[0]
        eq = eq.split('(')[0] + '.ref' + t
    #print(eq)
    for item in items:
        if eq in item:
            return True, item
    print('search', eq, item)
    return False, None

def spc2name(spc, fspc):
    name = fspc['name'].lower()
    if 'ref' in spc:
        t = spc.split('ref')[1]
        if len(t) > 0:
            name = name + '(%s)'%t
    
    return name

def get_curve_eq(shelf, toml, mode='curve', ilabelset=0, unit='kcal', xunit='angs', plot=False, verbose=3):
    if ':' in toml:
        toml, dset = toml.split(':')
    else:
        dset = 'spc'
    equations = toml_load(toml, dset)
    print(equations)
    #equations = {'n2': 'n+n'}
    #exit()
    labels, labels_display = labelset[ilabelset]
    e_serie = {}
    e_spc = {}
    with shelve.open(shelf) as f:
        items = f.keys()
        for eq in equations:
            has_eq, eq_in_shelf = has_eq_fuzzy(items, eq)
            if not has_eq:
                continue
            e_serie[eq] = f[eq_in_shelf]
        for spc in items:
            if 'spc' not in spc:
                continue
            else:
                fspc = f[spc]
                name = spc2name(spc, fspc)
                e_spc[name] = f[spc]
        #print(e_serie)
        #print(e_spc)
    if verbose > 3:
        print(e_serie.keys())
        print(e_spc.keys())
    e_serie = update_elabel(e_serie, labels=labels)
    #print(e_serie)
    submin = False
    if len(e_spc) == 0:
        if 'min' in equations.values():
            submin = True
        else:
            return e_serie
    if len(e_spc) > 0:
        e_spc = update_elabel(e_spc, labels=labels)
    eq_energy = {}
    print('unit: ', unit)
    for eq in e_serie:
        left_spc = eq
        left_data = e_serie[left_spc]
        if not submin:
            left_data = sanit(left_data)
            right_spc = parse_eq(equations[eq])
            print(left_spc, right_spc) 
            #print(left_data)
            right_data = [e_spc[s] for s in right_spc]   
            eq_data = sub_eq(left_data, right_data, labels=labels, unit=unit#, scale=-1.0
                         )
        else:
            eq_data = sub_min(left_data, labels=labels, unit=unit)
        eq_data['x'] = left_data['x']
        if verbose > 3:
            print('eq_data', eq_data)
        #interp
        funcs, mins = interp_all_wrap(eq_data)
        #plot_eq(eq_data)
        if plot:
            if not submin:
                print(mins)
                plot_all(eq_data['x'], funcs, mins, labels=labels_display, datafile=eq, scale=-1.0, unit=unit,
                         ylim=(None, 1.0))
            else:
                plot_all(eq_data['x'], funcs, mins, labels=labels_display, datafile=eq, scale=1.0, unit=unit,
                         xunit=xunit, ylim=(0.0, None), plotmin=False)
        eq_energy[eq] = eq_data

    return eq_energy

def interp_all_wrap(eq_data):
    labels = []
    ys0 = []
    for label in eq_data:
        if label == 'x' or label == 'name' or label == 'tag':
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

def sub_min(data, labels=['suhf'], unit='au'):
    eq_data = {}
    eq_data['name'] = data['name']
    scal = to_unit(unit)
    imin = data['suhf'].argmin()
    for label in labels:
        left_e = data[label]
        eq_e = left_e - left_e[imin]
        eq_data[label] = eq_e*scal
    return eq_data

def sub_eq(left, right, labels=['suhf'], unit='au', scale=1.0):
    '''
    left: dict
    right: list of dict
    '''
    #print(left)
    eq_data = {}
    eq_data['name'] = left['name']
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
        if eq not in ref:
            continue
        ref_e = ref[eq]
        eq_dev = {}
        for label in e:
            if not isinstance(e[label], str):
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

def plot_eq(eq_data, scale=-1.0):
    plt.rc('font', size=12)
    plt_lines = []
    labels = []
    #print(ys)
    x = eq_data['x']
    print('x', x)
    fig, ax = plt.subplots()
    for label in eq_data:
        if label == 'x' or label == 'name' or label == 'tag':
            continue
        print('plot ', label)
        l, = ax.plot(x, eq_data[label]*scale)
        plt_lines.append(l)
        labels.append(label)
    ax.set_xlabel('R / $\AA$')
    ax.set_ylabel('E / kcal/mol')
    ymin = (eq_data['pbe']*scale).min() - 0.5
    ax.set_ylim(ymin, 1.0)
    ax.legend(handles = plt_lines, labels = labels)
    #if show:
    #    plt.show()
    #print("save figure to %s.png" % datafile)
    fig.savefig('%s.png'%eq_data['name'])


def interp_plot(ax, x, y, label):
    l, = ax.plot(x, y, label=label)
    return l

if __name__ == '__main__':
    args = p.parse_args()
    shelf = args.input
    mode = args.mode
    toml = args.toml
    verbose = args.verbose
    if mode == 'curve':
        get_curve_eq(shelf, toml, mode, ilabelset=args.labelset, 
                     unit=args.unit, xunit=args.xunit, plot=args.plot, verbose=verbose)
    elif mode == 'none':
        get_elabel(shelf)
    else:
        get_eq_energy(shelf, toml, mode, ilabelset=args.labelset)
