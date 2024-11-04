import sxl
import sympy

# https://f.yukterez.net/einstein.equations/files/8.html#transformation

units = sxl.spacetime.UnitSystem.si_ncc()
coords = sxl.spacetime.CoordinateSystem.trtp()
metric = sxl.spacetime.MetricTensor.lvlf_txyz(units)
st = sxl.spacetime.Spacetime(metric, units)

st.solve()

print()

print("Christoffel symbols of the second kind:")

alpha = units.c**2 + sympy.Symbol("v")*sympy.Function("phi")(*coords.coordinates)

sympy.pprint(st.christoffel_symbols.christoffel_symbols_udd)
sympy.pprint(st.christoffel_symbols.udd(0, 0, 0).subs(sympy.Function("v_s")(coords.x(0)), sympy.Symbol("v")).subs(alpha, sympy.Symbol("alpha")))