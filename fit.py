#!/usr/bin/env python
import tomli
import shelve
import sys
from statutil import suDataDB, to_unit

LABELS = ['suhf', 'pbe', 'pbe0', 'pbe02', 
          ('pbe', 0.25, 2.5),
          ('pbe', 0.25, 3.0),
          ('pbe', 0.2, 2.0),
          ('pbe', 0.2, 2.5),
          ('pbe', 0.2, 3.0)
          ]
def toml_load(toml, domain):
    with open(toml, 'rb') as f:
        equations = tomli.load(f)[domain]
    return equations

def get_eq_energy(shelf, toml):
    '''
    energy for some equation like B2 -> B + B
    '''
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
    e_data = update_elabel(e_data, labels=LABELS)
    eq_energy = {}
    for eq in equations:
        left_spc = eq
        right_spc = parse_eq(equations[eq])
        print(left_spc, right_spc)
        if eq not in e_data:
            raise ValueError('eq %s not in e_data'%eq)
        left_data = e_data[eq]
        right_data = [e_data[s] for s in right_spc]
        eq_data = sub_eq(left_data, right_data, labels=LABELS, unit='kcal')
        print(eq_data)
        eq_energy[eq] = eq_data
    eq_deviation = sub_ref(eq_energy, ref)
    #print(eq_deviation)
    return eq_energy
        

def parse_eq(eq):
    spc = eq.split('+')
    return spc

def sub_eq(left, right, labels=['suhf'], unit='au'):
    '''
    left: dict
    right: list of dict
    '''
    #print(left)
    eq_data = {}
    scal = to_unit(unit)
    for label in labels:
        left_e = left[label]
        right_e = sum([r[label] for r in right])
        eq_e = right_e - left_e
        eq_data[label] = eq_e*scal
    return eq_data

def sub_ref(eq_e, ref):
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
        print(eq)
        dump_dev(eq_dev)
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

def dump_dev(dev):
    p02, p025, p03 = dev['pbe02'], dev[('pbe', 0.25, 2.5)], dev[('pbe', 0.25, 3.0)]
    pm2, pm25, pm3 = dev[('pbe', 0.2, 2.0)], dev[('pbe', 0.2, 2.5)], dev[('pbe', 0.2, 3.0)]
    print("%.3f %.3f %.3f" % (p02, p025, p03))
    print("%.3f %.3f %.3f" % (pm2, pm25, pm3))

if __name__ == '__main__':
    get_eq_energy(sys.argv[1], sys.argv[2])