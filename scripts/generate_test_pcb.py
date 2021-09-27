import sys

sys.path.append(r"C:\Users\ahadrauf\Desktop\Research\dxf_stl_renderer")

from pattern import *
from settings import *
import numpy as np
from datetime import datetime

MIL_TO_MM = 0.0254


def generate_test_pcb():
    p = Pattern()

    N_range = np.arange(1, 6)
    w_range = np.array([3., 6., 9., 12.])*MIL_TO_MM
    l = 5.
    gap = 1.

    w_bondpad = 8.
    h_bondpad = 8.
    w_buffer = 5.
    h_buffer = 5.

    for idx in range(len(N_range)):
        N = N_range[idx]
        for idy in range(len(w_range)):
            w = w_range[idy]
            x = (w_bondpad + w_buffer)*idx
            y = (h_bondpad*2 + l + h_buffer)*idy
            p.add_rectangle((x, y), (x + w_bondpad, y + h_bondpad))
            p.add_rectangle((x, y + h_bondpad + l), (x + w_bondpad, y + l + 2*h_bondpad))
            for n in range(N):
                p.add_rectangle((x + (gap + w)*n, y + h_bondpad), (x + (gap + w)*n + w, y + h_bondpad + l))

    return p


if __name__ == '__main__':
    now = datetime.now()
    name_clarifier = "_test_pcb"
    timestamp = now.strftime("%Y%m%d_%H_%M_%S") + name_clarifier
    print(timestamp)
    p = generate_test_pcb()

    # p.generate_svg('../patterns/' + timestamp + '.svg', save=True, default_linewidth=1)
    p.generate_dxf('../patterns/' + timestamp + '.dxf', save=True)
