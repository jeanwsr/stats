from scipy.interpolate import make_interp_spline as spl
from scipy.optimize import root
import sys

def spline_findmin(x, y):
    f = spl(x, y, k=3)
    deriv = f.derivative()
    res = root(deriv, x[2])
    print('root:    %.6f' %res.x)
    print('y(root): %.6f' %f(res.x))
    return res.x

