
import subprocess
import numpy as np

class suData():
    def __init__(self, data, mode, occdata=None):
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
        if occdata is not None:
            if isinstance(occdata, list):
                self.natocc = [float(n) for n in occdata]
            elif isinstance(occdata, tuple):
                self.natocc_a = [float(n) for n in occdata[0]] 
                self.natocc_b = [float(n) for n in occdata[1]]
            self.ent = self.ent()

    def series(self):
        return ['suhf', 'j', 'k', 'c', 'ddxc', 'otx', 'otc', 'otxc', 'ent']
    
    def res(self):
        if getattr(self, 'ddxc', None) is None: self.ddxc = 0.0
        if getattr(self, 'ent', None) is None: self.ent = 0.0
        return [self.suhf, self.j, self.k, self.c, self.ddxc, self.otx, self.otc, self.otxc, self.ent]
    
    def sudd(self, hyb):
        if hasattr(self, 'ddxc'):
            return self.suhf + (self.ddxc - self.k - self.c)*(1.0-hyb)
        else:
            return 0.0
    def supd(self, hyb):
        return self.suhf + (self.otxc - self.k - self.c)*(1.0-hyb)
    def supd_k(self, hyb, k):
        return self.suhf + (self.otx - self.k - self.c)*(1.0-hyb) + (1.0-hyb**k)*self.otc
    
    def supd_t(self, hyb, t):
        return self.suhf + (self.otx - self.k - self.c)*(1.0-hyb) + 1.0*self.otc - hyb*t*self.ent
    
    def only_ent(self, hyb, t):
        e = - hyb*t*self.ent
        return e
    
    def supd_p3(self, hyb, potk, potc):
        '''
        h*(k+c) + (1 - h + potk)*otk + (1 - h + potc)*otc
        '''
        return self.suhf + (self.otx + self.otc - self.k - self.c)*(1.0-hyb) + potk*self.otx + potc*self.otc

    def get_elabels(self, labels):
        elabels = {}
        for label in labels:
            if isinstance(label, str):
                h, k, t = FUN_param[label]
                #t = 0.0
                elabels[label] = self.supd_k(h, k)
                if 'ent' in label:
                    elabels[label] = self.only_ent(h, t)
            elif isinstance(label, tuple):
                if isinstance(label[1], float):
                    if len(label) == 3:
                        h, k = label[1], label[2]
                        t = 0.0
                        elabels[label] = self.supd_k(h, k)
                    elif len(label) == 4:
                        h, k, t = label[1], label[2], label[3]
                        elabels[label] = self.supd_t(h, t)
                    elif len(label) == 5:
                        h, k, t, (potk, potc) = label[1:]
                        #potk, potc = label[4]
                        elabels[label] = self.supd_p3(h, potk, potc)
                        #continue
                else:
                    if label[1] == 'p3':
                        h, potk, potc = label[2:]
                        elabels[label] = self.supd_p3(h, potk, potc)

            
        return elabels
    
    def ent(self):
        return get_ent(self.natocc_a) + get_ent(self.natocc_b)

class suDataDB(suData):
    def __init__(self, datadict):
        self.__dict__.update(datadict)

def runcmd(cmd):
    out, err = subprocess.Popen(cmd, 
         shell=True,
         stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
         encoding='utf-8').communicate()
    #print(cmd, out, err)
    return out

FUN_param = {
    'suhf': [1.0, 1.0, 0.0],
    'pbe': [0.0, 1.0, 0.0],
    'pbe0': [0.25, 1.0, 0.0],
    'pbe02': [0.25, 2.0, 0.0],
    'blyp': [0.0, 1.0, 0.0],
    'b3lyp': [0.2,1.0, 0.0],
    'blyp02': [0.2,2.0, 0.0],
    'ent5': [0.25, 0.0, 0.005]
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

def entropy_term(n, thr=1e-6):
    if n > 1.0 or n < 0.0:
        raise ValueError(f"n = {n}, must be in [0,1]")
    elif n > 1.0 - thr or n < thr:
        return 0.0
    else:
        return n*np.log(n) + (1-n)*np.log(1-n)

def get_ent(natocc):
    return sum([entropy_term(n) for n in natocc])

def split_method(taskfile):
    # split file into pieces by 'method:'
    linenumber = runcmd("grep 'method SU' %s -n | awk -F: '{print $1}'"%taskfile)
    linenumber = linenumber.split('\n')[:-1]
    #print(linenumber)
    pieces = []
    for i, n in enumerate(linenumber):
        start = int(n)-1
        start = str(start)
        if i == len(linenumber) - 1:
            end = '$'
        else:
            end = int(linenumber[i+1])-2
        end = str(end)
        piece = runcmd("sed -n '%s,%sp' %s > %s"%(start, end, taskfile, taskfile+start))
        pieces.append(taskfile+start)
    return pieces

