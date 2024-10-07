import sxl
import sympy

# https://f.yukterez.net/einstein.equations/files/8.html#transformation

units = sxl.spacetime.UnitSystem.si_ncc()
coords = sxl.spacetime.CoordinateSystem.trtp()
metric = sxl.spacetime.MetricTensor.lvfd_txyz(units)
st = sxl.spacetime.Spacetime(metric, units)

st.solve()

sympy.pprint(st.stress_energy_momentum_tensor.stress_energy_momentum_tensor_uu)