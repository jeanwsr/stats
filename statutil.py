
import subprocess

class suData():
    def __init__(self, data, mode):
        shift = 0
        if 'dd' in mode:
            shift += 7
        #if 'mc' in mode:
        #    shift += 9
        self.suhf = float(data[0])
        self.j = float(data[3])
        self.k = float(data[4])
        self.c = float(data[5])
        if 'dd' in mode:
            self.ddxc = float(data[6])
        self.otx = float(data[6+shift])
        self.otc = float(data[7+shift])
        self.otxc = float(data[8+shift])

    def series(self):
        return ['suhf', 'j', 'k', 'c', 'ddxc', 'otx', 'otc', 'otxc']
    
    def res(self):
        if getattr(self, 'ddxc', None) is None: self.ddxc = 0.0
        return [self.suhf, self.j, self.k, self.c, self.ddxc, self.otx, self.otc, self.otxc]
    
    def sudd(self, hyb):
        if hasattr(self, 'ddxc'):
            return self.suhf + (self.ddxc - self.k - self.c)*(1.0-hyb)
        else:
            return 0.0
    def supd(self, hyb):
        return self.suhf + (self.otxc - self.k - self.c)*(1.0-hyb)
    def supd_k(self, hyb, k):
        return self.suhf + (self.otx - self.k - self.c)*(1.0-hyb) + (1.0-hyb**k)*self.otc
    
    def get_elabels(self, labels):
        elabels = {}
        for label in labels:
            if isinstance(label, str):
                h, k = FUN_param[label]
            elif isinstance(label, tuple):
                h, k = label[1], label[2]
            elabels[label] = self.supd_k(h, k)
        return elabels

class suDataDB(suData):
    def __init__(self, datadict):
        self.__dict__.update(datadict)

def runcmd(cmd):
    p = subprocess.Popen(cmd, 
         shell=True,
         stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
         encoding='utf-8').communicate()[0]
    return p

FUN_param = {
    'suhf': [1.0, 1.0],
    'pbe': [0.0, 1.0],
    'pbe0': [0.25, 1.0],
    'pbe02': [0.25, 2.0],
    'blyp': [0.0, 1.0],
    'b3lyp': [0.2,1.0],
    'blyp02': [0.2,2.0]
}

def get_param(fun):
    return FUN_param[fun.lower()]

def to_unit(unit):
    Ha2ev = 27.211386
    Ha2kcal = 627.509474
    if unit.lower() == 'kcal':
        return Ha2kcal
    elif unit.lower() == 'ev':
        return Ha2ev
    elif unit.lower() == 'au':
        return 1.0
    else:
        raise ValueError("unit not recognized")
