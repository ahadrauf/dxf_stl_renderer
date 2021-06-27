from pattern import *
from settings import *
import numpy as np
from datetime import datetime


def generate_hexagon_pattern(nx, ny, s, buffer_height, seamhole_diameter, spring_radius, spring_gap, gap):
    p = Pattern(setting=LaserCutter)
    # Derived constants
    cell_width = 1.5*s
    cell_height = np.sqrt(3)*s
    s_short = 0.5*(s-gap/2)
    s_long = np.sqrt(3)/2*(s-gap/2)
    cutout_width = 2*spring_radius + 3*spring_gap
    cutout_depth = 2*spring_radius
    cutout_width_x = cutout_width*0.5
    cutout_width_y = cutout_width*np.sqrt(3)/2
    cutout_depth_x = cutout_depth*0.5
    cutout_depth_y = cutout_depth*np.sqrt(3)/2

    # Define hexagons
    for i in range(nx):
        for j in range(ny):
            if i % 2 == 0:
                center = (cell_width*i, cell_height*j)
            else:
                center = (cell_width*i, cell_height*j + s_long + gap/2)
            p1 = (center[0] - s_short, center[1] + s_long)  # left top
            p2 = (center[0] - (s - gap/2), center[1])  # left
            p.add_line(p1, p2)
            p1 = p2
            p2 = (center[0] - s_short, center[1] - s_long)  # left bottom
            p.add_line(p1, p2)
            p1 = p2
            p2 = (center[0] + s_short, p1[1])  # right bottom
            p.add_line(p1, p2)
            p1 = p2
            p2 = (center[0] + (s - gap/2), center[1])  # right
            p.add_line(p1, p2)
            p1 = p2
            p2 = (center[0] + s_short, center[1] + s_long)  # right top
            p.add_line(p1, p2)
            p1 = p2
            p2 = (center[0] - s_short, center[1] + s_long)  # left top
            p.add_line(p1, p2)

    return p


if __name__ == '__main__':
    nx = 14
    ny = 20
    s = 10.
    buffer_height = 20.  # mm, extra length on end to use as a handle
    seamhole_diameter = 3.  # mm
    kerf = 3.  # mm
    gap = 1.5  # mm, for defining the straight line segments

    now = datetime.now()
    name_clarifier = "_hexagon_pattern_nx={:d}xny={:d}_s={:.2f}_kerf={:.2f}_gap={:.2f}_noseamholes".format(
        nx, ny, s, kerf, gap
    )
    timestamp = now.strftime("%Y%m%d_%H_%M_%S") + name_clarifier
    print(timestamp)
    p = generate_hexagon_pattern(nx, ny, s, buffer_height, seamhole_diameter, kerf, gap)

    p.generate_svg('../patterns/' + timestamp + '.svg', save=True, offset_x=s, offset_y=np.sqrt(3)/2*s)
    # p.generate_dxf('../patterns/' + timestamp + '.dxf', save=True, offset_x=1.5*s, offset_y=np.sqrt(3)/2*s)
