from sxl.spacetime import *
from sxl.einstein import *
from sympy import *

coords = Coordinates("t r theta phi")
t, r, th, ph = coords.coordinate_symbols
c, G, M = symbols("c G M")
schwarzschild = 1 - (2 * G * M)/(r * c**2)
alpha = Function("alpha")(t, r)
metric = MetricTensor([
	[schwarzschild, 0, 0, 0],
	[0, -1/schwarzschild, 0, 0],
	[0, 0, -r**2, 0],
	[0, 0, 0, -r**2 * sin(th)**2]
], coords)

manifold = Manifold(metric)

manifold.define(ChristoffelSymbols)
manifold.define(RiemannTensor)
manifold.define(RicciTensor)
manifold.define(RicciScalar)
manifold.define(EinsteinTensor)

for x in manifold.of(EinsteinTensor).tensor_contra:
	pprint(x)

# for i in range(4):
# 	for j in range(4):
# 		for k in range(4):
# 			for l in range(4):
# 				print(i, j, k, l)
# 				pprint(manifold.of(RiemannTensor).mixed(i, j, k, l))
# 				print()