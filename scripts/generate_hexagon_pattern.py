from pattern import *
from settings import *
import numpy as np
from datetime import datetime


def generate_hexagon_pattern(nx, ny, s, buffer_height, seamhole_diameter, spring_radius, spring_gap, spring_thickness,
                             gap):
    p = Pattern(setting=LaserCutter)
    # Derived constants
    cell_width = 1.5*s
    cell_height = np.sqrt(3)*s
    s_short = 0.5*(s - gap/2)
    s_long = np.sqrt(3)/2*(s - gap/2)
    cutout_width = 4*spring_radius + 3*spring_gap + 2*spring_thickness
    cutout_depth = 2*spring_radius

    # cutout_width_x = cutout_width*0.5
    # cutout_width_y = cutout_width*np.sqrt(3)/2
    # cutout_depth_x = cutout_depth*0.5
    # cutout_depth_y = cutout_depth*np.sqrt(3)/2

    # Define hexagons
    def add_side(pstart, pend, omit_first_point=False):
        center = ((pstart[0] + pend[0])/2, (pstart[1] + pend[1])/2)
        theta = np.arctan2(pend[1] - pstart[1], pend[0] - pstart[0])
        cutout_width_x = cutout_width*np.cos(theta)
        cutout_width_y = cutout_width*np.sin(theta)
        cutout_depth_x = cutout_depth*np.sin(theta)
        cutout_depth_y = cutout_depth*np.cos(theta)

        p1 = pstart
        p2 = (center[0] - cutout_width_x/2, center[1] - cutout_width_y/2)
        p3 = (p2[0] + cutout_depth_x, p2[1] - cutout_depth_y)
        bottom_edge = spring_gap + 2*spring_radius - spring_thickness/2
        p4 = (p3[0] + bottom_edge*np.cos(theta),
              p3[1] + bottom_edge*np.sin(theta))
        p5 = (p4[0] - (gap/2)*np.sin(theta),
              p4[1] + (gap/2)*np.cos(theta))
        p.add_lines([p1, p2, p3, p4, p5])
        spring_inner_radius = spring_radius - spring_thickness/2
        spring_outer_radius = spring_radius + spring_thickness/2
        p6 = (p5[0] - spring_inner_radius*np.cos(theta),
              p5[1] - spring_inner_radius*np.sin(theta))
        p.add_circle(p6, spring_inner_radius, start_angle=theta, end_angle=theta + np.pi/2)
        p7 = (p6[0] - (2*spring_radius)*np.sin(theta),
              p6[1] + (2*spring_radius)*np.cos(theta))
        p.add_circle(p7, spring_outer_radius, start_angle=theta - np.pi/2, end_angle=theta - np.pi)

        p.add_circle(p7, spring_inner_radius, start_angle=theta - np.pi/2, end_angle=theta - np.pi)
        p.add_circle(p6, spring_outer_radius, start_angle=theta, end_angle=theta + np.pi/2)
        p8 = (p6[0] + spring_outer_radius*np.cos(theta),
              p6[1] + spring_outer_radius*np.sin(theta))
        p9 = (p8[0] + (gap/2)*np.sin(theta),
              p8[1] - (gap/2)*np.cos(theta))
        p10 = (p9[0] + spring_gap*np.cos(theta),
               p9[1] + spring_gap*np.sin(theta))
        p11 = (p10[0] - (gap/2)*np.sin(theta),
               p10[1] + (gap/2)*np.cos(theta))
        p.add_lines([p8, p9, p10, p11])

        p1 = pend
        p2 = (center[0] + cutout_width_x/2, center[1] + cutout_width_y/2)
        p3 = (p2[0] + cutout_depth_x, p2[1] - cutout_depth_y)
        p4 = (p3[0] - bottom_edge*np.cos(theta),
              p3[1] - bottom_edge*np.sin(theta))
        p5 = (p4[0] - (gap/2)*np.sin(theta),
              p4[1] + (gap/2)*np.cos(theta))
        p.add_lines([p1, p2, p3, p4, p5])
        p6 = (p5[0] + spring_inner_radius*np.cos(theta),
              p5[1] + spring_inner_radius*np.sin(theta))
        p.add_circle(p6, spring_inner_radius, start_angle=theta + np.pi, end_angle=theta + np.pi/2)
        p7 = (p6[0] - (2*spring_radius)*np.sin(theta),
              p6[1] + (2*spring_radius)*np.cos(theta))
        p.add_circle(p7, spring_outer_radius, start_angle=theta - np.pi/2, end_angle=theta)
        p.add_circle(p7, spring_inner_radius, start_angle=theta - np.pi/2, end_angle=theta)
        p.add_circle(p6, spring_outer_radius, start_angle=theta + np.pi, end_angle=theta + np.pi/2)

    for i in range(nx):
        for j in range(ny):
            if i%2 == 0:
                center = (cell_width*i, cell_height*j)
            else:
                center = (cell_width*i, cell_height*j + s_long + gap/2)
            lefttop = (center[0] - s_short, center[1] + s_long)
            left = (center[0] - (s - gap/2), center[1])
            leftbot = (center[0] - s_short, center[1] - s_long)
            rightbot = (center[0] + s_short, center[1] - s_long)
            right = (center[0] + (s - gap/2), center[1])
            righttop = (center[0] + s_short, center[1] + s_long)

            add_side(lefttop, righttop)
            add_side(righttop, right, omit_first_point=True)
            add_side(right, rightbot, omit_first_point=True)
            add_side(rightbot, leftbot, omit_first_point=True)
            add_side(leftbot, left, omit_first_point=True)
            add_side(left, lefttop, omit_first_point=True)
            # points.append((center[0] - s_short, center[1] + s_long))  # left top
            # points.append((center[0] - (s - gap/2), center[1]))  # left
            # points.append((center[0] - s_short, center[1] - s_long))  # left bottom
            # points.append((center[0] + s_short, center[1] - s_long))  # right bottom
            # points.append((center[0] + (s - gap/2), center[1]))  # right
            # points.append((center[0] + s_short, center[1] + s_long))  # right top
            # points.append((center[0] - s_short, center[1] + s_long))  # left top
            # p.add_lines(points)

    return p


if __name__ == '__main__':
    nx = 14
    ny = 20
    s = 10.
    buffer_height = 20.  # mm, extra length on end to use as a handle
    seamhole_diameter = 3.  # mm
    spring_radius = 0.6  # radius of the two sinusoidal springs
    spring_gap = 0.7  # gap between the two sinusoidal springs
    spring_thickness = 0.5  # thickness of the sinusoidal springs
    gap = 3.  # gap between hexagons

    now = datetime.now()
    name_clarifier = "_hexagon_pattern_nx={:d}xny={:d}_s={:.2f}_springradius={:.2f}_springgap={:.2f}_springthickness={:.2f}_gap={:.2f}_noseamholes".format(
        nx, ny, s, spring_radius, spring_gap, spring_thickness, gap
    )
    timestamp = now.strftime("%Y%m%d_%H_%M_%S") + name_clarifier
    print(timestamp)
    p = generate_hexagon_pattern(nx, ny, s, buffer_height, seamhole_diameter, spring_radius, spring_gap,
                                 spring_thickness, gap)

    p.generate_svg('../patterns/' + timestamp + '.svg', save=True, offset_x=s, offset_y=np.sqrt(3)/2*s)
    # p.generate_dxf('../patterns/' + timestamp + '.dxf', save=True, offset_x=1.5*s, offset_y=np.sqrt(3)/2*s)
