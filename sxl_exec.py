import sxl
import sympy

# https://f.yukterez.net/einstein.equations/files/8.html#transformation

units = sxl.spacetime.UnitSystem.si_ncc()
coords = sxl.spacetime.CoordinateSystem.trtp()
metric = sxl.spacetime.MetricTensor.schwarzschild_txyz(units)
st = sxl.spacetime.Spacetime(metric, units)

# Calculate Christoffel symbols

st.christoffel_symbols.compute()
sympy.pprint(st.christoffel_symbols.christoffel_symbols_udd)

# Calculate Ricci tensor

st.ricci_tensor.compute()
sympy.pprint(st.ricci_tensor.ricci_tensor_dd)

# Calculate Einstein tensor

st.einstein_tensor.compute()
sympy.pprint(st.einstein_tensor.einstein_tensor_dd)