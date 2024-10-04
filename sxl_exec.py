import sxl
import sympy

# https://f.yukterez.net/einstein.equations/files/8.html#transformation

units = sxl.spacetime.UnitSystem.si_ncc()
coords = sxl.spacetime.CoordinateSystem.trtp()
metric = sxl.spacetime.MetricTensor.minkowski_trtp(units)
spacetime = sxl.spacetime.Spacetime(metric, units)

# Calculate Christoffel symbols

spacetime.christoffel_symbols.compute()
sympy.pprint(spacetime.christoffel_symbols.christoffel_symbols_udd)

# Calculate Ricci tensor

spacetime.ricci_tensor.compute()
sympy.pprint(spacetime.ricci_tensor.ricci_tensor_dd)