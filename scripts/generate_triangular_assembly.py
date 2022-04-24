from pattern import *
from settings import *
import numpy as np
from datetime import datetime


def generate_triangular_pattern(width, height, nx, angle, handle_width, handle_height, gap):
    p = Pattern(setting=LaserCutter)
    # Derived constants
    cell_width = width/nx
    # angle = np.arctan2(cell_height, cell_width/2)
    # angle = np.pi/6
    ny = int(height/(cell_width/2*np.tan(angle)))
    cell_height = height/ny
    gap_x = gap*np.cos(angle)
    gap_y = gap*np.sin(angle)

    # gap = 2*kerf + gap

    tab_width = 0.2*width
    tab_edge = tab_width / np.sin(np.pi/6)
    triangle_height = width*np.sin(np.pi/3)
    buffer_height = handle_height + triangle_height

    # Define horizontal cuts
    for elem_x in range(4):
        max_x = nx if elem_x != 3 else 1
        for j in range(0, ny):
            if j%2 == 1:
                for i in range(nx):
                    p0 = (width*elem_x + cell_width*i + gap_x + handle_width, cell_height*j + gap_y + buffer_height)
                    p1 = (width*elem_x + cell_width*(i + 1/2) + handle_width, cell_height*(j + 1) + buffer_height)
                    p2 = (width*elem_x + cell_width*(i + 1) - gap_x + handle_width, cell_height*j + gap_y + buffer_height)
                    p.add_lines([p0, p1, p2])
            else:
                for i in range(-1, nx):
                    p0 = (width*elem_x + cell_width*(i + 1/2) + gap_x + handle_width, cell_height*j + gap_y + buffer_height)
                    p1 = (width*elem_x + cell_width*(i + 1) + handle_width, cell_height*(j + 1) + buffer_height)
                    p2 = (width*elem_x + cell_width*(i + 3/2) - gap_x + handle_width, cell_height*j + gap_y + buffer_height)
                    if i == -1:
                        pts = [p1, p2]
                    elif i == nx - 1:
                        pts = [p0, p1]
                    else:
                        pts = [p0, p1, p2]
                    p.add_lines(pts)

    # Define border
    bottom_left = (0, triangle_height)
    top_right = (3*width + 2*handle_width + cell_width, height + buffer_height + handle_height)
    p.add_lines([(width, bottom_left[1]), bottom_left, (bottom_left[0], top_right[1]),
                 (width, top_right[1])])
    p.add_lines([(2*width, bottom_left[1]), (top_right[0], bottom_left[1]), top_right,
                 (2*width, top_right[1])])

    # Define guiding cuts between the edge widths (along the handle)
    for elem_x in range(1, 4):
        # Bottom cut
        p0 = (width*elem_x, triangle_height - tab_edge)
        p1 = (p0[0], p0[1] + tab_edge)
        p.add_line(p0, p1)
        # Top cut
        p0 = (width*elem_x, height + buffer_height + handle_height)
        p1 = (p0[0], p0[1] + tab_edge)
        p.add_line(p0, p1)

    # Define insert triangle
    p0 = (width, triangle_height - tab_edge)
    p1 = (width*1.5 - tab_edge*np.cos(np.pi/6), tab_edge*np.sin(np.pi/6))
    p2 = (width*1.5, 0)
    p3 = (width*1.5 + tab_edge*np.cos(np.pi/6), p1[1])
    p4 = (2*width, p0[1])
    p.add_lines([p0, p1, p2, p3, p4])
    p0 = (width, height + buffer_height + handle_height + tab_edge)
    p1 = (width*1.5 - tab_edge*np.cos(np.pi/6), p0[1] + triangle_height - tab_edge - tab_edge*np.sin(np.pi/6))
    p2 = (width*1.5, p0[1] + triangle_height - tab_edge)
    p3 = (width*1.5 + tab_edge*np.cos(np.pi/6), p1[1])
    p4 = (2*width, p0[1])
    p.add_lines([p0, p1, p2, p3, p4])

    ################### Add circular holes for the tubes ##################
    p.add_circle((width*1.5 - 3.5, height + buffer_height + handle_height + triangle_height*1/3), radius=3.0)
    p.add_circle((width*1.5 + 3.5, height + buffer_height + handle_height + triangle_height*1/3), radius=3.0)

    ################### Add etched lines ##################
    # Add lines between side walls
    p0 = (width, triangle_height)
    p1 = (p0[0], buffer_height + height + handle_height)
    p.add_line(p0, p1, mode=LaserCutter.ENGRAVE)
    p0 = (2*width, triangle_height)
    p1 = (p0[0], buffer_height + height + handle_height)
    p.add_line(p0, p1, mode=LaserCutter.ENGRAVE)

    # Add lines for insert triangle
    p0 = (width, triangle_height)
    p1 = (width*1.5, 0)
    p2 = (width*2, triangle_height)
    p.add_lines([p0, p1, p2], mode=LaserCutter.ENGRAVE)
    p0 = (width, height + buffer_height + handle_height)
    p1 = (width*1.5, p0[1] + triangle_height)
    p2 = (width*2, p0[1])
    p.add_lines([p0, p1, p2], mode=LaserCutter.ENGRAVE)

    # Add guides for adding tape
    p0 = (0, 0)
    p1 = (3*width, 0)
    p2 = (3*width, height + 2*buffer_height)
    p3 = (0, height + 2*buffer_height)
    p.add_lines([p0, p1, p2, p3, p0], mode=LaserCutter.ENGRAVE)
    return p


if __name__ == '__main__':
    width = 30
    height = 150.
    nx = 3
    ny = 12
    buffer_width = 0.  # 2.5
    buffer_height = 10.  # 5.  # mm, extra length on end to use as a handle
    width -= 2*buffer_width
    # height -= 2*buffer_height
    seamhole_diameter = 3.  # mm
    kerf = 3.  # mm
    # gap = 1.5  # (5*3+4*3+7*2)*0.0254 #  1.5  # mm, for defining the straight line segments
    angle = np.pi/6
    l = (width/nx)/2/np.cos(angle)
    gap = 0.156*l
    cell_width = width/nx
    ny = int(height/(cell_width/2*np.tan(angle)))

    # Derived constants
    cell_width = width/nx
    cell_height = height/ny

    now = datetime.now()
    # name_clarifier = "_triangular_pattern_nx={:d}xny={:d}_wx={:.2f}xwy={:.2f}_gap={:.2f}_noseamholes".format(
    #     nx, ny, cell_width, cell_height, gap)
    name_clarifier = "_triangular_assembly_nx={:d}xny={:d}_wx={:.2f}xwy={:.2f}_bx={:.2f}xby={:.2f}_gap={:.2f}".format(
        nx, ny, cell_width, cell_height, buffer_width, buffer_height, gap)
    timestamp = now.strftime("%Y%m%d_%H_%M_%S") + name_clarifier
    print(timestamp)
    p = generate_triangular_pattern(width, height, nx, angle, buffer_width, buffer_height, gap)

    # p.generate_svg('../patterns/' + timestamp + '.svg', save=True, default_linewidth=0.02)
    p.generate_dxf('../patterns/' + timestamp + '.dxf', save=True)
