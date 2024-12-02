import sxl
import sympy

# https://f.yukterez.net/einstein.equations/files/8.html#transformation

units = sxl.spacetime.UnitSystem.si_ncc()
coords = sxl.spacetime.CoordinateSystem.trtp()
metric = sxl.spacetime.MetricTensor.lf_simple(units)
st = sxl.spacetime.Spacetime(metric, units)

st.solve()

print()

print("Christoffel symbols of the second kind:")

alpha = units.c**2 + sympy.Symbol("v")*sympy.Function("phi")(*coords.coordinates)

sympy.pprint(st.ricci_tensor.ricci_tensor_uu)
input()
sympy.pprint(st.ricci_tensor.scalar())