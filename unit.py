
def get_unit(line):
    unit = None
    if 'ev' in line.lower():
        unit = 'eV'
    elif 'kcal' in line.lower():
        unit = 'kcal'
    elif 'au' in line.lower():
        unit = 'au'
    elif 'mh' in line.lower():
        unit = 'mha'
    else:
        print("unit not recognized in res file, use kcal")
        unit = 'kcal'
    return unit

energy_unit_base = {
    'au': 1.0,
    'eV': 1/27.211386,
    'kcal': 1/627.509474,
    'mha': 1.0e-3
}

def scal_factor(dataunit, target_unit):
    if dataunit == target_unit:
        return 1.0
    if dataunit not in energy_unit_base:
        raise NotImplementedError("unit not supported: %s"%dataunit)
    scal = energy_unit_base[dataunit] / energy_unit_base[target_unit]
    return scal
