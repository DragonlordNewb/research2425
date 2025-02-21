import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def linear_drive(R, Z, c, V):
	numerator = (- (R**2 * V**4 * Z**2) - (5 * R**6 * V**4) - (3 * R**4 * V**4 * Z**2) 
				 + (11 * R**4 * V**4) + (6 * V**2 * c**2) + (5 * V**2 * c**2 * Z**2) 
				 - (4 * R**2 * V**4) - (13 * R**2 * V**2 * c**2))
	
	denominator = (R**2 * V**2 - c**2 - R**4 * V**2) ** 3

	return numerator / denominator

def linear_stat(R, Z, c, V):
	numerator1 = -V**2 * (7*V**4*c**2*R**2 - 4*V**2*c**4 - 3*V**6*R**4 - V**6*Z**2*R**6 \
						 + 3*V**4*c**2*Z**2*R**4 + 10*V**6*R**6 - 5*V**2*c**4*Z**2 - 4*V**6*Z**2*R**4 \
						 - V**4*c**2*Z**2 + V**6*Z**2*R**2 + 8*V**4*c**2*Z**2*R**2 - 22*V**4*c**2*R**4 \
						 - 5*V**6*R**8 + 13*V**2*c**4*R**2 + 5*V**4*c**2*R**6)
	
	numerator2 = -2 * V * (10*V**5*R**6 - 11*V**3*c**2*R**4 - 3*V**5*R**4 + 7*V**3*c**2*Z**2*R**2 \
						   + V**5*Z**2*R**2 - V**3*c**2*Z**2 - 5*V**5*R**8 - V**5*Z**2*R**6 \
						   - 4*V**5*Z**2*R**4 + 2*V*c**4 + 3*V**3*c**2*R**2)
	
	numerator3 = -(11*V**4*R**4 - V**4*Z**2*R**2 - 5*V**4*R**6 - 13*V**2*c**2*R**2 - 4*V**4*R**2 \
				  + 5*V**2*c**2*Z**2 + 6*V**2*c**2 - 3*V**4*Z**2*R**4)
	
	denominator = (c**2 - V**2*R**2 + V**2*R**4)**3
	
	result = (numerator1 + numerator2 + numerator3) / denominator
	
	return result

#
#
#
#
#

# Parameters
a, b, c, V = 1.0, 1.0, 1.0, 1.0
lim = 2
x_min, x_max = -lim, lim
z_min, z_max = -lim, lim
x_values = np.linspace(x_min, x_max, 100)
z_values = np.linspace(z_min, z_max, 100)
X, Z = np.meshgrid(x_values, z_values)

C = 1000

def cartesify(fn):
	def decorated(x, z, c=1, V=1):
		R = x**2 + z**2 + 0 # y=0
		Z = z
		return fn(R, Z, c, V)
	return decorated

# Compute function values

BLOCK_1_SELECTOR = linear_drive
BLOCK_2_SELECTOR = linear_stat

F1 = cartesify(BLOCK_1_SELECTOR)
F2 = cartesify(BLOCK_2_SELECTOR)

fig, axes = plt.subplots(2, 3, figsize=(18, 9), subplot_kw={'projection': None})
fig.suptitle("Energy Density Profiles in Two Reference Frames")

# --- Colormap (heatmap) ---
ax1 = axes[0, 0] # fig.add_subplot(2, 3, 1)
cmap_plot = ax1.contourf(X, Z, F1(X, Z), levels=50, cmap='plasma')
plt.colorbar(cmap_plot, ax=ax1)
ax1.set_title("Colormap of xz Slice")
ax1.set_xlabel("x")
ax1.set_ylabel("z")

zero_contour1 = ax1.contour(X, Z, F1(X, Z), levels=[0], colors='cyan', linewidths=1)
ax1.clabel(zero_contour1, fmt='%.2f', colors='white', fontsize=10)

# --- 3D Surface Plot ---
ax2 = fig.add_subplot(2, 3, 2, projection='3d')
ax2.plot_surface(X, Z, F1(X, Z), cmap='plasma')
ax2.set_title("3D Surface Plot")
ax2.set_xlabel("x")
ax2.set_ylabel("z")
ax2.set_zlabel("f(x, z)")

# --- 2D Line Plot ---
z_fixed = 0  # Fix z for line plot
F1_x = F1(x_values, z_fixed)
ax3 = axes[0, 2] # fig.add_subplot(2, 3, 3)
ax3.plot(x_values, F1_x, label=f"z={z_fixed}")
ax3.set_title("2D Line Plot Along x")
ax3.set_xlabel("x")
ax3.set_ylabel("f(x, z_fixed)")
ax3.legend()

ax3.axhline(y=0, color='r', linestyle='--', label='0')



ax4 = axes[1, 0] # fig.add_subplot(2, 3, 4)
cmap_plot2 = ax4.contourf(X, Z, F2(X, Z), levels=50, cmap='plasma')
plt.colorbar(cmap_plot2, ax=ax4)
ax4.set_title("Colormap in Second Frame")
ax4.set_xlabel("x")
ax4.set_ylabel("z")

zero_contour2 = ax4.contour(X, Z, F2(X, Z), levels=[0], colors='cyan', linewidths=1)
ax4.clabel(zero_contour2, fmt='%.2f', colors='white', fontsize=10)

ax5 = fig.add_subplot(2, 3, 5, projection='3d')
ax5.plot_surface(X, Z, F2(X, Z), cmap='plasma')
ax5.set_title("3D Surface Plot in Second Frame")
ax5.set_xlabel("x")
ax5.set_ylabel("z")
ax5.set_zlabel("f(x, z)")


F2_x = F2(x_values, z_fixed)  # Modify for second frame
ax6 = axes[1, 2] # fig.add_subplot(2, 3, 6)
ax6.plot(x_values, F2_x, label=f"z={z_fixed}", color='red')
ax6.set_title("2D Line Plot in Second Frame")
ax6.set_xlabel("x")
ax6.set_ylabel("f(x, z_fixed)")
ax6.legend()

ax6.axhline(y=0, color='b', linestyle='--', label='0')

plt.tight_layout()
plt.show()
