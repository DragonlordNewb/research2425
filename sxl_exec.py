import sxl
import sympy

# https://f.yukterez.net/einstein.equations/files/8.html#transformation

units = sxl.spacetime.UnitSystem.si_ncc()
coords = sxl.spacetime.CoordinateSystem.trtp()
metric = sxl.spacetime.MetricTensor.schwarzschild_trtp(units)
st = sxl.spacetime.Spacetime(metric, units)

# Calculate Christoffel symbols

st.christoffel_symbols.compute()
sympy.pprint(st.christoffel_symbols.christoffel_symbols_udd)

# Calculate Riemann  tensor

st.riemann_tensor.compute()
sympy.pprint(st.riemann_tensor.riemann_tensor_uddd)

# Calculate Ricci tensor

st.ricci_tensor.compute()
sympy.pprint(st.ricci_tensor.ricci_tensor_dd)
sympy.pprint(st.ricci_tensor.ricci_scalar)

# Calculate Einstein tensor

st.einstein_tensor.compute()
st.stress_energy_momentum_tensor.compute()
sympy.pprint(st.stress_energy_momentum_tensor.stress_energy_momentum_tensor_uu)