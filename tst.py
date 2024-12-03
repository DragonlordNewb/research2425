from sxl.spacetime import *
from sxl.einstein import *
from sympy import *

coords = Coordinates("t r phi theta")
t, r, th, p = coords.coordinate_symbols
c, G, M = symbols("c G M")
schwarzschild = 1 - (2 * G * M)/(r * c**2)
alpha = Function("alpha")(t, r)
metric = MetricTensor([
	[c**2, alpha, 0, 0, 0],
	[0, -1, 0, 0],
	[0, 0, -r**2, 0],
	[0, 0, 0, -r**2 * sin(th)**2]
], coords)

manifold = Manifold(metric)

manifold.define(ChristoffelSymbols)
manifold.define(RiemannTensor)
manifold.define(RicciTensor)
manifold.define(RicciScalar)
manifold.define(EinsteinTensor)