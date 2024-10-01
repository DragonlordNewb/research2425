from sxl.spacetime.spacetime import *

si_units = UnitSystem(False, False, False, False)
cGh_units = UnitSystem(True, True, True, True)

coordinates_txyz = CoordinateSystem("t", "x", "y", "z")
coordinates_trtp = CoordinateSystem("t", "r", "theta", "phi")
coordinates_trtz = CoordinateSystem("t", "r", "t", "z")

metric_Minkowski_txyz = lambda units: MetricTensor(coordinates_txyz, [[units.c**2, 0, 0, 0], [0, -1, 0, 0], [0, 0, -1, 0], [0, 0, 0, -1]])
metric_Minkowski_trtp = lambda units: MetricTensor(coordinates_trtp, [[units.c**2, 0, 0, 0], [0, -1, 0, 0], [0, 0, -r**2, 0], [0, 0, 0, -(r**2 * sympy.sin(coordinates_trtp.x2)**2)]])