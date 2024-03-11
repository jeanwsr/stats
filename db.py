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

def dump(serie):
    np.set_printoptions(linewidth=400)
    print("name: %s tag: %s"%(serie['name'], serie['tag']))
    print("x: ", serie['x'])
    for k in serie.keys():
        if k not in ['name', 'tag', 'x']:
            print("%s: "%k, serie[k])
