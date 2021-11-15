import numpy as np
import matplotlib.pyplot as plt

INCH_TO_M = 0.0254
x = np.arange(0, 17., 0.1)
labels = ["Bare Balloon", "Unlocked with Skins",
          "Fully Locked Towards", "Half Locked Towards",
          "Fully Locked Against", "Half Locked Against"]
curvatures = [0.022233, 0.0192, 0.0319, 0.0291, 0.01132, 0.0124]
colors = ["b", "b", "r", "r", "g", "g"]
widths = [2, 4, 4, 2, 4, 2]

for label, K, c, w in zip(labels, curvatures, colors, widths):
    theta = np.linspace(0., np.arcsin(17*INCH_TO_M*K))
    x = 1/K*(1 - np.cos(theta))
    y = 1/K*np.sin(theta)
    plt.plot(x, y, color=c, linewidth=w)

plt.legend(labels)
plt.xlabel("x (m)")
plt.ylabel("y (m)")
plt.title("Path Traced by Auxetic Skins at 2.5psi")
plt.show()
