import numpy as np
import sys
import matplotlib.pyplot as plt
import sympy

if len(sys.argv) == 1:
	print("Use \"contour\" or \"surface\".")

def f1(R, Z, c=1, a=1, b=1, V=1):
	# Linear dilation-shift
    numerator = (1/4) * (8*V**4*R**2*a**2*b + 5*V**4*R**5*b**4 - 2*V**4*R**3*b**2 
                - 13*V**4*R**3*a*b**2 + 16*Z**2*V**4*a**2*b - 8*V**4*R**2*a**3*b 
                - 39*Z**2*V**4*R*a*b**2 - 8*Z**2*V**4*a**3*b + 3*c**2*Z**2*V**2*R*b**2 
                + 23*Z**2*V**4*R**2*b**3 + 27*Z**2*V**4*R*a**2*b**2 - 30*Z**2*V**4*R**2*a*b**3 
                + 12*Z**2*V**4*R*b**2 + 8*c**2*Z**2*V**2*b + 21*V**4*R**3*a**2*b**2 
                + 5*V**4*R**4*b**3 + 11*Z**2*V**4*R**3*b**4 - 8*Z**2*V**4*a*b 
                - 18*V**4*R**4*a*b**3 - 8*c**2*V**2*R**2*a*b)
    
    denominator = ((V**2*R**2*b**2 + c**2 + V**2*R*b - V**2*a - 2*V**2*R*a*b + V**2*a**2)**3 * R**3)
    
    return numerator / denominator

def f2(R, Z, c=1, a=1, b=1, V=1):
	# Quadratic dilation-shift
    numerator1 = (10 * a**2 * b + 5 * b**4 * R**6 - 8 * a**3 * b + 3 * a**2 * b**2 * Z**2 
                 - 17 * a * b**2 * R**2 + 3 * b**4 * R**4 * Z**2 - 7 * a * b**2 * Z**2 
                 + 21 * a**2 * b**2 * R**2 + 4 * b**2 * Z**2 - 2 * a * b + 7 * b**3 * R**4 
                 - 18 * a * b**3 * R**4 + 7 * b**3 * R**2 * Z**2 - 6 * a * b**3 * R**2 * Z**2) * V**4
    
    denominator = (a * V**2 + 2 * a * b * R**2 * V**2 - b * R**2 * V**2 - b**2 * R**4 * V**2 - c**2 - a**2 * V**2) ** 3
    
    term2 = (2 * b * V**2 * c**2 - 8 * a * b * V**2 * c**2 + 13 * b**2 * R**2 * V**2 * c**2 - 5 * b**2 * V**2 * c**2 * Z**2) / denominator
    
    return - numerator1 / denominator - term2

def f3(R, Z, c=1, a=1, b=0, V=1):
	# Cubic dilation-shift
    numerator1 = (3/4) * V**4 * (8 * Z**2 * a * b**3 + 32 * R**2 * a * b**2 + R**9 * Z**2 * a**4 
                + 4 * R**3 * Z**2 * a**2 - 24 * R**2 * a * b**3 - 16 * Z**2 * a * b**2 
                + 6 * R**6 * Z**2 * a**3 * b + 5 * R**6 * Z**2 * a**3 + 8 * Z**2 * a * b 
                - 54 * R**8 * a**3 * b - 8 * R**2 * a * b - 15 * R**3 * Z**2 * a**2 * b**2 
                - 55 * R**5 * a**2 * b + 2 * R**5 * a**2 + 23 * R**8 * a**3 + 11 * R**3 * Z**2 * a**2 * b 
                + 15 * R**11 * a**4 + 63 * R**5 * a**2 * b**2)
    
    denominator = R * (c**2 + R**6 * V**2 * a**2 + R**3 * V**2 * a - V**2 * b + V**2 * b**2 - 2 * R**3 * V**2 * a * b) ** 3
    
    term2 = (3/4) * (8 * R**2 * V**2 * c**2 * a - 8 * V**2 * c**2 * Z**2 * a + 39 * R**5 * V**2 * c**2 * a**2 
                     + 8 * V**2 * c**2 * Z**2 * a * b - 24 * R**2 * V**2 * c**2 * a * b - 23 * R**3 * V**2 * c**2 * Z**2 * a**2) / denominator
    
    return numerator1 / denominator + term2

def f4(R, Z, c=1, a=1, b=1, V=1):
    # Quartic dilation-shift
    numerator1 = (9 * a**2 * R**4 * V**2 * c**2 * Z**2 + 4 * a * V**2 * c**2 * Z**2 
                 - 3 * a * R**2 * V**2 * c**2 + 8 * a * b * R**2 * V**2 * c**2 
                 - 4 * a * b * V**2 * c**2 * Z**2 - 13 * a**2 * R**6 * V**2 * c**2)
    
    denominator = (a * R**4 * V**2 + b**2 * V**2 - 2 * a * b * R**4 * V**2 
                   + a**2 * R**8 * V**2 + c**2 - b * V**2) ** 3
    
    term2 = (8 * a * b**3 * R**2 - 4 * a * b * Z**2 + 9 * a**2 * b**2 * R**4 * Z**2 
            - 21 * a**2 * b**2 * R**6 - a**2 * R**6 - 8 * a**3 * R**10 + 18 * a**3 * b * R**10 
            - 11 * a * b**2 * R**2 - 4 * a * b**3 * Z**2 + 3 * a * b * R**2 + 19 * a**2 * b * R**6 
            - 5 * a**4 * R**14 + 8 * a * b**2 * Z**2 + a**3 * R**8 * Z**2 + a**4 * R**12 * Z**2 
            - 6 * a**3 * b * R**8 * Z**2 - 9 * a**2 * b * R**4 * Z**2) * V**4
    
    return -4 * (numerator1 / denominator) - 4 * (term2 / denominator)

def f5(R, Z, c=1, a=1, b=1, V=1):
    # 10th-power dilation-shift
    numerator1 = (105 * a**2 * b**2 * R**18 + 8 * a**2 * R**18 + 58 * a * b**2 * R**8 + 32 * a * b * R**6 * Z**2 
                 - 17 * a**4 * R**36 * Z**2 + 93 * a**2 * b * R**16 * Z**2 + 25 * a**4 * R**38 + 32 * a * b**3 * R**6 * Z**2 
                 - 40 * a * b**3 * R**8 + 66 * a**3 * b * R**26 * Z**2 + 43 * a**3 * R**28 - 29 * a**3 * R**26 * Z**2 
                 - 90 * a**3 * b * R**28 - 18 * a * b * R**8 - 101 * a**2 * b * R**18 - 64 * a * b**2 * R**6 * Z**2 
                 - 81 * a**2 * b**2 * R**16 * Z**2 - 12 * a**2 * R**16 * Z**2) * V**4
    
    denominator = (2 * a * b * R**10 * V**2 - b**2 * V**2 - a**2 * R**20 * V**2 - a * R**10 * V**2 - c**2 + b * V**2) ** 3
    
    term2 = (18 * a * R**8 * V**2 * c**2 - 40 * a * b * R**8 * V**2 * c**2 + 32 * a * b * R**6 * V**2 * c**2 * Z**2 
            - 57 * a**2 * R**16 * V**2 * c**2 * Z**2 - 32 * a * R**6 * V**2 * c**2 * Z**2 + 65 * a**2 * R**18 * V**2 * c**2) / denominator
    
    return -5 * (numerator1 / denominator + term2)

def f6(R, Z, c=1, a=1, b=1, V=1):
    # 50th-power dilation-shift
    numerator1 = (-25 * (98 * a * R**48 * V**2 * c**2 - 325 * a**2 * R**98 * V**2 * c**2 + 317 * a**2 * R**96 * V**2 * c**2 * Z**2 
                 - 200 * a * b * R**48 * V**2 * c**2 - 192 * a * R**46 * V**2 * c**2 * Z**2 + 192 * a * b * R**46 * V**2 * c**2 * Z**2))
    
    denominator = ((2 * a * b * R**50 * V**2 + a**2 * R**100 * V**2 - b * V**2 - a * R**50 * V**2 + c**2 + b**2 * V**2) ** 3)
    
    term2 = (25 * V**4 * (98 * a * b * R**48 - 192 * a * b * R**46 * Z**2 + 48 * a**2 * R**98 - 521 * a**2 * b * R**98 
             - 223 * a**3 * R**148 - 192 * a * b**3 * R**46 * Z**2 - 426 * a**3 * b * R**146 * Z**2 - 501 * a**2 * b**2 * R**96 * Z**2 
             + 209 * a**3 * R**146 * Z**2 + 593 * a**2 * b * R**96 * Z**2 - 92 * a**2 * R**96 * Z**2 + 450 * a**3 * b * R**148 
             + 200 * a * b**3 * R**48 + 525 * a**2 * b**2 * R**98 - 298 * a * b**2 * R**48 - 117 * a**4 * R**196 * Z**2 
             + 384 * a * b**2 * R**46 * Z**2 + 125 * a**4 * R**198)) / denominator
    
    return numerator1 / denominator + term2

def f7(R, Z, c=299792458, a=.1, b=1, V=2):
    # Hyperbolic tangential dilation-shift
    tanh_term = np.tanh(-b + R)
    numerator1 = V**4 * (
        42 * R * tanh_term**5 * Z**2 * a**4 + 32 * tanh_term**2 * Z**2 * a**2 +
        45 * R * tanh_term**2 * Z**2 * a**4 - 45 * R**3 * tanh_term**2 * a**4 +
        24 * R**2 * tanh_term**4 * a**4 + 32 * R**2 * tanh_term**3 * a**3 -
        3 * R**3 * a**4 - 54 * R**3 * tanh_term * a**3 - 64 * R * tanh_term * Z**2 * a**2 +
        24 * tanh_term * Z**2 * a**4 - 8 * R**2 * tanh_term**5 * a**4 + 32 * R**3 * tanh_term * a**2 +
        78 * R * tanh_term * Z**2 * a**3 - 8 * R**2 * a**4 - 35 * R * tanh_term**4 * Z**2 * a**4 -
        14 * R * Z**2 * a**3 - 28 * R * tanh_term**3 * Z**2 * a**3 + 24 * R**2 * tanh_term * a**4 -
        90 * R**3 * tanh_term**4 * a**3 + 20 * R**3 * tanh_term**3 * a**4 - 8 * Z**2 * a**4 +
        64 * R * tanh_term**3 * Z**2 * a**2 - 16 * tanh_term**3 * Z**2 * a**4 + 16 * R * Z**2 * a**2 -
        32 * tanh_term**4 * Z**2 * a**3 + 24 * R**3 * tanh_term**4 * a**2 +
        42 * R**3 * tanh_term**5 * a**3 - 42 * R**3 * tanh_term**5 * a**4 - 32 * Z**2 * a**2 -
        32 * R**3 * tanh_term**3 * a**2 - 48 * R * tanh_term**4 * Z**2 * a**2 +
        24 * tanh_term**4 * Z**2 * a**4 + 64 * tanh_term**3 * Z**2 * a**3 +
        12 * R**3 * tanh_term**3 * a**3 + 32 * Z**2 * a**3 + 35 * R**3 * tanh_term**4 * a**4 -
        32 * R**2 * tanh_term * a**3 - 16 * R**2 * tanh_term**2 * a**4 -
        20 * R * tanh_term**3 * Z**2 * a**4 - 32 * tanh_term**3 * Z**2 * a**2 +
        3 * R * Z**2 * a**4 + 114 * R * tanh_term**4 * Z**2 * a**3 + 16 * R**2 * a**3 -
        13 * R * tanh_term**6 * Z**2 * a**4 - 8 * R**3 * a**2 - 22 * R * tanh_term * Z**2 * a**4 +
        32 * tanh_term * Z**2 * a**2 - 8 * tanh_term**5 * Z**2 * a**4 -
        16 * tanh_term**2 * Z**2 * a**4 + 32 * R * tanh_term**2 * Z**2 * a**2 -
        16 * R**3 * tanh_term**2 * a**2 + 22 * R**3 * tanh_term * a**4 +
        13 * R**3 * tanh_term**6 * a**4 - 64 * tanh_term * Z**2 * a**3 +
        6 * R**3 * a**3 - 16 * R**2 * tanh_term**3 * a**4 - 16 * R**2 * tanh_term**4 * a**3 +
        84 * R**3 * tanh_term**2 * a**3 - 50 * R * tanh_term**5 * Z**2 * a**3 -
        100 * R * tanh_term**2 * Z**2 * a**3)
    denominator = R**3 * (2 * tanh_term * V**2 * a + 4 * c**2 + V**2 * a**2 -
        2 * V**2 * a - 2 * tanh_term * V**2 * a**2 + tanh_term**2 * V**2 * a**2) ** 3
    return numerator1 / denominator

def f8(R, Z, a=1, b=1, c=1, V=1):
    # Linear dilation
    return (1/2) * (V**4 * (3 * R * b**2 - 4 * a * b)) / (R * (V**2 * a - R * V**2 * b + c**2)**3) \
           - 2 * (V**2 * c**2 * b) / (R * (V**2 * a - R * V**2 * b + c**2)**3)

def f9(R, Z, a=1, b=1, c=1, V=1):
    return 6 * (b * V**2 * c**2) / ((b * R**2 * V**2 - c**2 - a * V**2)**3) + \
            2 * ((3 * a * b - 2 * b**2 * R**2) * V**4) / ((b * R**2 * V**2 - c**2 - a * V**2)**3)

f = f9

C = 299792458
lim = 2.5


def f_cartesian(x, y, z, c=1, a=1, b=0.5, V=1):
    R = np.sqrt(x**2 + y**2 + z**2)
    Z = z
    return f(R, Z, c, a, b, V)

# Generate data for x and z
x_values = np.linspace(-lim, lim, 100)
z_values = np.linspace(-lim, lim, 100)
x, z = np.meshgrid(x_values, z_values)
y = np.zeros_like(x)  # Slice through y=0

F_values = f_cartesian(x, 0, z)

# # Plot the function
# plt.figure(figsize=(8, 6))
# plt.contourf(x, z, F_values, levels=50, cmap='cividis')
# plt.colorbar(label='f(x, z)')

# zero_contour = plt.contour(x, z, F_values, levels=[0], colors='cyan', linewidths=1)
# plt.clabel(zero_contour, fmt='%.2f', colors='white', fontsize=10)

# plt.xlabel('x')
# plt.ylabel('z')
# plt.title('Contour Plot of f(x, z) in Cartesian Coordinates')
# plt.show()

R = np.linspace(0.1, 5, 100)
Z = np.linspace(-3, 3, 100)
R, Z = np.meshgrid(R, Z)
F = f(R, Z)

fig = plt.figure(figsize=(12, 5))

# Contour Plot
ax1 = fig.add_subplot(1, 2, 1)
contour = ax1.contourf(x_values, z_values, F_values, levels=50, cmap='plasma')
plt.colorbar(contour, ax=ax1)
ax1.set_xlabel("x")
ax1.set_ylabel("z")
ax1.set_title("Energy density contour plot")

zero_contour = plt.contour(x, z, F_values, levels=[0], colors='cyan', linewidths=1)
plt.clabel(zero_contour, fmt='%.2f', colors='white', fontsize=10)

# 3D Surface Plot
ax2 = fig.add_subplot(1, 2, 2, projection='3d')
surf = ax2.plot_surface(x, z, F_values, cmap='plasma', edgecolor='none')
fig.colorbar(surf, ax=ax2, shrink=0.5, aspect=5)
ax2.set_xlabel("x")
ax2.set_ylabel("z")
ax2.set_zlabel("T⁰⁰")
ax2.set_title("")
ax2.view_init(elev=20, azim=50) # Adjust elevation and azimuth

plt.tight_layout()
plt.show()