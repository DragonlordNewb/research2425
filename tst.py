from sxl.spacetime import *
from sxl.einstein import *
from sympy import *
import sympy

coords = Coordinates("t r z")
t, r, z = coords.coordinate_symbols
c, G, M = symbols("c G M")
a1, b1, a2, b2 = symbols("a1 b1 a2 b2")
sch = 1 - (2*G*M)/(r * c**2)
alpha = Function("alpha")(r)
chi = Function("chi")(r)
metric = MetricTensor([
	[alpha, 0, 0],
	[0, -1/alpha, 0],
	[0, 0, -r**2],
], coords)

manifold = Manifold(metric)

manifold.define(ChristoffelSymbols)
manifold.define(RiemannTensor)
manifold.define(RicciTensor)
manifold.define(RicciScalar)
manifold.define(EinsteinTensor)

ein = manifold.of(EinsteinTensor)

print("\n" * 4)
for i in range(4):
	sympy.pprint(ein.contra(i, i))
	input()
	print("\n" * 4)

# sympy.pprint(ein.contra(0, 0)*metric.co(0, 0) + ein.contra(1, 1)*metric.co(1, 1) + ein.contra(2, 2)*metric.co(2, 2))

# for i in range(4):
# 	for j in range(4):
# 		for k in range(4):
# 			for l in range(4):
# 				print(i, j, k, l)
# 				pprint(manifold.of(RiemannTensor).mixed(i, j, k, l))
# 				print()