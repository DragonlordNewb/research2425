from sxl import spacetime
from sxl import einstein

coordinates = spacetime.Coordinates("t", "x", "y", "z")
t, x, y, z = coordinates.x(0), coordinates.x(1), coordinates.x(2), coordinates.x(3)
c = spacetime.Symbol("c")
H = spacetime.Function("H")(x, y, z - c*t)

metric = spacetime.MetricTensor([
	[c**2 - H/2, 0, 0, H/2],
	[0, -1, 0, 0],
	[0, 0, -1, 0],
	[H/2, 0, 0, -1 - H/2]
], coordinates)

mf = spacetime.Manifold(metric)

mf.define(einstein.ChristoffelSymbols)
mf.define(einstein.RiemannTensor)
mf.define(einstein.RicciTensor)
mf.define(einstein.RicciScalar)
mf.define(einstein.EinsteinTensor)
G = mf.of(einstein.EinsteinTensor)
for i in range(4):
	for j in range(4):
		print(i, j, G.co(i, j))