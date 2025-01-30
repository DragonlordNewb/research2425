from sxl.spacetime import *
from sxl.einstein import *
from sympy import *

coords = Coordinates("t x y z")
t, x, y, z = coords.coordinate_symbols
c = Symbol("c")
phi = Function("phi")(t, x, y, z)
metric = MetricTensor([
	[c**2, phi/2, 0, 0],
	[phi/2, -1, 0, 0],
	[0, 0, -1, 0],
	[0, 0, 0, -1]
], coords)

manifold = Manifold(metric)

manifold.define(ChristoffelSymbols)
manifold.define(RiemannTensor)
manifold.define(RicciTensor)
manifold.define(RicciScalar)
manifold.define(EinsteinTensor)

pprint(manifold.of(EinsteinTensor).contra())