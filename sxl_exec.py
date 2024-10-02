import sxl
import sympy

# https://f.yukterez.net/einstein.equations/files/8.html#transformation

units = sxl.spacetime.UnitSystem.si()
metric = sxl.spacetime.MetricTensor.minkowski_txyz(units)
spacetime = sxl.spacetime.Spacetime(metric, units)
spacetime.stress_energy_momentum_tensor.compute_uu()
sympy.pprint(spacetime.stress_energy_momentum_tensor.stress_energy_momentum_tensor_uu)