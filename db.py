import shelve
import numpy as np

def save_from_txt(datafile, shelfname, molname, tag='none'):
    from plot import datafile
    x, ys, series, dataunit = get_curves(datafile)
    save(x, ys, series, shelfname, molname, tag)

def save(x, ys, series, shelfname, molname, tag='none'):
    curve_series = {}
    curve_series['name'] = molname
    curve_series['tag'] = tag
    curve_series['x'] = x
    if ys.shape[1] != len(series):
        raise ValueError('inconsistent shape of ys and series: ys ', ys.shape, ' series ', len(series))
    for i,s in enumerate(series):
        #print(s,i)
        curve_series[s] = ys[:,i]
    d = shelve.open(shelfname)
    d['serie_%s.%s'%(molname,tag)] = curve_series
    d.close()

def save_spc(ys, series, shelfname, molname, tag='none', x=None):
    curve_series = {}
    curve_series['name'] = molname
    curve_series['tag'] = tag
    if x is not None:
        curve_series['x'] = x
    if len(ys) != len(series):
        raise ValueError('inconsistent shape of ys and series: ys ', ys.shape, ' series ', len(series))
    for i,s in enumerate(series):
        #print(s,i)
        curve_series[s] = ys[i]
    d = shelve.open(shelfname)
    d['spc_%s.%s'%(molname,tag)] = curve_series
    d.close()

def dump(serie, short=False):
    np.set_printoptions(linewidth=400)
    print("name: %s tag: %s"%(serie['name'], serie['tag']))
    x = serie['x']
    if short:
        x_noatom = [xi for xi in x if xi > 0.0]
        print("len(x): %d"%len(x_noatom), "x_noatom: ", x_noatom)
    else:
        print("x: ", x)
        for k in serie.keys():
            if k not in ['name', 'tag', 'x']:
                print("%s: "%k, serie[k])

def dump_spc(spc, short=False):
    print("name: %s tag: %s"%(spc['name'], spc['tag']))
    if short:
        #print("len(x): %d"%len(spc['x']))
        pass
    else:
        #print("x: ", spc['x'])
        for k in spc.keys():
            if k not in ['name', 'tag']:
                print("%s: "%k, spc[k])
