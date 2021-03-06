from pattern import *
from settings import *
import numpy as np
from datetime import datetime


def generate_squarelv1_pattern(width, height, nx, ny, buffer_height, seamhole_diameter, kerf, gap):
    p = Pattern(setting=LaserCutter)
    # Derived constants
    cell_width = width/nx
    cell_height = height/ny
    gap = 2*kerf + gap

    # Define horizontal cuts
    for j in range(1, ny):
        if j%2 == 1:
            for i in range(nx//2 + 1):
                for k in [kerf/2, -kerf/2]:
                    start_pos = (max(0., cell_width*(2*i - 1) + gap/2), cell_height*j + k + buffer_height)
                    end_pos = (min(width, cell_width*(2*i + 1) - gap/2), cell_height*j + k + buffer_height)
                    p.add_line(start_pos, end_pos)
                if i != 0:  # Add left arc
                    center = (max(0., cell_width*(2*i - 1) + gap/2), cell_height*j + buffer_height)
                    p.add_arc(center, kerf/2, start_angle=-np.pi/2, end_angle=-3*np.pi/2)
                if i != (nx//2):  # Add right arc
                    center = (min(width, cell_width*(2*i + 1) - gap/2), cell_height*j + buffer_height)
                    p.add_arc(center, kerf/2, start_angle=np.pi/2, end_angle=-np.pi/2)
        else:
            for i in range(nx//2):
                for k in [kerf/2, -kerf/2]:
                    start_pos = (cell_width*(2*i) + gap/2, cell_height*j + k + buffer_height)
                    end_pos = (cell_width*(2*i + 2) - gap/2, cell_height*j + k + buffer_height)
                    p.add_line(start_pos, end_pos)
                if True:  # Add left arc
                    center = (cell_width*(2*i) + gap/2, cell_height*j + buffer_height)
                    p.add_arc(center, kerf/2, start_angle=-np.pi/2, end_angle=-3*np.pi/2)
                if i != (nx//2):  # Add right arc
                    center = (cell_width*(2*i + 2) - gap/2, cell_height*j + buffer_height)
                    p.add_arc(center, kerf/2, start_angle=np.pi/2, end_angle=-np.pi/2)

    # Define vertical cuts
    for i in range(1, nx):
        if i%2 == 0:
            for j in range(ny//2 + 1):
                for k in [kerf/2, -kerf/2]:
                    start_pos = (cell_width*i + k, max(0., cell_height*(2*j - 1) + gap/2) + buffer_height)
                    end_pos = (cell_width*i + k, min(height, cell_height*(2*j + 1) - gap/2) + buffer_height)
                    p.add_line(start_pos, end_pos)
                if True:  # Add bottom arc
                    center = (cell_width*i, max(0., cell_height*(2*j - 1) + gap/2) + buffer_height)
                    p.add_arc(center, kerf/2, start_angle=-np.pi, end_angle=0)
                if True:  # Add top arc
                    center = (cell_width*i, min(height, cell_height*(2*j + 1) - gap/2) + buffer_height)
                    p.add_arc(center, kerf/2, start_angle=np.pi, end_angle=0)
        else:
            for j in range(ny//2):
                for k in [kerf/2, -kerf/2]:
                    start_pos = (cell_width*i + k, cell_height*(2*j) + gap/2 + buffer_height)
                    end_pos = (cell_width*i + k, cell_height*(2*j + 2) - gap/2 + buffer_height)
                    p.add_line(start_pos, end_pos)
                if True:  # Add bottom arc
                    center = (cell_width*i, cell_height*(2*j) + gap/2 + buffer_height)
                    p.add_arc(center, kerf/2, start_angle=-np.pi, end_angle=0)
                if True:  # Add top arc
                    center = (cell_width*i, cell_height*(2*j + 2) - gap/2 + buffer_height)
                    p.add_arc(center, kerf/2, start_angle=np.pi, end_angle=0)

    # Define seam holes
    # for i in [cell_width/2, cell_width*3/2, width - cell_width*3/2, width - cell_width/2]:
    #     for j in [cell_height/2 + cell_height*j for j in range(ny)]:
    #         p.add_circle((i, j + buffer_height), seamhole_diameter/2)

    # Define border
    p0 = (0, 0)
    p1 = (width, 0)
    p2 = (width, height + 2*buffer_height)
    p3 = 0, height + 2*buffer_height
    p.add_line(p0, p1)
    y_edges = [p1[1]]
    for j in range(1, ny, 2):
        y_edges.append(cell_height*j - kerf/2 + buffer_height)
        y_edges.append(cell_height*j + kerf/2 + buffer_height)
    y_edges.append(height + 2*buffer_height)
    for j in range(0, len(y_edges) - 1, 2):
        p.add_line((width, y_edges[j]), (width, y_edges[j + 1]))
    p.add_line(p2, p3)
    for j in range(0, len(y_edges) - 1, 2):
        p.add_line((0, y_edges[j]), (0, y_edges[j + 1]))
    return p


if __name__ == '__main__':
    width = 80.
    height = 120.
    nx = 8
    ny = 12
    buffer_height = 20.  # mm, extra length on end to use as a handle
    seamhole_diameter = 3.  # mm
    kerf = 3.  # mm
    gap = (5*3+4*3+7*2)*0.0254 #  1.5  # mm, for defining the straight line segments

    # Derived constants
    cell_width = width/nx
    cell_height = height/ny

    now = datetime.now()
    name_clarifier = "_square_pattern_nx={:d}xny={:d}_wx={:.2f}xwy={:.2f}_kerf={:.2f}_gap={:.2f}_noseamholes".format(
        nx, ny, cell_width, cell_height, kerf, gap
    )
    timestamp = now.strftime("%Y%m%d_%H_%M_%S") + name_clarifier
    print(timestamp)
    p = generate_squarelv1_pattern(width, height, nx, ny, buffer_height, seamhole_diameter, kerf, gap)

    # p.generate_svg('../patterns/' + timestamp + '.svg', save=True, default_linewidth=1)
    p.generate_dxf('../patterns/' + timestamp + '.dxf', save=True)
