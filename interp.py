from scipy.interpolate import make_interp_spline as spl
from scipy.optimize import root
import sys

def spline_findmin(x, y):
    f = spl(x, y, k=3)
    deriv = f.derivative()
    res = root(deriv, x[2])
    yroot = f(res.x)
    return f, (res.x, yroot)


