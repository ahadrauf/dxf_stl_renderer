import numpy as np
from pcb_layout import *
from pcb_layout_plus_dxf import *
from datetime import datetime

def generate_squarelv1_pattern(p: PCBPattern, width, height, nx, ny, buffer_height, kerf, gap):
    # Derived constants
    cell_width = width/nx
    cell_height = height/ny
    gap = 2*kerf + gap

    linestart = '  '
    out = ""
    x_buffer = max(gap/2, M2_HOLE_DIAMETER/2 + BOARD_EDGE_SPACING_EFF)
    gap_edge = gap + M2_HOLE_DIAMETER + 2*BOARD_EDGE_SPACING_EFF  # gap for the edges (with seamholes)
    left_edge_x = -x_buffer
    right_edge_x = width + x_buffer
    total_width = right_edge_x - left_edge_x
    total_height = height + 2*buffer_height
    print("Total Width: {}, Total Height: {}".format(total_width, total_height))

    # Define horizontal cuts
    for layer in ["Edge.Cuts", "Eco2.User"]:
        for j in range(1, ny):
            if j%2 == 1:
                for i in range(nx//2 + 1):
                    for k in [kerf/2, -kerf/2]:
                        start_pos = (max(left_edge_x, cell_width*(2*i - 1) + gap/2), cell_height*j + k + buffer_height)
                        end_pos = (min(right_edge_x, cell_width*(2*i + 1) - gap/2), cell_height*j + k + buffer_height)
                        p.add_graphic_line([start_pos, end_pos], layer=layer)
                        # out += add_boundary([start_pos, end_pos], linestart=linestart)
                    if i != 0:  # Add left arc
                        center = (max(left_edge_x, cell_width*(2*i - 1) + gap/2), cell_height*j + buffer_height)
                        p.add_graphic_arc(center, kerf/2, -np.pi/2, -3*np.pi/2, layer=layer)
                        # out += add_arc(center, kerf/2, start_angle=-np.pi/2, end_angle=-3*np.pi/2, linestart=linestart)
                    if i != (nx//2):  # Add right arc
                        center = (min(right_edge_x, cell_width*(2*i + 1) - gap/2), cell_height*j + buffer_height)
                        p.add_graphic_arc(center, kerf/2, np.pi/2, -np.pi/2, layer=layer)
                        # out += add_arc(center, kerf/2, start_angle=np.pi/2, end_angle=-np.pi/2, linestart=linestart)
            else:
                for i in range(nx//2):
                    for k in [kerf/2, -kerf/2]:
                        start_pos = (cell_width*(2*i) + gap/2, cell_height*j + k + buffer_height)
                        end_pos = (cell_width*(2*i + 2) - gap/2, cell_height*j + k + buffer_height)
                        p.add_graphic_line([start_pos, end_pos], layer=layer)
                        # out += add_boundary([start_pos, end_pos], linestart=linestart)
                    if True:  # Add left arc
                        center = (cell_width*(2*i) + gap/2, cell_height*j + buffer_height)
                        p.add_graphic_arc(center, kerf/2, -np.pi/2, -3*np.pi/2, layer=layer)
                        # out += add_arc(center, kerf/2, start_angle=-np.pi/2, end_angle=-3*np.pi/2, linestart=linestart)
                    if i != (nx//2):  # Add right arc
                        center = (cell_width*(2*i + 2) - gap/2, cell_height*j + buffer_height)
                        p.add_graphic_arc(center, kerf/2, np.pi/2, -np.pi/2, layer=layer)
                        # out += add_arc(center, kerf/2, start_angle=np.pi/2, end_angle=-np.pi/2, linestart=linestart)

        # Define vertical cuts
        for i in range(0, nx + 1):
            if i%2 == 0:
                for j in range(ny//2 + 1):
                    for k in [kerf/2, -kerf/2]:
                        # if (i == 0 and k == -kerf/2) or (i == nx and k == kerf/2):
                        #     continue
                        start_pos = (cell_width*i + k, max(0., cell_height*(2*j - 1) +gap/2) + buffer_height)
                        end_pos = (cell_width*i + k, min(height, cell_height*(2*j + 1) - gap/2) + buffer_height)
                        p.add_graphic_line([start_pos, end_pos], layer=layer)
                        # out += add_boundary([start_pos, end_pos], linestart=linestart)
                    if True:  # Add bottom arc
                        center = (cell_width*i, max(0., cell_height*(2*j - 1) + gap/2) + buffer_height)
                        # if i == 0:
                        #     p.add_graphic_arc(center, kerf/2, -np.pi/2, 0, layer=layer)
                        # elif i == nx:
                        #     p.add_graphic_arc(center, kerf/2, -np.pi, -np.pi/2, layer=layer)
                        # else:
                        p.add_graphic_arc(center, kerf/2, -np.pi, 0, layer=layer)
                        # out += add_arc(center, kerf/2, start_angle=-np.pi, end_angle=0, linestart=linestart)
                    if True:  # Add top arc
                        center = (cell_width*i, min(height, cell_height*(2*j + 1) - gap/2) + buffer_height)
                        # if i == 0:
                        #     p.add_graphic_arc(center, kerf/2, np.pi/2, 0, layer=layer)
                        # elif i == nx:
                        #     p.add_graphic_arc(center, kerf/2, np.pi, np.pi/2, layer=layer)
                        # else:
                        p.add_graphic_arc(center, kerf/2, np.pi, 0, layer=layer)
                        # out += add_arc(center, kerf/2, start_angle=np.pi, end_angle=0, linestart=linestart)
            else:
                for j in range(ny//2):
                    for k in [kerf/2, -kerf/2]:
                        start_pos = (cell_width*i + k, cell_height*(2*j) + gap/2 + buffer_height)
                        end_pos = (cell_width*i + k, cell_height*(2*j + 2) - gap/2 + buffer_height)
                        p.add_graphic_line([start_pos, end_pos], layer=layer)
                        # out += add_boundary([start_pos, end_pos], linestart=linestart)
                    if True:  # Add bottom arc
                        center = (cell_width*i, cell_height*(2*j) + gap/2 + buffer_height)
                        p.add_graphic_arc(center, kerf/2, -np.pi, 0, layer=layer)
                        # out += add_arc(center, kerf/2, start_angle=-np.pi, end_angle=0, linestart=linestart)
                    if True:  # Add top arc
                        center = (cell_width*i, cell_height*(2*j + 2) - gap/2 + buffer_height)
                        p.add_graphic_arc(center, kerf/2, np.pi, 0, layer=layer)
                        # out += add_arc(center, kerf/2, start_angle=np.pi, end_angle=0, linestart=linestart)

    # Define seam holes
    for i in [cell_width/2, cell_width*3/2, width - cell_width*3/2, width - cell_width/2]:
        for j in [cell_height/2 + cell_height*j for j in range(ny)]:
            # add_arc((i, j + buffer_height), seamhole_diameter/2)
            # m2_text = add_M2_drill_nonplated((i, j + buffer_height))
            # p.add_object(m2_text)
            p.add_M2_drill((i, j + buffer_height), plated=False)

    # Define border
    for layer in ["Edge.Cuts", "Eco2.User"]:
        p0 = (left_edge_x, 0)
        p1 = (right_edge_x, 0)
        p2 = (right_edge_x, height + 2*buffer_height)
        p3 = (left_edge_x, height + 2*buffer_height)
        p.add_graphic_line([p0, p1], layer=layer)
        # out += add_boundary([p0, p1], linestart=linestart)
        y_edges = [p1[1]]
        for j in range(1, ny, 2):
            y_edges.append(cell_height*j - kerf/2 + buffer_height)
            y_edges.append(cell_height*j + kerf/2 + buffer_height)
        y_edges.append(height + 2*buffer_height)
        for j in range(0, len(y_edges) - 1, 2):
            p.add_graphic_line([(right_edge_x, y_edges[j]), (right_edge_x, y_edges[j + 1])], layer=layer)
            # out += add_boundary([(right_edge_x, y_edges[j]), (right_edge_x, y_edges[j + 1])], linestart=linestart)
        p.add_graphic_line([p2, p3], layer=layer)
        # out += add_boundary([p2, p3], linestart=linestart)
        for j in range(0, len(y_edges) - 1, 2):
            p.add_graphic_line([(left_edge_x, y_edges[j]), (left_edge_x, y_edges[j + 1])], layer=layer)
            # out += add_boundary([(left_edge_x, y_edges[j]), (left_edge_x, y_edges[j + 1])], linestart=linestart)

    return p

if __name__ == '__main__':
    width = 80.
    height = 120.
    nx = 4
    ny = 6
    buffer_height = 10.  # mm, extra length on end to use as a handle
    kerf = 1.  # mm
    gap = 1.5  # mm, for defining the straight line segments

    # Derived constants
    cell_width = width/nx
    cell_height = height/ny

    now = datetime.now()
    name_clarifier = "_square_pattern_nx={:d}xny={:d}_wx={:.2f}xwy={:.2f}_kerf={:.2f}_gap={:.2f}".format(
        nx, ny, cell_width, cell_height, kerf, gap
    )
    timestamp = now.strftime("%Y%m%d_%H_%M_%S") + name_clarifier
    print(timestamp)

    p = PCBPattern()
    p = generate_squarelv1_pattern(p, width, height, nx, ny, buffer_height, kerf, gap)
    # out += generate_square_wiring(width, height, nx, ny, buffer_height, seamhole_diameter, kerf, gap)
    # pyperclip.copy(out)

    kicad_filename = "C:/Users/ahadrauf/Desktop/Research/pcb_wire_testing_setup/pcb_wire_testing_setup.kicad_pcb"
    dxf_cut_filename = "C:/Users/ahadrauf/Desktop/Research/pcb_wire_testing_setup/pcb_wire_testing_setup_cut.dxf"
    dxf_etch_filename = "C:/Users/ahadrauf/Desktop/Research/pcb_wire_testing_setup/pcb_wire_testing_setup_etch.dxf"
    p.generate_kicad(kicad_filename, save=True, offset_x=0., offset_y=0.)
    p.generate_dxf(dxf_cut_filename, dxf_etch_filename, save=True, offset_x=0., offset_y=0.)
    # with open(filename, 'w') as f:
    #     f.write(out)
