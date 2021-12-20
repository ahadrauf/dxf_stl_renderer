from pattern import *
from settings import *
import numpy as np
from datetime import datetime


def generate_hexagon_pattern(nx, ny, s, buffer_height, kerf, gap, handle_x, handle_y):
    p = Pattern(setting=LaserCutter)
    # Derived constants
    cell_width = 1.5*s
    cell_height = np.sqrt(3)*s

    # Define hexagons
    def add_side(center):
        s_short = s - gap/2
        s_short_kerf = s_short - kerf/2
        cx, cy = center
        p.add_circle((cx + s_short_kerf, cy), kerf/2, start_angle=np.pi/2, end_angle=-np.pi/2)
        p.add_lines([(cx + s_short_kerf, cy + kerf/2),
                     (cx + kerf/2, cy + kerf/2),
                     (cx - s_short_kerf/2 + kerf/2*np.sqrt(3)/2, cy + s_short_kerf*np.sqrt(3)/2 + kerf/2/2)])
        p.add_circle((cx - s_short_kerf/2, cy + s_short_kerf*np.sqrt(3)/2),
                     kerf/2, start_angle=np.pi/6, end_angle=7*np.pi/6)
        p.add_lines([(cx - s_short_kerf/2 - kerf/2*np.sqrt(3)/2, cy + s_short_kerf*np.sqrt(3)/2 - kerf/2/2),
                     (cx - kerf/2, cy),
                     (cx - s_short_kerf/2 - kerf/2*np.sqrt(3)/2, cy - s_short_kerf*np.sqrt(3)/2 + kerf/2/2)])
        p.add_circle((cx - s_short_kerf/2, cy - s_short_kerf*np.sqrt(3)/2),
                     kerf/2, start_angle=5*np.pi/6, end_angle=11*np.pi/6)
        p.add_lines([(cx - s_short_kerf/2 + kerf/2*np.sqrt(3)/2, cy - s_short_kerf*np.sqrt(3)/2 - kerf/2/2),
                     (cx + kerf/2, cy - kerf/2),
                     (cx + s_short_kerf, cy - kerf/2)])

    for i in range(nx):
        for j in range(ny//2):
            if i%2 == 1:
                center = (cell_width/2 + s/2*i, cell_height/2*(2*j + 1/2))
            else:
                center = (cell_width/2 + s/2*i, cell_height/2*(2*j + 3/2))
            add_side(center)

    bottom_left = (-handle_x, -handle_y)
    top_right = (cell_width/2 + s/2*nx + handle_x, cell_height/2*(ny + 1/2) + handle_y)
    p.add_lines([(bottom_left[0], bottom_left[1]), (bottom_left[0], top_right[1]),
                 (top_right[0], top_right[1]), (top_right[0], bottom_left[1]),
                 (bottom_left[0], bottom_left[1])])
    print(bottom_left, top_right)

    return p


if __name__ == '__main__':
    nx = 30
    ny = 18
    s = 10.
    buffer_height = 20.  # mm, extra length on end to use as a handle
    kerf = 1  # cut size
    gap = 10  # gap between hexagons (always > kerf)
    handle_width = 10
    handle_height = 10

    now = datetime.now()
    name_clarifier = "_hexagon_star_pattern_nx={:d}xny={:d}_s={:.2f}_kerf={:.2f}_gap={:.2f}_noseamholes".format(
        nx, ny, s, kerf, gap
    )
    timestamp = now.strftime("%Y%m%d_%H_%M_%S") + name_clarifier
    print(timestamp)
    p = generate_hexagon_pattern(nx, ny, s, buffer_height, kerf, gap, handle_width, handle_height)

    # p.generate_svg('../patterns/' + timestamp + '.svg', save=True, offset_x=handle_width, offset_y=handle_height,
    #                default_linewidth=1.)
    p.generate_dxf('../patterns/' + timestamp + '.dxf', save=True, offset_x=handle_width, offset_y=handle_height)
