import sxl
import sympy

# https://f.yukterez.net/einstein.equations/files/8.html#transformation

units = sxl.spacetime.UnitSystem.si_ncc()
coords = sxl.spacetime.CoordinateSystem.trtp()
metric = sxl.spacetime.MetricTensor.schwarzschild_trtp(units)
st = sxl.spacetime.Spacetime(metric, units, M=1000)

st.solve()

print()

print("Christoffel symbols of the second kind:")

sympy.pprint(st.christoffel_symbols.christoffel_symbols_udd)