import shelve

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
        raise ValueError('inconsistent shape of ys and series')
    for s,i in enumerate(series):
        curve_series[s] = ys[:,i]
    d = shelve.open(shelfname)
    d['serie_%s.%s'%(molname,tag)] = curve_series
    d.close()
