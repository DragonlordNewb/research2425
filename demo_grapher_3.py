import numpy as np
import matplotlib.pyplot as plt

# Define a piecewise function for the new graph
def f(x):
    if abs(x) <= 2:
        return 1
    elif 2 < abs(x) <= 4:
        return (4 - abs(x)) / 2
    else:
        return 0

# Generate x values
x_values = np.linspace(-5, 5, 300)
y_values = np.array([f(x) for x in x_values])

# Create the plot
fig, ax = plt.subplots(figsize=(8, 6))
ax.plot(x_values, y_values, label="Piecewise Symmetric Graph", color='blue')
ax.axhline(0, color='black', linewidth=0.8)  # X-axis
ax.axvline(0, color='black', linewidth=0.8)  # Y-axis
ax.set_title("Symmetric Piecewise Function with Three Regions")
ax.set_ylabel("f")
ax.set_xticklabels([])  # Remove x-axis numbers

# Shade the three regions
ax.fill_between(x_values, y_values, where=(abs(x_values) <= 2), color='green', alpha=0.3, label="Flat Central Region")
ax.fill_between(x_values, y_values, where=(2 < abs(x_values)) & (abs(x_values) <= 4), color='orange', alpha=0.3, label="Sloped Regions")
ax.fill_between(x_values, y_values, where=(abs(x_values) > 3.75), color='red', alpha=0.3, label="Outer Zero Regions")

# Add vertical lines at transitions
for x_pos in [-3.75, -2, 2, 3.75]:
    ax.axvline(x_pos, color='black', linestyle='dashed', linewidth=1)

ax.axhline(1, color="black", linestyle="dashed", linewidth=1)

# Annotate regions
ax.text(1, 0.5, "Isochronal\nRegion", fontsize=12, ha='center', color='black')  # Central region
ax.text(-3, 0.9, "Subchronal\nRegion", fontsize=10, ha='center', color='black')  # Left sloped region
ax.text(3, 0.9, "Subchronal\nRegion", fontsize=10, ha='center', color='black')  # Right sloped region
ax.text(-4.7, 0.3, "Achronal\nRegion\n(elsewhere)", fontsize=10, ha='center', color='black')  # Left outer region
ax.text(4.7, 0.3, "Achronal\nRegion\n(elsewhere)", fontsize=10, ha='center', color='black')  # Right outer region

ax.text(-3.75, -0.1, "Inverted event horizon")

plt.show()