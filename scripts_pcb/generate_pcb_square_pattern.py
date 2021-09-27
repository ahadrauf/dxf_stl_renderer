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

    # Define horizontal cuts
    for j in range(1, ny):
        if j%2 == 1:
            for i in range(nx//2 + 1):
                for k in [kerf/2, -kerf/2]:
                    start_pos = (max(0., cell_width*(2*i - 1) + gap/2), cell_height*j + k + buffer_height)
                    end_pos = (min(width, cell_width*(2*i + 1) - gap/2), cell_height*j + k + buffer_height)
                    out += add_boundary([start_pos, end_pos], linestart=linestart)
                if i != 0:  # Add left arc
                    center = (max(0., cell_width*(2*i - 1) + gap/2), cell_height*j + buffer_height)
                    out += add_arc(center, kerf/2, start_angle=-np.pi/2, end_angle=-3*np.pi/2, linestart=linestart)
                if i != (nx//2):  # Add right arc
                    center = (min(width, cell_width*(2*i + 1) - gap/2), cell_height*j + buffer_height)
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
    p0 = (0, 0)
    p1 = (width, 0)
    p2 = (width, height + 2*buffer_height)
    p3 = 0, height + 2*buffer_height
    out += add_boundary([p0, p1], linestart=linestart)
    y_edges = [p1[1]]
    for j in range(1, ny, 2):
        y_edges.append(cell_height*j - kerf/2 + buffer_height)
        y_edges.append(cell_height*j + kerf/2 + buffer_height)
    y_edges.append(height + 2*buffer_height)
    for j in range(0, len(y_edges) - 1, 2):
        out += add_boundary([(width, y_edges[j]), (width, y_edges[j + 1])], linestart=linestart)
    out += add_boundary([p2, p3], linestart=linestart)
    for j in range(0, len(y_edges) - 1, 2):
        out += add_boundary([(0, y_edges[j]), (0, y_edges[j + 1])], linestart=linestart)

    return out


def generate_square_wiring(width, height, nx, ny, buffer_height, seamhole_diameter, kerf, gap):
    # Derived constants
    cell_width = width/nx
    cell_height = height/ny
    gap = 2*kerf + gap
    N_corner = 5

    linestart = '  '
    out = ""
    pad_spacing_x = 2*LINESPACE*np.ceil(ny//2) + BOARD_EDGE_SPACING
    pad_spacing_y = BOARD_EDGE_SPACING
    pad_width = cell_width - kerf - 2*pad_spacing_x
    pad_height = cell_height - kerf - 2*pad_spacing_y
    pad_corner_radius = cell_width/10.

    N_connector_pads = nx*ny//2
    w_connector_pads = width/N_connector_pads - 2*BOARD_EDGE_SPACING
    h_connector_pads = buffer_height*0.75
    conector_pad_corner_radius = w_connector_pads/10.

    # Add main pads
    for i in range(nx):
        for j in range(ny):
            # x = cell_width*i + kerf/2
            # y = cell_height*j + buffer_height + kerf/2
            # out += add_fill_zone_rectangle((x + pad_spacing_x, y + pad_spacing_y),
            #                                (x + cell_width - kerf - pad_spacing_x,
            #                                 y + cell_height - kerf - pad_spacing_y), linestart=linestart)

            x = cell_width*i + kerf/2 + pad_spacing_x
            y = cell_height*j + buffer_height + kerf/2 + pad_spacing_y
            pts = [(x + pad_corner_radius, y), (x + pad_width - pad_corner_radius, y)]
            pts += [(x + pad_width - pad_corner_radius*(1-np.sin(theta)), y + pad_corner_radius*(1-np.cos(theta)))
                    for theta in np.linspace(0., np.pi/2, N_corner)]
            pts += [(x + pad_width, y + pad_corner_radius), (x + pad_width, y + pad_height - pad_corner_radius)]
            pts += [(x + pad_width - pad_corner_radius*(1-np.cos(theta)), y + pad_height - pad_corner_radius*(1-np.sin(theta)))
                    for theta in np.linspace(0., np.pi/2, N_corner)]
            pts += [(x + pad_width - pad_corner_radius, y + pad_height), (x + pad_corner_radius, y + pad_height)]
            pts += [(x + pad_corner_radius*(1-np.sin(theta)), y + pad_height - pad_corner_radius*(1-np.cos(theta)))
                    for theta in np.linspace(0., np.pi/2, N_corner)]
            pts += [(x, y + pad_height - pad_corner_radius), (x, y + pad_corner_radius)]
            pts += [(x + pad_corner_radius*(1 - np.sin(theta)), y + pad_corner_radius*(1 - np.cos(theta)))
                    for theta in np.linspace(0., np.pi/2, N_corner)]
            out += add_fill_zone_polygon(pts, linestart=linestart)

    # Add connector pads to each side
    for i in range(N_connector_pads):
        topleft = (width/N_connector_pads*i + BOARD_EDGE_SPACING, buffer_height/2 - h_connector_pads/2)
        bottomright = (width/N_connector_pads*(i + 1) - BOARD_EDGE_SPACING, buffer_height/2 + h_connector_pads/2)
        out += add_fill_zone_rectangle(topleft, bottomright, linestart=linestart)

        topleft = (width/N_connector_pads*i + BOARD_EDGE_SPACING,
                   height + 2*buffer_height - (buffer_height/2 - h_connector_pads/2))
        bottomright = (width/N_connector_pads*(i + 1) - BOARD_EDGE_SPACING,
                       height + 2*buffer_height - (buffer_height/2 + h_connector_pads/2))
        out += add_fill_zone_rectangle(topleft, bottomright, linestart=linestart)

    return out


if __name__ == '__main__':
    width = 40.
    height = 40.
    nx = 4
    ny = 4
    buffer_height = 20.  # mm, extra length on end to use as a handle
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
