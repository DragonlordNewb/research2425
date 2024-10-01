from sxl.util import tp

tp("Loading Spacetime Exploration Library ...")

import sxl.spacetime
import sxl.spacetime.instances

print("done.\nSetting up Minkowski geometry ...")
tp("  Loading unit system ...")

units = sxl.spacetime.instances.si_units

tp("done.\n  Loading metric ...")

metric = sxl.spacetime.instances.metric_Minkowski_txyz(units)

tp("done.\n  Setting up spacetime ...")

st = sxl.spacetime.Spacetime(metric, units)

print("done.")
print("Spacetime configured.")

for i in range(4):
    for j in range(4):
        print("stress-energy component", i, j, ": ", st.stress_energy_momentum.get_uu(i, j))