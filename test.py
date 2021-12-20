import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime


now = datetime.now()
name_clarifier = "visualization_heightmap"
timestamp = now.strftime("%Y%m%d_%H_%M_%S") + name_clarifier
print(timestamp)

# INCH_TO_M = 0.0254
# x = np.arange(0, 17., 0.1)
# labels = ["Bare Balloon", "Unlocked with Skins",
#           "Fully Locked Towards", "Half Locked Towards",
#           "Fully Locked Against", "Half Locked Against"]
# curvatures = [0.022233, 0.0192, 0.0319, 0.0291, 0.01132, 0.0124]
# colors = ["b", "b", "r", "r", "g", "g"]
# widths = [2, 4, 4, 2, 4, 2]
#
# for label, K, c, w in zip(labels, curvatures, colors, widths):
#     theta = np.linspace(0., np.arcsin(17*INCH_TO_M*K))
#     x = 1/K*(1 - np.cos(theta))
#     y = 1/K*np.sin(theta)
#     plt.plot(x, y, color=c, linewidth=w)
#
# plt.legend(labels)
# plt.xlabel("x (m)")
# plt.ylabel("y (m)")
# plt.title("Path Traced by Auxetic Skins at 2.5psi")
# plt.show()


size = 100
x = np.linspace(-10, 10, size)
y = np.linspace(-10, 10, size)
x, y = np.meshgrid(x, y)

sigma_xs = [3, 2, 2, 8]
sigma_ys = [3, 4, 4, 6]
mu_xs = [-8, 3, 5, 0]
mu_ys = [-8, -9, -8.5, 0]
zs = []

for sigma_x, sigma_y, mu_x, mu_y in zip(sigma_xs, sigma_ys, mu_xs, mu_ys):
    z = (1/(2*np.pi*sigma_x*sigma_y)*np.exp(-((x - mu_x)**2/(2*sigma_x**2) + (y - mu_y)**2/(2*sigma_y**2))))
    zs.append(z)

# sigma_x = 5.
# sigma_y = 2.
# mu_x, mu_y = 0, 5
# z = (1/(2*np.pi*sigma_x*sigma_y) * np.exp(-((x - mu_x)**2/(2*sigma_x**2)
#      + (y - mu_y)**2/(2*sigma_y**2))))
#
# sigma_x = 3.
# sigma_y = 5.
# mu_x, mu_y = -4, -1
# z2 = (1/(2*np.pi*sigma_x*sigma_y) * np.exp(-((x - mu_x)**2/(2*sigma_x**2)
#      + (y - mu_y)**2/(2*sigma_y**2))))

# plt.contourf(x, y, z + z2, cmap='Greys')
fig = plt.imshow(sum(zs))
plt.set_cmap('Greys')
plt.axis('off')
plt.savefig("figures/" + timestamp + ".png", bbox_inches='tight', pad_inches=0)
plt.show()
