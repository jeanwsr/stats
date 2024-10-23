from scipy.interpolate import make_interp_spline as spl
from scipy.optimize import root
import sys

def spline_findmin(x, y):
    f = spl(x, y, k=3)
    xroot, yroot = findmin(f, x)
    return f, (xroot, yroot)


def spline(x, y):
    f = spl(x, y, k=3)
    return f

def findmin(f, x):
    res = root(f.derivative(), x[2])
    return res.x, f(res.x)