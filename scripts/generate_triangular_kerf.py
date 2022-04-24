from pattern import *
from settings import *
import numpy as np
from datetime import datetime


def generate_triangular_pattern(width, height, nx, angle, buffer_width, buffer_height, gap, kerf):
    p = Pattern(setting=LaserCutter)
    # Derived constants
    cell_width = width/nx
    # angle = np.arctan2(cell_height, cell_width/2)
    # angle = np.pi/6
    ny = int(height/(cell_width/2*np.tan(angle)))
    cell_height = height/ny
    gap_x = gap*np.cos(angle)
    gap_y = gap*np.sin(angle)
    kerf_x = kerf*np.sin(angle)/2
    kerf_y = kerf*np.cos(angle)/2
    # gap = 2*kerf + gap

    # Define horizontal cuts
    for j in range(0, ny):
        if j%2 == 1:
            for i in range(nx):
                # p0 = (cell_width*i + gap_x + buffer_width, cell_height*j + gap_y + buffer_height)
                # p1 = (cell_width*(i + 1/2) + buffer_width, cell_height*(j + 1) + buffer_height)
                # p2 = (cell_width*(i + 1) - gap_x + buffer_width, cell_height*j + gap_y + buffer_height)
                # p.add_lines([p0, p1, p2])
                # p.add_lines(p.offset_trace(p.generate_rounded_curve([p0, p1, p2], kerf/2, 4), kerf/2, round_ends=True))
                # p.add_lines(p.generate_rounded_curve(p.offset_trace([p0, p1, p2], kerf/2, round_ends=True), kerf/2, 4))
                # Top
                # p0 = (cell_width*i + gap_x + buffer_width - kerf_x, cell_height*j + gap_y + buffer_height + kerf_y)
                # p1 = (cell_width*(i + 1/2) + buffer_width - kerf_x, cell_height*(j + 1) + buffer_height + kerf_y)
                # p.add_line(p0, p1)
                # p0 = (cell_width*(i + 1/2) + buffer_width + kerf_x, cell_height*(j + 1) + buffer_height + kerf_y)
                # p1 = (cell_width*(i + 1) - gap_x + buffer_width + kerf_x, cell_height*j + gap_y + buffer_height + kerf_y)
                # p.add_line(p0, p1)
                # p0 = (cell_width*i + gap_x + buffer_width + kerf_x, cell_height*j + gap_y + buffer_height - kerf_y)
                # p1 = (cell_width*(i + 1/2) + buffer_width - kerf_x, cell_height*(j + 1) + buffer_height - kerf_y)
                # p.add_line(p0, p1)
                # p0 = (cell_width*(i + 1/2) + buffer_width + kerf_x, cell_height*(j + 1) + buffer_height - kerf_y)
                # p1 = (cell_width*(i + 1) - gap_x + buffer_width - kerf_x, cell_height*j + gap_y + buffer_height - kerf_y)
                # p.add_line(p0, p1)
                p0 = (cell_width*i + gap_x + buffer_width + kerf/2*np.cos(angle) - kerf/2*np.sin(angle),
                      cell_height*j + gap_y + buffer_height + kerf/2*np.sin(angle) + kerf/2*np.cos(angle))
                p1 = (cell_width*(i + 1/2) + buffer_width, cell_height*(j + 1) + buffer_height + kerf/2/np.cos(angle))
                p2 = (cell_width*(i + 1) - gap_x + buffer_width - kerf/2*np.cos(angle) + kerf/2*np.sin(angle),
                      cell_height*j + gap_y + buffer_height + kerf/2*np.sin(angle) + kerf/2*np.cos(angle))
                # p.add_lines(p.generate_rounded_curve([p0, p1, p2], kerf/2, 5))
                p.add_lines([p0, p1, p2])

                p0 = (cell_width*i + gap_x + buffer_width + kerf/2*np.cos(angle) + kerf/2*np.sin(angle),
                      cell_height*j + gap_y + buffer_height + kerf/2*np.sin(angle) - kerf/2*np.cos(angle))
                p1 = (cell_width*(i + 1/2) + buffer_width, cell_height*(j + 1) + buffer_height - kerf/2/np.cos(angle))
                p2 = (cell_width*(i + 1) - gap_x + buffer_width - kerf/2*np.cos(angle) - kerf/2*np.sin(angle),
                      cell_height*j + gap_y + buffer_height + kerf/2*np.sin(angle) - kerf/2*np.cos(angle))
                # p.add_lines(p.generate_rounded_curve([p0, p1, p2], kerf/2, 5))
                p.add_lines([p0, p1, p2])

                # Left arc
                p.add_arc((cell_width*i + gap_x + buffer_width + kerf/2*np.cos(angle),
                           cell_height*j + gap_y + buffer_height + kerf/2*np.sin(angle)), kerf/2, 4,
                          start_angle=angle + 3*np.pi/2, end_angle=angle + np.pi/2)
                p.add_arc((cell_width*(i + 1) - gap_x + buffer_width - kerf/2*np.cos(angle),
                           cell_height*j + gap_y + buffer_height + kerf/2*np.sin(angle)), kerf/2, 4,
                          start_angle=-angle - np.pi/2, end_angle=-angle + np.pi/2)
        else:
            for i in range(-1, nx):
                # p0 = (cell_width*(i + 1/2) + gap_x + buffer_width, cell_height*j + gap_y + buffer_height)
                # p1 = (cell_width*(i + 1) + buffer_width, cell_height*(j + 1) + buffer_height)
                # p2 = (cell_width*(i + 3/2) - gap_x + buffer_width, cell_height*j + gap_y + buffer_height)
                # if i == -1:
                #     pts = [p1, p2]
                # elif i == nx - 1:
                #     pts = [p0, p1]
                # else:
                #     pts = [p0, p1, p2]
                # p.add_lines(pts)
                # p.add_lines(p.offset_trace(p.generate_rounded_curve(pts, kerf/2, 4), kerf/2))

                p0 = (cell_width*(i + 1/2) + gap_x + buffer_width + kerf/2*np.cos(angle) - kerf/2*np.sin(angle),
                      cell_height*j + gap_y + buffer_height + kerf/2*np.sin(angle) + kerf/2*np.cos(angle))
                p1 = (cell_width*(i + 1) + buffer_width, cell_height*(j + 1) + buffer_height + kerf/2/np.cos(angle))
                p2 = (cell_width*(i + 3/2) - gap_x + buffer_width - kerf/2*np.cos(angle) + kerf/2*np.sin(angle),
                      cell_height*j + gap_y + buffer_height + kerf/2*np.sin(angle) + kerf/2*np.cos(angle))
                # pts_top = p.generate_rounded_curve([p0, p1, p2], kerf/2, 5)
                pts_top = [p0, p1, p2]
                if i == -1:
                    pts_top = [pt for pt in pts_top if pt[0] >= 0]
                if i == nx - 1:
                    pts_top = [pt for pt in pts_top if pt[0] <= width]
                p.add_lines(pts_top)

                p0 = (cell_width*(i + 1/2) + gap_x + buffer_width + kerf/2*np.cos(angle) + kerf/2*np.sin(angle),
                      cell_height*j + gap_y + buffer_height + kerf/2*np.sin(angle) - kerf/2*np.cos(angle))
                p1 = (cell_width*(i + 1) + buffer_width, cell_height*(j + 1) + buffer_height - kerf/2/np.cos(angle))
                p2 = (cell_width*(i + 3/2) - gap_x + buffer_width - kerf/2*np.cos(angle) - kerf/2*np.sin(angle),
                      cell_height*j + gap_y + buffer_height + kerf/2*np.sin(angle) - kerf/2*np.cos(angle))
                # pts_bottom = p.generate_rounded_curve([p0, p1, p2], kerf/2, 5)
                pts_bottom = [p0, p1, p2]
                if i == -1:
                    pts_bottom = [pt for pt in pts_bottom if pt[0] >= 0]
                if i == nx - 1:
                    pts_bottom = [pt for pt in pts_bottom if pt[0] <= width]
                p.add_lines(pts_bottom)

                if i != -1:
                    p.add_arc((cell_width*(i + 1/2) + gap_x + buffer_width + kerf/2*np.cos(angle),
                               cell_height*j + gap_y + buffer_height + kerf/2*np.sin(angle)), kerf/2, 4,
                              start_angle=angle + 3*np.pi/2, end_angle=angle + np.pi/2)
                else:
                    p.add_line(pts_top[0], pts_bottom[0])
                if i != nx - 1:
                    p.add_arc((cell_width*(i + 3/2) - gap_x + buffer_width - kerf/2*np.cos(angle),
                               cell_height*j + gap_y + buffer_height + kerf/2*np.sin(angle)), kerf/2, 4,
                              start_angle=-angle - np.pi/2, end_angle=-angle + np.pi/2)
                else:
                    p.add_line(pts_top[-1], pts_bottom[-1])

                # p0 = (cell_width*(i + 1/2) + gap_x + buffer_width - kerf_x, cell_height*j + gap_y + buffer_height + kerf_y)
                # p1 = (cell_width*(i + 1) + buffer_width - kerf_x, cell_height*(j + 1) + buffer_height + kerf_y)
                # p.add_line(p0, p1)
                # p0 = (cell_width*(i + 1) + buffer_width + kerf_x, cell_height*(j + 1) + buffer_height + kerf_y)
                # p1 = (cell_width*(i + 3/2) - gap_x + buffer_width + kerf_x, cell_height*j + gap_y + buffer_height + kerf_y)
                # p.add_line(p0, p1)
                # p0 = (cell_width*(i + 1/2) + gap_x + buffer_width + kerf_x, cell_height*j + gap_y + buffer_height - kerf_y)
                # p1 = (cell_width*(i + 1) + buffer_width - kerf_x, cell_height*(j + 1) + buffer_height - kerf_y)
                # p.add_line(p0, p1)
                # p0 = (cell_width*(i + 1) + buffer_width + kerf_x, cell_height*(j + 1) + buffer_height - kerf_y)
                # p1 = (cell_width*(i + 3/2) - gap_x + buffer_width - kerf_x, cell_height*j + gap_y + buffer_height - kerf_y)
                # p.add_line(p0, p1)

    # Define seam holes
    # for i in [cell_width/2, cell_width*3/2, width - cell_width*3/2, width - cell_width/2]:
    #     for j in [cell_height/2 + cell_height*j for j in range(ny)]:
    #         p.add_circle((i, j + buffer_height), seamhole_diameter/2)

    # Define border
    p.add_rectangle((0, 0), (width + 2*buffer_width, height + 2*buffer_height))
    # p0 = (0, 0)
    # p1 = (width, 0)
    # p2 = (width, height + 2*buffer_height)
    # p3 = 0, height + 2*buffer_height
    # p.add_line(p0, p1)
    # y_edges = [p1[1]]
    # for j in range(1, ny, 2):
    #     y_edges.append(cell_height*j - kerf/2 + buffer_height)
    #     y_edges.append(cell_height*j + kerf/2 + buffer_height)
    # y_edges.append(height + 2*buffer_height)
    # for j in range(0, len(y_edges) - 1, 2):
    #     p.add_line((width, y_edges[j]), (width, y_edges[j + 1]))
    # p.add_line(p2, p3)
    # for j in range(0, len(y_edges) - 1, 2):
    #     p.add_line((0, y_edges[j]), (0, y_edges[j + 1]))
    return p


if __name__ == '__main__':
    width = 32.07
    height = 150.
    nx = 3
    # ny = 12
    buffer_width = 0.  # 2.5
    buffer_height = 5.  # mm, extra length on end to use as a handle
    width -= 2*buffer_width
    # height -= 2*buffer_height
    seamhole_diameter = 3.  # mm
    kerf = 0.25  # mm
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
    name_clarifier = "_triangular_kerf_nx={:d}xny={:d}_wx={:.2f}xwy={:.2f}_bx={:.2f}xby={:.2f}_gap={:.2f}_kerf={:.2f}".format(
        nx, ny, cell_width, cell_height, buffer_width, buffer_height, gap, kerf)
    timestamp = now.strftime("%Y%m%d_%H_%M_%S") + name_clarifier
    print(timestamp)
    p = generate_triangular_pattern(width, height, nx, angle, buffer_width, buffer_height, gap, kerf)

    # p.generate_svg('../patterns/' + timestamp + '.svg', save=True, default_linewidth=0.02)
    p.generate_dxf('../patterns/' + timestamp + '.dxf', save=True)
