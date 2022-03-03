import sys

sys.path.append(r"C:\Users\ahadrauf\Desktop\Research\dxf_stl_renderer")

from pattern import *
from settings import *
import numpy as np
from datetime import datetime

MIL_TO_MM = 0.0254
INCH_TO_MM = 25.4

# def generate_test_pcb():
#     p = Pattern()
#
#     N_range = np.arange(1, 6)
#     w_range = np.array([3., 6., 9., 12.])*MIL_TO_MM
#     l = 5.
#     gap = 1.
#
#     w_bondpad = 8.
#     h_bondpad = 8.
#     w_buffer = 5.
#     h_buffer = 5.
#
#     for idx in range(len(N_range)):
#         N = N_range[idx]
#         for idy in range(len(w_range)):
#             w = w_range[idy]
#             x = (w_bondpad + w_buffer)*idx
#             y = (h_bondpad*2 + l + h_buffer)*idy
#             p.add_rectangle((x, y), (x + w_bondpad, y + h_bondpad))
#             p.add_rectangle((x, y + h_bondpad + l), (x + w_bondpad, y + l + 2*h_bondpad))
#             for n in range(N):
#                 p.add_rectangle((x + (gap + w)*n, y + h_bondpad), (x + (gap + w)*n + w, y + h_bondpad + l))
#
#     return p


if __name__ == '__main__':
    now = datetime.now()
    name_clarifier = "_mylar_5x5_grid"
    timestamp = now.strftime("%Y%m%d_%H_%M_%S") + name_clarifier
    print(timestamp)

    nx = 5
    ny = 5
    pvdf_buffer = 1.5/2
    cell_width = 15
    cell_height = 15

    p = Pattern()
    total_width = nx*cell_width
    total_height = ny*cell_height

    for i in range(nx + 1):
        p.add_line((cell_width*i, 0), (cell_width*i, total_height))
    for j in range(ny + 1):
        p.add_line((0, cell_height*j), (total_width, cell_height*j))

    # for i in range(nx):
    #     for j in range(ny):
    #         p.add_rectangle((cell_width*i + pvdf_buffer, cell_height*j + pvdf_buffer),
    #                         (cell_width*(i+1) - pvdf_buffer, cell_height*(j+1) - pvdf_buffer))

    # p.generate_svg('../patterns/' + timestamp + '.svg', save=True, default_linewidth=1)
    p.generate_dxf('../patterns/' + timestamp + '_cut.dxf', save=True)

    # name_clarifier = "_pvdf_1cm_square_etch"
    # timestamp = now.strftime("%Y%m%d_%H_%M_%S") + name_clarifier
    # print(timestamp)

    p = Pattern()
    p.add_line((cell_width*0, 0), (cell_width*0, total_height))
    p.add_line((cell_width*nx, 0), (cell_width*nx, total_height))
    p.add_line((cell_width*0, cell_height*0), (total_width, cell_height*0))
    p.add_line((cell_width*0, cell_height*ny), (total_width, cell_height*ny))
    for i in range(nx):
        for j in range(ny):
            p.add_rectangle((cell_width*i + pvdf_buffer, cell_height*j + pvdf_buffer),
                            (cell_width*(i + 1) - pvdf_buffer, cell_height*(j + 1) - pvdf_buffer))

    # p.generate_svg('../patterns/' + timestamp + '.svg', save=True, default_linewidth=1)
    p.generate_dxf('../patterns/' + timestamp + '_etch.dxf', save=True)
