import sxl
import sympy

# https://f.yukterez.net/einstein.equations/files/8.html#transformation

units = sxl.spacetime.UnitSystem.si_ncc()
metric = sxl.spacetime.MetricTensor.minkowski_trtp(units)
spacetime = sxl.spacetime.Spacetime(metric, units)
spacetime.christoffel_symbols.compute()
spacetime.riemann_tensor.compute_uddd()
sympy.pprint(spacetime.riemann_tensor.riemann_tensor_uddd)
sympy.pprint(spacetime.christoffel_symbols.christoffel_symbols_udd)
