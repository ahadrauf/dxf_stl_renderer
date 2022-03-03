import numpy as np

import pcb_layout
from pcb_layout import *
from pcb_layout_plus_dxf import *
from datetime import datetime


def generate_squarelv1_pattern(p: PCBPattern, width, height, nx, ny, buffer_width, buffer_height, kerf, gap):
    # Derived constants
    cell_width = width/nx
    cell_height = height/ny
    gap_orig = gap
    gap = 2*kerf + 2*gap + 2*BOARD_EDGE_SPACING_EFF  # the BOARD_EDGE_SPACING_EFF term is just extra stress buffer

    x_buffer = max(kerf/2 + gap_orig, M2_HOLE_DIAMETER/2 + BOARD_EDGE_SPACING_EFF)
    gap_edge = max(gap,
                   2*kerf + 2*M2_COURTYARD_DIAMETER + 4*BOARD_EDGE_SPACING_EFF)  # gap for the edges (with seamholes)

    cutaway_gap = 0
    buffer_height_pins = buffer_height + 6
    left_edge_x = -x_buffer
    right_edge_x = width + x_buffer
    bottom_edge_y = -x_buffer  #  -buffer_height_pins
    top_edge_y = height + x_buffer

    total_width = right_edge_x - left_edge_x + 2*buffer_width
    total_height = top_edge_y - bottom_edge_y + buffer_height  # height + 2*buffer_height
    print("Total Width: {}, Total Height: {}".format(total_width, total_height))

    # Define horizontal cuts
    for layer in ["Edge.Cuts"]:  # , "Eco2.User"]:
    # for layer in ["F.SilkS"]:
        for j in range(0, ny + 1):
            if j%2 == 1:
                for i in range(nx//2 + 1):
                    for k in [kerf/2, -kerf/2]:
                        start_pos = (max(0, cell_width*(2*i - 1) + gap/2), cell_height*j + k)
                        end_pos = (min(width, cell_width*(2*i + 1) - gap/2), cell_height*j + k)
                        p.add_graphic_line([start_pos, end_pos], layer=layer)
                    if True:  # Add left arc
                        center = (max(0, cell_width*(2*i - 1) + gap/2), cell_height*j)
                        p.add_graphic_arc(center, kerf/2, -np.pi/2, -3*np.pi/2, layer=layer)
                    if True:  # Add right arc
                        center = (min(width, cell_width*(2*i + 1) - gap/2), cell_height*j)
                        p.add_graphic_arc(center, kerf/2, np.pi/2, -np.pi/2, layer=layer)
            else:
                for i in range(nx//2):
                    # gap_eff = gap_edge if (j == ny) else gap
                    gap_eff = gap
                    for k in [kerf/2, -kerf/2]:
                        start_pos = (cell_width*(2*i) + gap_eff/2, cell_height*j + k)
                        end_pos = (cell_width*(2*i + 2) - gap_eff/2, cell_height*j + k)
                        p.add_graphic_line([start_pos, end_pos], layer=layer)
                    if True:  # Add left arc
                        center = (cell_width*(2*i) + gap_eff/2, cell_height*j)
                        p.add_graphic_arc(center, kerf/2, -np.pi/2, -3*np.pi/2, layer=layer)
                    if True:  # Add right arc
                        center = (cell_width*(2*i + 2) - gap_eff/2, cell_height*j)
                        p.add_graphic_arc(center, kerf/2, np.pi/2, -np.pi/2, layer=layer)

        # Define vertical cuts
        for i in range(0, nx + 1):
            if i%2 == 0:
                # gap_eff = gap_edge if (i == 0 or i == nx) else gap
                gap_eff = gap
                for j in range(ny//2 + 1):
                    for k in [kerf/2, -kerf/2]:
                        start_pos = (cell_width*i + k, max(0., cell_height*(2*j - 1) + gap_eff/2))
                        end_pos = (cell_width*i + k, min(height, cell_height*(2*j + 1) - gap_eff/2))
                        if j == (ny // 2):
                            end_pos = (cell_width*i + k, height)
                        p.add_graphic_line([start_pos, end_pos], layer=layer)
                    if True:  # Add bottom arc
                        center = (cell_width*i, max(0., cell_height*(2*j - 1) + gap_eff/2))
                        p.add_graphic_arc(center, kerf/2, -np.pi, 0, layer=layer)
                    if True:  # Add top arc
                        center = (cell_width*i, min(height, cell_height*(2*j + 1) - gap_eff/2))
                        p.add_graphic_arc(center, kerf/2, np.pi, 0, layer=layer)
            else:
                for j in range(ny//2):
                    for k in [kerf/2, -kerf/2]:
                        start_pos = (cell_width*i + k, cell_height*(2*j) + gap/2)
                        end_pos = (cell_width*i + k, cell_height*(2*j + 2) - gap/2)
                        p.add_graphic_line([start_pos, end_pos], layer=layer)
                    if True:  # Add bottom arc
                        center = (cell_width*i, cell_height*(2*j) + gap/2)
                        p.add_graphic_arc(center, kerf/2, -np.pi, 0, layer=layer)
                    if True:  # Add top arc
                        center = (cell_width*i, cell_height*(2*j + 2) - gap/2)
                        p.add_graphic_arc(center, kerf/2, np.pi, 0, layer=layer)

    # Define seam holes
    for i in [0, width]:
        # for j in [cell_height/2 + cell_height*j for j in range(ny)]:
        for j in range(-1, ny):
            if j%2 == 0 or j == -1:
                center = (i, cell_height*(j + 1) - kerf/2 - BOARD_EDGE_SPACING_EFF - M2_COURTYARD_DIAMETER/2)
            else:
                center = (i, cell_height*j + kerf/2 + BOARD_EDGE_SPACING_EFF + M2_COURTYARD_DIAMETER/2)
            p.add_M2_drill(center, plated=False, cut=False, etch=False)
            # if i == 0:
            #     p.add_M2_drill((left_edge_x - buffer_width/2, center[1]), plated=False)
            # else:
            #     p.add_M2_drill((right_edge_x + buffer_width/2, center[1]), plated=False)
    for j in [height]:  # [-buffer_height/2, height]:
        for i in range(nx):
            if i%2 == 1:
                center = (cell_width*(i + 1) - kerf/2 - BOARD_EDGE_SPACING_EFF - M2_COURTYARD_DIAMETER/2, j)
            else:
                center = (cell_width*i + kerf/2 + BOARD_EDGE_SPACING_EFF + M2_COURTYARD_DIAMETER/2, j)
            p.add_M2_drill(center, plated=False, cut=False, etch=False)
            # if j == height:
            #     p.add_M2_drill((center[0], top_edge_y + buffer_height/2), plated=False)
    # for j in [-buffer_height*2/3 - 2*2.54, -kerf/2 - BOARD_EDGE_SPACING_EFF - M2_COURTYARD_DIAMETER/2]:
    #     for i in range(2, nx - 1, 2):
    #         center = (cell_width*i, j)
    #         p.add_M2_drill(center, plated=False)

    # Define border
    for layer in ["Edge.Cuts"]:  # , "Eco2.User"]:
        p0 = (left_edge_x, bottom_edge_y)
        p1 = (right_edge_x, bottom_edge_y)
        p2 = (right_edge_x, top_edge_y)
        p3 = (left_edge_x, top_edge_y)
        p0_extended = (p0[0] - buffer_width, p0[1])
        p1_extended = (p1[0] + buffer_width, p0[1])
        p2_extended = (p2[0] + buffer_width, top_edge_y)  # + buffer_height)
        p3_extended = (p0[0] - buffer_width, top_edge_y)  # + buffer_height)
        p.add_graphic_line([p0_extended, p1_extended], layer=layer)
        p.add_graphic_line([p1_extended, p2_extended], layer=layer)
        p.add_graphic_line([p2_extended, p3_extended], layer=layer)
        p.add_graphic_line([p3_extended, p0_extended], layer=layer)

    # for layer in ["Edge.Cuts"]:
    #     # Define cut edges
    #     y_edges = [p1[1]]
    #     y_edges.append(p1[1] + 2*buffer_height_pins/3)  # add extra cut edges
    #     y_edges.append(p1[1] + 2*buffer_height_pins/3)  # add extra cut edges
    #     # x_edges = [p0[0]]
    #     x_edges = [p0[0] - buffer_width]
    #     for j in range(1, ny, 2):
    #         y_edges.append(cell_height*j - kerf/2)
    #         y_edges.append(cell_height*j + kerf/2)
    #         y_edges.append(cell_height*j + 2*cell_height/3)  # add extra cut edges
    #         y_edges.append(cell_height*j + 2*cell_height/3)  # add extra cut edges
    #         if j < ny - 1:
    #             y_edges.append(cell_height*j + 4*cell_height/3)
    #             y_edges.append(cell_height*j + 4*cell_height/3)
    #     y_edges.append(p2[1])
    #     for i in range(0, nx + 1, 2):
    #         x_edges.append(cell_width*i - kerf/2)
    #         x_edges.append(cell_width*i + kerf/2)
    #         if i != nx:
    #             x_edges.append(cell_width*i + 2*cell_width/3)  # add extra cut edges
    #             x_edges.append(cell_width*i + 2*cell_width/3)  # duplicate cut edge to create gap
    #             x_edges.append(cell_width*i + 4*cell_width/3)
    #             x_edges.append(cell_width*i + 4*cell_width/3)
    #     x_edges.append(p2[0] + buffer_width)
    #
    #     # Add cut edges
    #     for j in range(0, len(y_edges) - 1, 2):
    #         p.add_graphic_line([(right_edge_x, max(bottom_edge_y, y_edges[j] + cutaway_gap)),
    #                             (right_edge_x, min(top_edge_y, y_edges[j + 1] - cutaway_gap))], layer=layer)
    #     # p.add_graphic_line([p2, p3], layer=layer)
    #     for i in range(0, len(x_edges) - 1, 2):
    #         p.add_graphic_line([(max(p0[0], x_edges[i] + cutaway_gap), top_edge_y),
    #                             (min(p1[0], x_edges[i + 1] - cutaway_gap), top_edge_y)], layer=layer)
    #     for j in range(0, len(y_edges) - 1, 2):
    #         p.add_graphic_line([(left_edge_x, max(bottom_edge_y, y_edges[j] + cutaway_gap)),
    #                             (left_edge_x, min(top_edge_y, y_edges[j + 1] - cutaway_gap))], layer=layer)


    return p


if __name__ == '__main__':
    now = datetime.now()
    name_clarifier = "_pcb_square_fem"
    timestamp = now.strftime("%Y%m%d_%H_%M_%S") + name_clarifier
    print(timestamp)

    width = 80.  # 200. # 50.
    height = 80.  # 200.  # 50.
    nx = 4  # 10  # 4
    ny = 4  # 10  # 4
    buffer_width = 0.  # mm, extra length on end to use as a handle
    buffer_height = 10.  # mm, extra length on end to use as a handle
    buffer_height_pins = buffer_height + 6
    trace_width = 6*MIL_TO_MM
    trace_spacing = trace_width
    pad_spacing_x = trace_width*ny + trace_spacing*(ny - 1) + 2*BOARD_EDGE_SPACING_EFF
    kerf = 3.  # mm
    gap = pad_spacing_x  # mm, for defining the straight line segments

    # Derived constants
    cell_width = width/nx
    cell_height = height/ny

    p = PCBPattern()
    p = generate_squarelv1_pattern(p, width, height, nx, ny, buffer_width, buffer_height, kerf, gap)
    x_buffer = max(kerf/2 + gap, M2_HOLE_DIAMETER/2 + BOARD_EDGE_SPACING_EFF) + buffer_width
    print(x_buffer, buffer_height)

    # kicad_filename = "C:/Users/ahadrauf/Desktop/Research/pcb_wire_testing_setup/pcb_wire_testing_setup.kicad_pcb"
    dxf_cut_filename = "C:/Users/ahadrauf/Desktop/Research/pcb_wire_testing_setup/patterns/{}_cut.dxf".format(timestamp)
    dxf_etch_filename = "C:/Users/ahadrauf/Desktop/Research/pcb_wire_testing_setup/patterns/{}_etch.dxf".format(timestamp)
    # p.generate_kicad(kicad_filename, save=True, offset_x=x_buffer, offset_y=buffer_height,
    #                  net_names=net_names, net_classes=net_classes, default_linewidth=2*LINESPACE,
    #                  default_clearance=1.5*LINESPACE, power_linewidth=2*LINESPACE, power_clearance=1.5*LINESPACE)
    p.generate_dxf(dxf_cut_filename, dxf_etch_filename, save_cut=True, save_etch=False, offset_x=x_buffer,
                   offset_y=buffer_height, include_traces_etch=False, cut_layers=("Edge.Cuts", "Eco2.User"),
                   etch_layers=("F.Cu", "Edge.Cuts", 'Eco2.User'))

