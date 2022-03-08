import sys

sys.path.append(r"C:\Users\ahadrauf\Desktop\Research\dxf_stl_renderer")

from pattern import *
from pcb_layout import *
from settings import *
import numpy as np
from datetime import datetime


def generate_test_pcb():
    p = Pattern()

    kerf = 3
    N = 5
    w = 9*MIL_TO_MM
    gap = 6*MIL_TO_MM
    N_corner = 10
    l = kerf + 2*BOARD_EDGE_SPACING_EFF

    w_bondpad = 8.
    h_bondpad = 8.
    panel_spacing = 0.  # 0.3
    boundary_gap = 2.5
    m2_drill_diameter = 2.45
    m2_offset = 1.65*max(m2_drill_diameter/2, kerf/2)
    cut_radius = (l - 2*BOARD_EDGE_SPACING_EFF)/2
    y_buffer = l/2 - cut_radius
    inset = N*w + (N - 1)*gap + BOARD_EDGE_SPACING_EFF + cut_radius

    x, y = 0, 0
    p.add_lines([(x - BOARD_EDGE_SPACING_EFF, y - BOARD_EDGE_SPACING_EFF),
                 (x - BOARD_EDGE_SPACING_EFF, y + l + 2*h_bondpad + BOARD_EDGE_SPACING_EFF)])
    # Bottom cut boundary
    p.add_lines([(x - BOARD_EDGE_SPACING_EFF + panel_spacing,
                  y + l + 2*h_bondpad + BOARD_EDGE_SPACING_EFF),
                 (x + w_bondpad - panel_spacing - 2*m2_offset,
                  y + l + 2*h_bondpad + BOARD_EDGE_SPACING_EFF)])
    p.add_arc((x + w_bondpad - 2*m2_offset,
               y + l + 2*h_bondpad + BOARD_EDGE_SPACING_EFF + m2_offset), m2_offset, start_angle=-np.pi/2,
              end_angle=0)
    p.add_lines(
        [(x + w_bondpad - m2_offset, y + l + 2*h_bondpad + BOARD_EDGE_SPACING_EFF + m2_offset),
         (x + w_bondpad - m2_offset, y + l + 2*h_bondpad + 2*m2_offset)])
    p.add_lines([(x + w_bondpad - m2_offset + panel_spacing, y + l + 2*h_bondpad + 2*m2_offset),
                 (x + w_bondpad + boundary_gap, y + l + 2*h_bondpad + 2*m2_offset)])
    p.add_lines(
        [(x + w_bondpad + boundary_gap, y + l + 2*h_bondpad + 2*m2_offset - panel_spacing),
         (x + w_bondpad + boundary_gap, y + l - y_buffer + h_bondpad + panel_spacing)])
    p.add_lines([(x + w_bondpad + boundary_gap, y + l - y_buffer + h_bondpad),
                 (x + inset, y + l - y_buffer + h_bondpad)])

    # Top cut boundary
    p.add_lines([(x - BOARD_EDGE_SPACING_EFF + panel_spacing,
                  y - BOARD_EDGE_SPACING_EFF),
                 (x + w_bondpad - panel_spacing - 2*m2_offset,
                  y - BOARD_EDGE_SPACING_EFF)])
    p.add_arc((x + w_bondpad - 2*m2_offset,
               y - BOARD_EDGE_SPACING_EFF - m2_offset), m2_offset, start_angle=np.pi/2, end_angle=0)
    p.add_lines([(x + w_bondpad - m2_offset, y - BOARD_EDGE_SPACING_EFF - m2_offset),
                 (x + w_bondpad - m2_offset, y - 2*m2_offset)])
    p.add_lines([(x + w_bondpad - m2_offset + panel_spacing, y - 2*m2_offset),
                 (x + w_bondpad + boundary_gap, y - 2*m2_offset)])
    p.add_lines([(x + w_bondpad + boundary_gap, y - 2*m2_offset + panel_spacing),
                 (x + w_bondpad + boundary_gap, y + y_buffer + h_bondpad - panel_spacing)])
    p.add_lines([(x + w_bondpad + boundary_gap, y + y_buffer + h_bondpad),
                 (x + inset, y + y_buffer + h_bondpad)])
    p.add_arc((x + inset, y + 2.5*l/5 + h_bondpad), cut_radius, start_angle=np.pi/2, end_angle=3*np.pi/2)

    p.add_arc((x + w_bondpad, y - m2_offset), 2.2/2)
    p.add_arc((x + w_bondpad, y + 2*h_bondpad + l + m2_offset), 2.2/2)

    return p


if __name__ == '__main__':
    now = datetime.now()
    name_clarifier = "_test_pcb"
    timestamp = now.strftime("%Y%m%d_%H_%M_%S") + name_clarifier
    print(timestamp)
    p = generate_test_pcb()

    # p.generate_svg('../patterns/' + timestamp + '.svg', save=True, default_linewidth=1)
    p.generate_dxf('../patterns/' + timestamp + '.dxf', save=True)
