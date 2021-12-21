import numpy as np
import matplotlib.pyplot as plt
from pcb_layout_plus_dxf import *

if __name__ == '__main__':
    p = PCBPattern()
    pts = [(0, 0), (2, 0), (0, 2), (2, 2), (2, 4), (4, 4), (4, 3), (2, 0)]
    p.add_trace_rounded(pts, 3, 0.5, 4)
    rounded_pts = p.traces[0][0]
    print(p.traces)
    print(rounded_pts)
    plt.plot([pt[0] for pt in rounded_pts], [pt[1] for pt in rounded_pts])
    plt.scatter([pt[0] for pt in pts], [pt[1] for pt in pts])
    plt.show()
