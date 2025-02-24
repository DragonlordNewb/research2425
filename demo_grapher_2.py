import numpy as np
import matplotlib.pyplot as plt

# Define a function that oscillates sharply and is symmetric about the y-axis
def g(x):
    return np.cos(2 * np.pi * x / 5) * np.exp(-0.5 * x**2 / 5)

# Generate x values
x_values = np.linspace(-5, 5, 300)
y_values = g(x_values)

# Find zero crossings
zero_crossings = x_values[np.where(np.diff(np.sign(y_values)))[0]]
if len(zero_crossings) >= 2:
    x_min_zero, x_max_zero = zero_crossings[0], zero_crossings[-1]
else:
    x_min_zero, x_max_zero = -5, 5  # Fallback in case of issues

# Apply cutoff to the function inside the zero-crossing region
modified_y_values = np.where((x_values >= x_min_zero) & (x_values <= x_max_zero), 0, y_values)

# Create the plot
fig, ax = plt.subplots(figsize=(8, 6))
ax.plot(x_values, modified_y_values, label="Energy density")
ax.axhline(0, color='black', linewidth=0.8)  # X-axis
ax.axvline(0, color='black', linewidth=0.8)  # Y-axis
ax.set_title("Stabilized warp drive energy densities (example)")
ax.set_xlabel("r")
ax.set_ylabel("U")
ax.legend()

# Cross-hatch the negative region
ax.fill_between(x_values, y_values, where=(x_values >= x_min_zero) & (x_values <= x_max_zero),
                color='red', alpha=0.1, hatch='//', label="Effects of stabilization")
ax.legend()

plt.show()
