import numpy as np
import matplotlib.pyplot as plt

# Define a function that oscillates sharply and is symmetric about the y-axis
def g(x):
    return np.cos(2 * np.pi * x / 5) * np.exp(-0.5 * x**2 / 5)

# Generate x values
x_values = np.linspace(-5, 5, 300)
y_values = g(x_values)

# Create the plot
fig, ax = plt.subplots(figsize=(8, 6))
ax.plot(x_values, y_values, label="Energy densities")
ax.axhline(0, color='black', linewidth=0.8)  # X-axis
ax.axvline(0, color='black', linewidth=0.8)  # Y-axis
ax.set_title("Warp drive energy densities (example)")
ax.set_xlabel("r")
ax.set_ylabel("U")
ax.legend()

# Find zero crossings
zero_crossings = x_values[np.where(np.diff(np.sign(y_values)))[0]]


# Shade negative regions
ax.fill_between(x_values, y_values, where=(y_values < 0), color='red', alpha=0.3, label="WEC violations")
ax.legend()

plt.show()
