from sxl.spacetime import GeneralFourVector as GFV
from sxl.spacetime import MetricTensor as MT
from sxl.spacetime import UnitSystem as US

m = MT.minkowski_txyz(US.si_ncc())

X = GFV(m, "u", 1, 2, 3, 4)
Y = GFV(m, "u", 2, 3, 4, 5)
print(X.d(0), X.d(1), X.d(2), X.d(3))
print(X)
print(Y)
print(X + Y)
