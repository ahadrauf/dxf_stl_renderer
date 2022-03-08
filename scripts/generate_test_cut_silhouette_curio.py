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
    # Test straight line performance (kerf width = 0)
    #############################################################################
    x, y = 0, 0
    line_lengths = np.arange(1., 52., 2.)
    gap_range = np.arange(3.5, 10.1, 0.5)
    y_offset = line_lengths[-1]/2

    for i in range(len(gap_range)):
        gap = gap_range[i]
        for j in range(len(line_lengths)):
            p.add_line((x + gap*j, y + y_offset - line_lengths[j]/2), (x + gap*j, y + y_offset + line_lengths[j]/2))
        x += gap*len(line_lengths) + pattern_buffer_x
        if i == len(gap_range)//2:
            x = 0
            y += 2*y_offset + pattern_buffer_y

    #############################################################################
    # Test artificial kerf performance (kerf width != 0)
    #############################################################################
    x, y = 0, y + line_lengths[-1] + pattern_buffer_y
    line_lengths = np.arange(1., 52., 2.)
    gap_range = np.arange(5.0, 10.1, 0.5)  # = kerf width
    y_offset = line_lengths[-1]/2 + gap_range[-1]/2

    for i in range(len(gap_range)):
        gap = gap_range[i]
        for j in range(len(line_lengths)):
            p.add_line((x + gap*2*j, y + y_offset - line_lengths[j]/2),
                       (x + gap*2*j, y + y_offset + line_lengths[j]/2))
            center = (x + gap*(2*j + 0.5), y + y_offset + line_lengths[j]/2)
            p.add_arc(center, gap/2, start_angle=np.pi, end_angle=0)
            p.add_line((x + gap*(2*j + 1), y + y_offset - line_lengths[j]/2),
                       (x + gap*(2*j + 1), y + y_offset + line_lengths[j]/2))
            center = (x + gap*(2*j + 0.5), y + y_offset - line_lengths[j]/2)
            p.add_arc(center, gap/2, start_angle=0, end_angle=-np.pi)
        x += 2*gap*len(line_lengths) + pattern_buffer_x
        if i == len(gap_range)//3 or i == 2*len(gap_range)//3:
            x = 0.
            y += line_lengths[-1] + gap + pattern_buffer_y

    #############################################################################
    # Test tug effect via expanding square
    #############################################################################
    x = 0
    y += line_lengths[-1] + gap_range[-1] + pattern_buffer_y
    num_segments = 10
    gap_range = np.arange(4.5, 10.1, 0.5)  # = kerf width
    y_offset = num_segments/2*gap_range[-1]

    cur_x, cur_y = x, y + y_offset
    for i in range(len(gap_range)):
        gap = gap_range[i]
        line_lengths = np.arange(gap, num_segments*gap, gap)
        for j in range(len(line_lengths)):
            line_length = line_lengths[j]
            if j % 2 == 0:
                p.add_lines([(cur_x, cur_y), (cur_x, cur_y + line_length), (cur_x - line_length, cur_y + line_length)])
                cur_x = cur_x - line_length
                cur_y = cur_y + line_length
            else:
                p.add_lines([(cur_x, cur_y), (cur_x, cur_y - line_length), (cur_x + line_length, cur_y - line_length)])
                cur_x = cur_x + line_length
                cur_y = cur_y - line_length
        if i < len(gap_range) - 1:
            cur_x, cur_y = x + num_segments*((i+1)*(gap_range[0] + gap_range[i+1])/2), y + y_offset

    return p


if __name__ == '__main__':
    now = datetime.now()
    name_clarifier = "_test_cut_silhouette_curio_v2"
    timestamp = now.strftime("%Y%m%d_%H_%M_%S") + name_clarifier
    print(timestamp)
    p = generate_test_cut_curio()

    # p.generate_svg('../patterns/' + timestamp + '.svg', save=True, default_linewidth=1)
    p.generate_dxf('../patterns/' + timestamp + '.dxf', save=True)
