from sxl.spacetime import *
from sxl.einstein import *
from sympy import *

coords = Coordinates("t r phi theta")
t, r, th, p = coords.coordinate_symbols
c, G, M = symbols("c G M")
schwarzschild = 1 - (2 * G * M)/(r * c**2)
metric = MetricTensor([
	[c**2, 0, 0, 0],
	[0, -1, 0, 0],
	[0, 0, -r**2, 0],
	[0, 0, 0, -r**2 * sin(th)**2]
], coords)

manifold = Manifold(metric)

manifold.define(ChristoffelSymbols)

pprint(metric.co_diff(1, 0, 0))

manifold.of(ChristoffelSymbols).solve()
pprint(manifold.of(ChristoffelSymbols).mixed()[0])
pprint(manifold.of(ChristoffelSymbols).mixed()[1])
pprint(manifold.of(ChristoffelSymbols).mixed()[2])
pprint(manifold.of(ChristoffelSymbols).mixed()[3])