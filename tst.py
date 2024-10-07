from sxl.spacetime import GeneralFourVector as GFV
from sxl.spacetime import MetricTensor as MT
from sxl.spacetime import UnitSystem as US

m = MT.minkowski_txyz(US.natural_ncc())

X = GFV(m, "u", 1, 2, 3, 4)
Y = GFV(m, "u", 2, 3, 4, 5)
Z = GFV(m, "d", 5, 1, 1, 1)
print(X)
print(Y)
print(X + Y)
print(Z)