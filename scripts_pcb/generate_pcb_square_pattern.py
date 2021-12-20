import numpy as np
from pcb_layout import *
from datetime import datetime
import pyperclip


# MIL_TO_MM = 0.0254
# LINESPACE = 3*MIL_TO_MM
# BOARD_EDGE_SPACING = 7*MIL_TO_MM


def generate_squarelv1_pattern(width, height, nx, ny, buffer_height, seamhole_diameter, kerf, gap):
    # Derived constants
    cell_width = width/nx
    cell_height = height/ny
    gap = 2*kerf + gap

    linestart = '  '
    out = ""
    left_edge_x = -1
    right_edge_x = width + 1

    # Define horizontal cuts
    for j in range(1, ny):
        if j%2 == 1:
            for i in range(nx//2 + 1):
                for k in [kerf/2, -kerf/2]:
                    start_pos = (max(left_edge_x, cell_width*(2*i - 1) + gap/2), cell_height*j + k + buffer_height)
                    end_pos = (min(right_edge_x, cell_width*(2*i + 1) - gap/2), cell_height*j + k + buffer_height)
                    out += add_boundary([start_pos, end_pos], linestart=linestart)
                if i != 0:  # Add left arc
                    center = (max(left_edge_x, cell_width*(2*i - 1) + gap/2), cell_height*j + buffer_height)
                    out += add_arc(center, kerf/2, start_angle=-np.pi/2, end_angle=-3*np.pi/2, linestart=linestart)
                if i != (nx//2):  # Add right arc
                    center = (min(right_edge_x, cell_width*(2*i + 1) - gap/2), cell_height*j + buffer_height)
                    out += add_arc(center, kerf/2, start_angle=np.pi/2, end_angle=-np.pi/2, linestart=linestart)
        else:
            for i in range(nx//2):
                for k in [kerf/2, -kerf/2]:
                    start_pos = (cell_width*(2*i) + gap/2, cell_height*j + k + buffer_height)
                    end_pos = (cell_width*(2*i + 2) - gap/2, cell_height*j + k + buffer_height)
                    out += add_boundary([start_pos, end_pos], linestart=linestart)
                if True:  # Add left arc
                    center = (cell_width*(2*i) + gap/2, cell_height*j + buffer_height)
                    out += add_arc(center, kerf/2, start_angle=-np.pi/2, end_angle=-3*np.pi/2, linestart=linestart)
                if i != (nx//2):  # Add right arc
                    center = (cell_width*(2*i + 2) - gap/2, cell_height*j + buffer_height)
                    out += add_arc(center, kerf/2, start_angle=np.pi/2, end_angle=-np.pi/2, linestart=linestart)

    # Define vertical cuts
    for i in range(1, nx):
        if i%2 == 0:
            for j in range(ny//2 + 1):
                for k in [kerf/2, -kerf/2]:
                    start_pos = (cell_width*i + k, max(0., cell_height*(2*j - 1) + gap/2) + buffer_height)
                    end_pos = (cell_width*i + k, min(height, cell_height*(2*j + 1) - gap/2) + buffer_height)
                    out += add_boundary([start_pos, end_pos], linestart=linestart)
                if True:  # Add bottom arc
                    center = (cell_width*i, max(0., cell_height*(2*j - 1) + gap/2) + buffer_height)
                    out += add_arc(center, kerf/2, start_angle=-np.pi, end_angle=0, linestart=linestart)
                if True:  # Add top arc
                    center = (cell_width*i, min(height, cell_height*(2*j + 1) - gap/2) + buffer_height)
                    out += add_arc(center, kerf/2, start_angle=np.pi, end_angle=0, linestart=linestart)
        else:
            for j in range(ny//2):
                for k in [kerf/2, -kerf/2]:
                    start_pos = (cell_width*i + k, cell_height*(2*j) + gap/2 + buffer_height)
                    end_pos = (cell_width*i + k, cell_height*(2*j + 2) - gap/2 + buffer_height)
                    out += add_boundary([start_pos, end_pos], linestart=linestart)
                if True:  # Add bottom arc
                    center = (cell_width*i, cell_height*(2*j) + gap/2 + buffer_height)
                    out += add_arc(center, kerf/2, start_angle=-np.pi, end_angle=0, linestart=linestart)
                if True:  # Add top arc
                    center = (cell_width*i, cell_height*(2*j + 2) - gap/2 + buffer_height)
                    out += add_arc(center, kerf/2, start_angle=np.pi, end_angle=0, linestart=linestart)

    # Define seam holes
    # for i in [cell_width/2, cell_width*3/2, width - cell_width*3/2, width - cell_width/2]:
    #     for j in [cell_height/2 + cell_height*j for j in range(ny)]:
    #         add_arc((i, j + buffer_height), seamhole_diameter/2)

    # Define border
    p0 = (left_edge_x, 0)
    p1 = (right_edge_x, 0)
    p2 = (right_edge_x, height + 2*buffer_height)
    p3 = (left_edge_x, height + 2*buffer_height)
    out += add_boundary([p0, p1], linestart=linestart)
    y_edges = [p1[1]]
    for j in range(1, ny, 2):
        y_edges.append(cell_height*j - kerf/2 + buffer_height)
        y_edges.append(cell_height*j + kerf/2 + buffer_height)
    y_edges.append(height + 2*buffer_height)
    for j in range(0, len(y_edges) - 1, 2):
        out += add_boundary([(right_edge_x, y_edges[j]), (right_edge_x, y_edges[j + 1])], linestart=linestart)
    out += add_boundary([p2, p3], linestart=linestart)
    for j in range(0, len(y_edges) - 1, 2):
        out += add_boundary([(left_edge_x, y_edges[j]), (left_edge_x, y_edges[j + 1])], linestart=linestart)

    return out


def generate_square_wiring(width, height, nx, ny, buffer_height, seamhole_diameter, kerf, gap):
    # Derived constants
    cell_width = width/nx
    cell_height = height/ny
    gap = 2*kerf + gap
    N_corner = 10
    trace_radius = 0.2

    linestart = '  '
    out = ""
    pad_spacing_x = 2*LINESPACE*np.ceil(ny//2) + BOARD_EDGE_SPACING_EFF
    pad_spacing_y = 2*LINESPACE*np.ceil(ny//2) + BOARD_EDGE_SPACING_EFF
    pad_width = cell_width - kerf - 2*pad_spacing_x
    pad_height = cell_height - kerf - 2*pad_spacing_y
    pad_corner_radius = cell_width/10.

    N_connector_pads = nx*ny//2
    # w_connector_pads = width/N_connector_pads - 2*BOARD_EDGE_SPACING_EFF
    w_connector_pads = (cell_width - kerf - 2*BOARD_EDGE_SPACING_EFF)//(ny//2)
    h_connector_pads = buffer_height*0.75
    conector_pad_corner_radius = w_connector_pads/10.
    print(cell_height)
    print(kerf)
    print(pad_spacing_y, BOARD_EDGE_SPACING, EDGECUT_WIDTH)
    print(kerf + 2*pad_spacing_y)

    # Add auxetic pads
    for i in range(nx):
        for j in range(ny):
            x = cell_width*i + kerf/2 + pad_spacing_x
            y = cell_height*j + buffer_height + kerf/2 + pad_spacing_y
            out += add_fill_zone_rounded_rectangle((x, y), (x + pad_width, y + pad_height), pad_corner_radius,
                                                   N=N_corner, linestart=linestart)
            out += add_fill_zone_rounded_rectangle((x, y), (x + pad_width, y + pad_height), pad_corner_radius,
                                                   N=N_corner, linestart=linestart, layer="F.Mask")

    # Add connection points between horizontal segments
    for j in range(ny):
        x = cell_width*0 + kerf/2 + pad_spacing_x - 1.2
        if j % 2 == 0:
            y = cell_height*j + buffer_height + kerf/2 + pad_spacing_y + pad_height - 1
        else:
            y = cell_height*j + buffer_height + kerf/2 + pad_spacing_y + 1
        out += add_M2_drill_nonplated((x, y), linestart=linestart)
        x = cell_width*(nx - 1) + kerf/2 + pad_spacing_x + pad_width + 1.2
        out += add_M2_drill_nonplated((x, y), linestart=linestart)

    return out
    # Add connector pads to each side
    for i in range(nx):
        # topleft = (width/N_connector_pads*i + BOARD_EDGE_SPACING_EFF, buffer_height/2 - h_connector_pads/2)
        # bottomright = (width/N_connector_pads*(i + 1) - BOARD_EDGE_SPACING_EFF, buffer_height/2 + h_connector_pads/2)
        # Since
        for j in range(ny//2):
            topleft = (cell_width*i + kerf/2 + w_connector_pads*j + BOARD_EDGE_SPACING_EFF*(j+1),
                       buffer_height/2 - h_connector_pads/2)
            bottomright = (topleft[0] + w_connector_pads, buffer_height/2 + h_connector_pads/2)
            out += add_fill_zone_rounded_rectangle(topleft, bottomright, conector_pad_corner_radius, N=N_corner,
                                                   linestart=linestart)
            # out += add_M2_drill_plated((topleft[0] + w_connector_pads/2, topleft[1]))

            topleft = (cell_width*i + kerf/2 + w_connector_pads*j + BOARD_EDGE_SPACING_EFF*(j+1),
                       height + 2*buffer_height - (buffer_height/2 + h_connector_pads/2))
            bottomright = (topleft[0] + w_connector_pads,
                           height + 2*buffer_height - (buffer_height/2 - h_connector_pads/2))
            out += add_fill_zone_rounded_rectangle(topleft, bottomright, conector_pad_corner_radius, N=N_corner,
                                                   linestart=linestart)
            # out += add_M2_drill_plated((topleft[0] + w_connector_pads/2, bottomright[1]))

    # Add traces to the exterior connector pads (the connector pads that are closest to their respective auxetic pads)
    # These occur at indices 0, ny-1, ny, 2*ny-1, 2*ny, ...
    # These are implemented separately because they can be routed on the opposite side from the other traces
    for i in np.arange(0, nx, 2):  # Start on the left side for these ones
        pts = [(cell_width*i + kerf/2 + BOARD_EDGE_SPACING_EFF + conector_pad_corner_radius,
                buffer_height/2 + h_connector_pads/2 - conector_pad_corner_radius)]
        x = cell_width*i + kerf/2 + pad_spacing_x + pad_width/2
        y = cell_height*0 + buffer_height + kerf/2 + pad_spacing_y + pad_height/2
        pts += [(x, y)]
        out += add_trace(pts)

        for j in range(1, ny//2):
            pts = [(cell_width*i + kerf/2 + w_connector_pads*j + BOARD_EDGE_SPACING_EFF*(j+1) +
                    BOARD_EDGE_SPACING_EFF - conector_pad_corner_radius,
                    buffer_height/2 + h_connector_pads/2 - conector_pad_corner_radius)]
            x = cell_width*i + kerf/2 + pad_spacing_x + pad_width/2
            y = cell_height*j + buffer_height + kerf/2 + pad_spacing_y + pad_height/2
            pts += [(x, y)]
            out += add_trace(pts)

        # Repeat for the bottom half of the pattern
        pts = [(cell_width*i + kerf/2 + BOARD_EDGE_SPACING_EFF + conector_pad_corner_radius,
                height + 2*buffer_height - (buffer_height/2 + h_connector_pads/2 - conector_pad_corner_radius))]
        x = cell_width*i + kerf/2 + pad_spacing_x + pad_width/2
        y = height + 2*buffer_height - (cell_height*0 + buffer_height + kerf/2 + pad_spacing_y + pad_height/2)
        pts += [(x, y)]
        out += add_trace(pts)

        for j in range(1, ny//2):
            pts = [(cell_width*i + kerf/2 + w_connector_pads*j + BOARD_EDGE_SPACING_EFF*(j + 1) +
                    BOARD_EDGE_SPACING_EFF - conector_pad_corner_radius,
                    height + 2*buffer_height - (buffer_height/2 + h_connector_pads/2 - conector_pad_corner_radius))]
            x = cell_width*i + kerf/2 + pad_spacing_x + pad_width/2
            y = height + 2*buffer_height - (cell_height*j + buffer_height + kerf/2 + pad_spacing_y + pad_height/2)
            pts += [(x, y)]
            out += add_trace(pts)
        # pts += [(pts[-1][0] - (trace_radius + conector_pad_corner_radius),
        #          pts[-1][1] + (trace_radius + conector_pad_corner_radius))]
        # print(pts)
        # pts += generate_arc(pts[-1], (pts[-1][0] - 5*trace_radius*np.sqrt(2)/2, pts[-1][1] + 5*trace_radius*np.sqrt(2)/2),
        #                     5*np.pi/4, N_corner)[1:]
        # pts += [(pts[-1][0], pts[-1][1] + 5)]
        # print(generate_arc(pts[-1], (pts[-1][0] - trace_radius*np.sqrt(2)/2, pts[-1][1] + trace_radius*np.sqrt(2)/2),
        #                     3*np.pi/4, N_corner))
    for i in np.arange(1, nx, 2):  # Start on the right side for these ones
        j = ny//2 - 1
        pts = [(cell_width*i + kerf/2 + w_connector_pads*(j+1) + BOARD_EDGE_SPACING_EFF*(j+1),
                buffer_height/2 + h_connector_pads/2)]
        x = cell_width*i + kerf/2 + pad_spacing_x + pad_width/2
        y = cell_height*0 + buffer_height + kerf/2 + pad_spacing_y + pad_height/2
        pts += [(x, y)]
        out += add_trace(pts)
        # pts += [(pts[-1][0] + trace_radius, pts[-1][1] + trace_radius)]
        # pts += generate_arc(pts[-1], (pts[-1][0] + trace_radius*np.sqrt(2)/2, pts[-1][1] + trace_radius*np.sqrt(2)/2),
        #                     np.pi/4, N_corner)[1:]

        for j in reversed(range(0, ny//2 - 1)):
            pts = [(cell_width*i + kerf/2 + w_connector_pads*j + BOARD_EDGE_SPACING_EFF*(j+1) +
                    BOARD_EDGE_SPACING_EFF - conector_pad_corner_radius,
                    buffer_height/2 + h_connector_pads/2 - conector_pad_corner_radius)]
            x = cell_width*i + kerf/2 + pad_spacing_x + pad_width/2
            y = cell_height*(ny//2 - 1 - j) + buffer_height + kerf/2 + pad_spacing_y + pad_height/2
            pts += [(x, y)]
            out += add_trace(pts)

        # Repeat for the bottom half of the pattern
        j = ny//2 - 1
        pts = [(cell_width*i + kerf/2 + w_connector_pads*(j + 1) + BOARD_EDGE_SPACING_EFF*(j + 1),
                height + 2*buffer_height - (buffer_height/2 + h_connector_pads/2))]
        x = cell_width*i + kerf/2 + pad_spacing_x + pad_width/2
        y = height + 2*buffer_height - (cell_height*0 + buffer_height + kerf/2 + pad_spacing_y + pad_height/2)
        pts += [(x, y)]
        out += add_trace(pts)

        for j in reversed(range(0, ny//2 - 1)):
            pts = [(cell_width*i + kerf/2 + w_connector_pads*j + BOARD_EDGE_SPACING_EFF*(j + 1) +
                    BOARD_EDGE_SPACING_EFF - conector_pad_corner_radius,
                    height + 2*buffer_height - (buffer_height/2 + h_connector_pads/2 - conector_pad_corner_radius))]
            x = cell_width*i + kerf/2 + pad_spacing_x + pad_width/2
            y = cell_height*(ny//2 - 1 - j) + buffer_height + kerf/2 + pad_spacing_y + pad_height/2
            pts += [(x, height + 2*buffer_height - y)]
            out += add_trace(pts)

    return out


if __name__ == '__main__':
    width = 40.
    height = 60.
    nx = 4
    ny = 6
    buffer_height = 10.  # mm, extra length on end to use as a handle
    seamhole_diameter = 3.  # mm
    kerf = 3.  # mm
    gap = 1.5  # mm, for defining the straight line segments

    # Derived constants
    cell_width = width/nx
    cell_height = height/ny

    now = datetime.now()
    name_clarifier = "_square_pattern_nx={:d}xny={:d}_wx={:.2f}xwy={:.2f}_kerf={:.2f}_gap={:.2f}_noseamholes".format(
        nx, ny, cell_width, cell_height, kerf, gap
    )
    timestamp = now.strftime("%Y%m%d_%H_%M_%S") + name_clarifier
    print(timestamp)

    out = add_header()
    out += generate_squarelv1_pattern(width, height, nx, ny, buffer_height, seamhole_diameter, kerf, gap)
    out += generate_square_wiring(width, height, nx, ny, buffer_height, seamhole_diameter, kerf, gap)
    out += add_footer()
    # pyperclip.copy(out)

    filename = "C:/Users/ahadrauf/Desktop/Research/pcb_wire_testing_setup/pcb_wire_testing_setup.kicad_pcb"
    with open(filename, 'w') as f:
        f.write(out)
