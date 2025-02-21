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

def quadratic_drive(R, Z, c, V):
    numerator = (-6 * V**2 * c**2 + 4 * R**2 * V**4 - 5 * V**2 * c**2 * Z**2 +
                 3 * R**4 * V**4 * Z**2 + 13 * R**2 * V**2 * c**2 +
                 5 * R**6 * V**4 + R**2 * V**4 * Z**2 - 11 * R**4 * V**4)
    denominator = (R**4 * V**2 + c**2 - R**2 * V**2)**3
    return -numerator / denominator

def quadratic_stat(R, Z, c, V):
    numerator1 = (-6 * V**2 * c**2 + 4 * R**2 * V**4 - 5 * V**2 * c**2 * Z**2 +
                  3 * R**4 * V**4 * Z**2 + 13 * R**2 * V**2 * c**2 +
                  5 * R**6 * V**4 + R**2 * V**4 * Z**2 - 11 * R**4 * V**4)
    numerator2 = (V**2 * (7 * R**2 * V**4 * c**2 - V**4 * c**2 * Z**2 -
                          22 * R**4 * V**4 * c**2 + 8 * R**2 * V**4 * c**2 * Z**2 -
                          R**6 * V**6 * Z**2 + 13 * R**2 * V**2 * c**4 +
                          10 * R**6 * V**6 + R**2 * V**6 * Z**2 - 5 * R**8 * V**6 +
                          5 * R**6 * V**4 * c**2 - 4 * V**2 * c**4 -
                          3 * R**4 * V**6 + 3 * R**4 * V**4 * c**2 * Z**2 -
                          4 * R**4 * V**6 * Z**2 - 5 * V**2 * c**4 * Z**2))
    numerator3 = (2 * V * (2 * V * c**4 - R**6 * V**5 * Z**2 -
                           5 * R**8 * V**5 + 7 * R**2 * V**3 * c**2 * Z**2 -
                           4 * R**4 * V**5 * Z**2 - 11 * R**4 * V**3 * c**2 +
                           10 * R**6 * V**5 - V**3 * c**2 * Z**2 +
                           3 * R**2 * V**3 * c**2 + R**2 * V**5 * Z**2 -
                           3 * R**4 * V**5))
    denominator = (R**4 * V**2 + c**2 - R**2 * V**2)**3
    return -numerator1 / denominator - numerator2 / denominator - numerator3 / denominator

def cubic_drive(R, Z, c, V):
    numerator = (11 * Z**2 * R**5 * V**4 - 23 * Z**2 * R**2 * V**2 * c**2 - 16 * R * V**2 * c**2 
                 + 15 * R**10 * V**4 + Z**2 * R**8 * V**4 - 31 * R**7 * V**4 + 39 * R**4 * V**2 * c**2 
                 + 10 * R**4 * V**4)
    denominator = (R**6 * V**2 - R**3 * V**2 + c**2)**3
    return (3/4) * (numerator / denominator)

def cubic_stat(R, Z, c, V):
    term1 = cubic_drive(R, V, Z, c)
    
    term2_numerator = ((15 * R**11 * V**4 * c**2 - 15 * R**14 * V**6 + 17 * R**5 * V**4 * c**2 
                        - 23 * Z**2 * R**3 * V**2 * c**4 + 36 * Z**2 * R**6 * V**4 * c**2 
                        + 39 * R**5 * V**2 * c**4 - 10 * R**2 * V**2 * c**4 + Z**2 * R**3 * V**4 * c**2 
                        - 2 * Z**2 * V**2 * c**4 + Z**2 * R**6 * V**6 + 28 * R**11 * V**6 
                        + 3 * Z**2 * R**12 * V**6 + Z**2 * R**9 * V**4 * c**2 - 7 * R**8 * V**6 
                        - 64 * R**8 * V**4 * c**2 - 16 * Z**2 * R**9 * V**6) * V**2)
    term2_denominator = (R**6 * V**2 - R**3 * V**2 + c**2)**3 * R
    term2 = (3/4) * (term2_numerator / term2_denominator)
    
    term3_numerator = ((15 * R**14 * V**5 - 28 * R**11 * V**5 + 33 * R**8 * V**3 * c**2 - Z**2 * R**6 * V**5 
                        + 16 * Z**2 * R**9 * V**5 + 7 * R**8 * V**5 - 6 * R**2 * V * c**4 
                        - 3 * Z**2 * R**12 * V**5 + 2 * Z**2 * V * c**4 - Z**2 * R**3 * V**3 * c**2 
                        - 25 * Z**2 * R**6 * V**3 * c**2 - 7 * R**5 * V**3 * c**2) * V)
    term3_denominator = (R**6 * V**2 - R**3 * V**2 + c**2)**3 * R
    term3 = (3/2) * (term3_numerator / term3_denominator)
    
    return term1 - term2 + term3

def quartic_drive(R, Z, c, V):
    numerator = 4 * (
        5 * R**8 * V**4 * Z**2 + 3 * R**6 * V**4 + 13 * R**6 * V**2 * c**2 
        - 9 * R**4 * V**2 * c**2 * Z**2 + 5 * R**14 * V**4 - R**12 * V**4 * Z**2 
        - 5 * R**2 * V**2 * c**2 - 10 * R**10 * V**4
    )
    denominator = (c**2 - R**4 * V**2 + R**8 * V**2)**3
    return numerator / denominator

def quartic_stat(R, Z, c, V):
    numerator_1 = 4 * V**2 * (
        3 * R**2 * V**2 * c**4 - 2 * R**16 * V**6 * Z**2 - R**4 * V**4 * c**2 * Z**2
        + 21 * R**10 * V**4 * c**2 + 5 * R**18 * V**6 - 5 * R**14 * V**4 * c**2
        + R**12 * V**4 * c**2 * Z**2 - 14 * R**8 * V**4 * c**2 * Z**2
        - 9 * R**14 * V**6 - 5 * R**6 * V**4 * c**2 + 6 * R**12 * V**6 * Z**2
        - 13 * R**6 * V**2 * c**4 + 9 * R**4 * V**2 * c**4 * Z**2 + V**2 * c**4 * Z**2
        + 2 * R**10 * V**6
    )
    numerator_2 = 8 * V * (
        V * c**4 * Z**2 - 2 * R**6 * V**3 * c**2 - 9 * R**8 * V**3 * c**2 * Z**2
        - 2 * R**16 * V**5 * Z**2 - 9 * R**14 * V**5 + 6 * R**12 * V**5 * Z**2
        + 5 * R**18 * V**5 + 11 * R**10 * V**3 * c**2 + 2 * R**10 * V**5
        - 2 * R**2 * V * c**4 - R**4 * V**3 * c**2 * Z**2
    )
    numerator_3 = 4 * (
        5 * R**8 * V**4 * Z**2 + 3 * R**6 * V**4 + 13 * R**6 * V**2 * c**2
        - 9 * R**4 * V**2 * c**2 * Z**2 + 5 * R**14 * V**4 - R**12 * V**4 * Z**2
        - 5 * R**2 * V**2 * c**2 - 10 * R**10 * V**4
    )
    denominator = (c**2 - R**4 * V**2 + R**8 * V**2)**3
    return (numerator_1 + numerator_2 + numerator_3) / denominator

# M1: 2 - R/2

def linear_m1_drive(R, Z, c, V):
    numerator = (-128 * c**2 * R**2 * V**2 + 168 * Z**2 * R * V**4 + 5 * R**5 * V**4 - 128 * Z**2 * V**4
                 + 52 * c**2 * R**3 * V**2 - 62 * R**4 * V**4 + 224 * R**3 * V**4 - 64 * c**2 * Z**2 * V**2
                 + 11 * Z**2 * R**3 * V**4 - 256 * R**2 * V**4 + 12 * c**2 * Z**2 * R * V**2 - 74 * Z**2 * R**2 * V**4)
    denominator = (R**2 * V**2 + 8 * V**2 - 6 * R * V**2 + 4 * c**2)**3 * R**3
    return numerator / denominator

def linear_m1_stat(R, Z, c, V):
    numerator1 = (12 * c**2 * Z**2 * R**2 * V**3 + 224 * Z**2 * R * V**5 - 5 * R**6 * V**5 - 128 * c**2 * R**2 * V**3
                  + 32 * c**4 * R**2 * V + 66 * R**5 * V**5 - 128 * Z**2 * V**5 - 7 * Z**2 * R**4 * V**5
                  - 296 * R**4 * V**5 + 160 * c**2 * R**3 * V**3 - 44 * c**2 * R**4 * V**3 + 560 * R**3 * V**5
                  + 54 * Z**2 * R**3 * V**5 + 32 * c**4 * Z**2 * V - 384 * R**2 * V**5 - 160 * Z**2 * R**2 * V**5
                  - 32 * c**2 * Z**2 * R * V**3)
    term1 = numerator1 * V
    
    numerator2 = (304 * c**2 * Z**2 * R * V**4 - 5 * R**6 * V**6 + 104 * c**4 * R**3 * V**2 + 224 * Z**2 * R * V**6
                  - 224 * c**4 * R**2 * V**2 - 296 * R**4 * V**6 + 10 * c**2 * R**5 * V**4 + 24 * c**4 * Z**2 * R * V**2
                  - 256 * c**2 * Z**2 * V**4 - 7 * Z**2 * R**4 * V**6 + 66 * R**5 * V**6 - 168 * c**2 * R**4 * V**4
                  - 128 * Z**2 * V**6 + 608 * c**2 * R**3 * V**4 + 54 * Z**2 * R**3 * V**6 + 560 * R**3 * V**6
                  + 22 * c**2 * Z**2 * R**3 * V**4 - 96 * c**4 * Z**2 * V**2 - 160 * Z**2 * R**2 * V**6
                  - 640 * c**2 * R**2 * V**4 - 136 * c**2 * Z**2 * R**2 * V**4 - 384 * R**2 * V**6)
    term2 = (1/2) * numerator2 * V**2
    
    denominator = (R**2 * V**2 + 8 * V**2 - 6 * R * V**2 + 4 * c**2)**3 * R**3
    return -(term1 / denominator + term2 / denominator + linear_m1_drive(c, R, V, Z))

def logarithmic_drive(R, Z, c, V):
    numerator = (-13 * V**4 * np.log(R)**2 * Z**2 + 16 * V**4 * np.log(R)**3 * Z**2 - 2 * R**2 * V**4 
                 - 5 * V**2 * c**2 * Z**2 - 7 * R**2 * V**4 * np.log(R)**2 + 7 * R**2 * V**4 * np.log(R) 
                 + V**4 * np.log(R) * Z**2 + R**2 * V**2 * c**2 + 16 * V**2 * c**2 * np.log(R) * Z**2)
    denominator = R**4 * (V**2 * np.log(R)**2 - V**2 * np.log(R) + c**2)**3
    return -1/4 * (numerator / denominator)

def logarithmic_stat(R, Z, c, V):
    term1_numerator = (-7 * V**5 * np.log(R)**3 * Z**2 + V**3 * c**2 * Z**2 + 3 * R**2 * V**3 * c**2 * np.log(R) 
                       + 8 * V**3 * c**2 * np.log(R)**2 * Z**2 + V**3 * c**2 * np.log(R) * Z**2 - V**5 * np.log(R) * Z**2 
                       + 4 * R**2 * V**5 * np.log(R)**2 - 5 * R**2 * V**5 * np.log(R)**3 - R**2 * V**3 * c**2 
                       + 12 * V**5 * np.log(R)**4 * Z**2 - 4 * V * c**4 * Z**2 - R**2 * V**5 * np.log(R)) * V
    term2_numerator = ((12 * V**6 * np.log(R)**4 * Z**2 + V**2 * c**4 * Z**2 - R**2 * V**2 * c**4 - V**6 * np.log(R) * Z**2 
                         + R**2 * V**4 * c**2 - R**2 * V**6 * np.log(R) + 21 * V**4 * c**2 * np.log(R)**2 * Z**2 
                         - 4 * R**2 * V**4 * c**2 * np.log(R) - 16 * V**2 * c**4 * np.log(R) * Z**2 + V**4 * c**2 * Z**2 
                         + 7 * R**2 * V**4 * c**2 * np.log(R)**2 - 16 * V**4 * c**2 * np.log(R)**3 * Z**2 
                         - 5 * R**2 * V**6 * np.log(R)**3 + 4 * R**2 * V**6 * np.log(R)**2 - 7 * V**6 * np.log(R)**3 * Z**2) * V**2)
    term3_numerator = (-13 * V**4 * np.log(R)**2 * Z**2 + 16 * V**4 * np.log(R)**3 * Z**2 - 2 * R**2 * V**4 
                        - 5 * V**2 * c**2 * Z**2 - 7 * R**2 * V**4 * np.log(R)**2 + 7 * R**2 * V**4 * np.log(R) 
                        + V**4 * np.log(R) * Z**2 + R**2 * V**2 * c**2 + 16 * V**2 * c**2 * np.log(R) * Z**2)
    denominator = R**4 * (V**2 * np.log(R)**2 - V**2 * np.log(R) + c**2)**3
    
    return (-1/2 * (term1_numerator / denominator) + 1/4 * (term2_numerator / denominator) - 1/4 * (term3_numerator / denominator))

def root_drive(R, Z, c, V):
    numerator = (-1/16) * ( 
        23 * R**175 * V**6 * c**2 - 82 * R**(349/2) * V**6 * c**2 +
        91 * R**174 * V**6 * c**2 - 135 * Z**4 * R**171 * V**6 * c**2 +
        585 * Z**4 * R**170 * V**6 * c**2 - 130 * Z**4 * R**(341/2) * V**6 * c**2 -
        340 * Z**6 * R**167 * V**4 * c**4 + 60 * Z**6 * R**(335/2) * V**4 * c**4 +
        274 * Z**2 * R**(343/2) * V**4 * c**4 - 170 * Z**2 * R**171 * V**4 * c**4 +
        5 * R**176 * V**8 - 10 * Z**10 * R**164 * V**8 +
        316 * Z**10 * R**165 * V**8 + 61 * Z**12 * R**(323/2) * V**4 * c**4 +
        970 * Z**8 * R**(333/2) * V**6 * c**2 - 195 * Z**8 * R**166 * V**6 * c**2
    )
    denominator = ((R * V**2 - np.sqrt(R) * V**2 + c**2)**5 * (Z**2 - R**2)**5 * R**164)
    return numerator / denominator

def root_stat(R, Z, c, V):
    term1 = root_drive(R, V, c, Z)
    term2 = (1/8) * V * (
        325 * Z**8 * R**132 * V**7 * c**2 - 115 * Z**8 * R**131 * V**9 -
        7 * R**138 * V**3 * c**6 - 105 * Z**4 * R**134 * V**3 * c**6 +
        25 * Z**12 * R**(251/2) * V**3 * c**6 + 202 * Z**2 * R**138 * V**9 +
        6 * Z**2 * R**139 * V**9 + 180 * Z**6 * R**134 * V**9 -
        140 * Z**6 * R**135 * V**9 + 370 * Z**4 * R**(271/2) * V**9 +
        34 * R**(279/2) * V**9 - 130 * Z**10 * R**(255/2) * V**3 * c**6
    )
    return term1 + term2

#
#
#
#
#

# Parameters
a, b, c, V = 1.0, 1.0, 1.0, 1
lim = 3
x_min, x_max = -lim, lim
z_min, z_max = -lim, lim
x_values = np.linspace(x_min, x_max, 100)
z_values = np.linspace(z_min, z_max, 100)
X, Z = np.meshgrid(x_values, z_values)

C = 299792458

def cartesify(fn):
	def decorated(x, z, c=C, V=C):
		R = x**2 + z**2 + 0 # y=0
		Z = z
		return fn(R, Z, c, V)
	return decorated

# Compute function values

BLOCK_1_SELECTOR = root_drive
BLOCK_2_SELECTOR = root_stat

F1 = cartesify(BLOCK_1_SELECTOR)
F2 = cartesify(BLOCK_2_SELECTOR)

fig, axes = plt.subplots(2, 3, figsize=(18, 9), subplot_kw={'projection': None})
fig.suptitle("Warp drive Eulerian energy densities (quartic drive function, a=b=c=1, V=1)")

# --- Colormap (heatmap) ---
ax1 = axes[0, 0] # fig.add_subplot(2, 3, 1)
cmap_plot = ax1.contourf(X, Z, F1(X, Z), levels=50, cmap='plasma')
plt.colorbar(cmap_plot, ax=ax1)
ax1.set_title("xz slice (drive's rest frame)")
ax1.set_xlabel("x")
ax1.set_ylabel("z")

zero_contour1 = ax1.contour(X, Z, F1(X, Z), levels=[0], colors='cyan', linewidths=1)
ax1.clabel(zero_contour1, fmt='%.2f', colors='white', fontsize=10)

# --- 3D Surface Plot ---
ax2 = fig.add_subplot(2, 3, 2, projection='3d')
ax2.plot_surface(X, Z, F1(X, Z), cmap='plasma')
ax2.set_title("xz slice (drive's rest frame)")
ax2.set_xlabel("x")
ax2.set_ylabel("z")
ax2.set_zlabel("f(x, z)")

# --- 2D Line Plot ---
z_fixed = 0  # Fix z for line plot
F1_x = F1(x_values, z_fixed)
ax3 = axes[0, 2] # fig.add_subplot(2, 3, 3)
ax3.plot(x_values, F1_x, label=f"z={z_fixed}")
ax3.set_title("Slice of y-surface at z=0 (drive's rest frame)")
ax3.set_xlabel("x")
ax3.set_ylabel("f(x, z_fixed)")
ax3.legend()

ax3.axhline(y=0, color='r', linestyle='--', label='0')



ax4 = axes[1, 0] # fig.add_subplot(2, 3, 4)
cmap_plot2 = ax4.contourf(X, Z, F2(X, Z), levels=50, cmap='plasma')
plt.colorbar(cmap_plot2, ax=ax4)
ax4.set_title("xz slice (Earth's rest frame)")
ax4.set_xlabel("x")
ax4.set_ylabel("z")

zero_contour2 = ax4.contour(X, Z, F2(X, Z), levels=[0], colors='cyan', linewidths=1)
ax4.clabel(zero_contour2, fmt='%.2f', colors='white', fontsize=10)

ax5 = fig.add_subplot(2, 3, 5, projection='3d')
ax5.plot_surface(X, Z, F2(X, Z), cmap='plasma')
ax5.set_title("xz slice (Earth's rest frame)")
ax5.set_xlabel("x")
ax5.set_ylabel("z")
ax5.set_zlabel("f(x, z)")


F2_x = F2(x_values, z_fixed)  # Modify for second frame
ax6 = axes[1, 2] # fig.add_subplot(2, 3, 6)
ax6.plot(x_values, F2_x, label=f"z={z_fixed}", color='red')
ax6.set_title("Slice of y-surface at z=0 (Earth's rest frame)")
ax6.set_xlabel("x")
ax6.set_ylabel("f(x, z_fixed)")
ax6.legend()

ax6.axhline(y=0, color='b', linestyle='--', label='0')

plt.tight_layout()
plt.show()
