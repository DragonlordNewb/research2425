from sxl.spacetime.spacetime import *

si_units = UnitSystem(False, False, False, False)
si_units_ncc = UnitSystem(False, False, False, True)
cGh_units = UnitSystem(True, True, True, True)

coordinates_txyz = CoordinateSystem("t", "x", "y", "z")
coordinates_trtp = CoordinateSystem("t", "r", "theta", "phi")
coordinates_trtz = CoordinateSystem("t", "r", "t", "z")

metric_Minkowski_txyz = lambda units: MetricTensor(coordinates_txyz, [[units.c**2, 0, 0, 0], [0, -1, 0, 0], [0, 0, -1, 0], [0, 0, 0, -1]])
metric_Minkowski_trtp = lambda units: MetricTensor(coordinates_trtp, [[units.c**2, 0, 0, 0], [0, -1, 0, 0], [0, 0, -coordinates_trtp.x1**2, 0], [0, 0, 0, -(coordinates_trtp.x1**2 * sympy.sin(coordinates_trtp.x2)**2)]])

M = sympy.Symbol("M")
P = sympy.Function("phi")(*coordinates_txyz.x)
txyz_r = sympy.sqrt(sum(coordinates_txyz.x[i]**2 for i in (1, 2, 3)))

txyz_Schwarzschild = lambda units: (1 - 2*units.G*M/(txyz_r * units.c**2))
trtp_Schwarzschild = lambda units: (1 - 2*units.G*M/(coordinates_trtp.x1 * units.c**2))
metric_Schwarzschild_txyz = lambda units: MetricTensor(coordinates_txyz, [
	[txyz_Schwarzschild(units) * units.c**2, 0, 0, 0],
	[0, -1/txyz_Schwarzschild(units), 0, 0],
	[0, 0, -1/txyz_Schwarzschild(units), 0],
	[0, 0, 0, -1/txyz_Schwarzschild(units)]
])
metric_Schwarzschild_trtp = lambda units: MetricTensor(coordinates_trtp, [
	[trtp_Schwarzschild(units) * units.c**2, 0, 0, 0],
	[0, -trtp_Schwarzschild(units), 0, 0],
	[0, 0, -coordinates_trtp.x1**2, 0],
	[0, 0, 0, -(coordinates_trtp.x1**2 * sympy.sin(coordinates_trtp.x2)**2)]
])

metric_gms = lambda units: MetricTensor(coordinates_txyz, [
	[units.c**2, P/2, 0, 0],
	[P/2, -1, 0, 0],
	[0, 0, -1, 0],
	[0, 0, 0, -1]
])