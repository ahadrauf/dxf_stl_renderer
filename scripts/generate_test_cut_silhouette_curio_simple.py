import sys
sys.path.append(r"C:\Users\ahadrauf\Desktop\Research\dxf_stl_renderer")

from pattern import *
from settings import *
import numpy as np
from datetime import datetime


def generate_test_cut_curio():
    p = Pattern(setting=LaserCutter)
    pattern_buffer_x = 20  # mm
    pattern_buffer_y = 20  # mm

    #############################################################################
    # Test artificial kerf performance (kerf width != 0)
    #############################################################################
    x, y = 0, 0
    line_lengths = np.arange(20., 52., 10.)
    gap_range = np.arange(5.0, 10.1, 5.0)  # = kerf width
    y_offset = line_lengths[-1]/2 + gap_range[-1]/2

    for i in range(len(gap_range)):
        gap = gap_range[i]
        for j in range(len(line_lengths)):
            p.add_line((x + gap*2*j, y + y_offset - line_lengths[j]/2),
                       (x + gap*2*j, y + y_offset + line_lengths[j]/2))
            center = (x + gap*(2*j + 0.5), y + y_offset + line_lengths[j]/2)
            p.add_circle(center, gap/2, start_angle=np.pi, end_angle=0)
            p.add_line((x + gap*(2*j + 1), y + y_offset - line_lengths[j]/2),
                       (x + gap*(2*j + 1), y + y_offset + line_lengths[j]/2))
            center = (x + gap*(2*j + 0.5), y + y_offset - line_lengths[j]/2)
            p.add_circle(center, gap/2, start_angle=0, end_angle=-np.pi)
        x += 2*gap*len(line_lengths) + pattern_buffer_x

    return p


if __name__ == '__main__':
    now = datetime.now()
    name_clarifier = "_test_cut_silhouette_curio_simple"
    timestamp = now.strftime("%Y%m%d_%H_%M_%S") + name_clarifier
    print(timestamp)
    p = generate_test_cut_curio()

    # p.generate_svg('../patterns/' + timestamp + '.svg', save=True, default_linewidth=1)
    p.generate_dxf('../patterns/' + timestamp + '.dxf', save=True)
