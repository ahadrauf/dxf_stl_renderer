import numpy as np

import pcb_layout
from pcb_layout import *
from pcb_layout_plus_dxf import *
from datetime import datetime


def generate_squarelv1_pattern(p: PCBPattern, width, height, nx, ny, buffer_height, kerf, gap):
    # Derived constants
    cell_width = width/nx
    cell_height = height/ny
    gap_orig = gap
    gap = 2*kerf + 2*gap

    x_buffer = max(kerf/2 + gap_orig, M2_HOLE_DIAMETER/2 + BOARD_EDGE_SPACING_EFF)
    gap_edge = max(gap, 2*kerf + 2*M2_COURTYARD_DIAMETER + 4*BOARD_EDGE_SPACING_EFF)  # gap for the edges (with seamholes)
    left_edge_x = -x_buffer
    right_edge_x = width + x_buffer
    bottom_edge_y = -buffer_height
    top_edge_y = height + x_buffer
    total_width = right_edge_x - left_edge_x
    total_height = top_edge_y - bottom_edge_y  # height + 2*buffer_height
    print("Total Width: {}, Total Height: {}".format(total_width, total_height))

    # Define horizontal cuts
    for layer in ["Edge.Cuts", "Eco2.User"]:
        for j in range(1, ny + 1):
            if j%2 == 1:
                for i in range(nx//2 + 1):
                    for k in [kerf/2, -kerf/2]:
                        start_pos = (max(left_edge_x, cell_width*(2*i - 1) + gap/2), cell_height*j + k)
                        end_pos = (min(right_edge_x, cell_width*(2*i + 1) - gap/2), cell_height*j + k)
                        p.add_graphic_line([start_pos, end_pos], layer=layer)
                    if i != 0:  # Add left arc
                        center = (max(left_edge_x, cell_width*(2*i - 1) + gap/2), cell_height*j)
                        p.add_graphic_arc(center, kerf/2, -np.pi/2, -3*np.pi/2, layer=layer)
                    if i != (nx//2):  # Add right arc
                        center = (min(right_edge_x, cell_width*(2*i + 1) - gap/2), cell_height*j)
                        p.add_graphic_arc(center, kerf/2, np.pi/2, -np.pi/2, layer=layer)
            else:
                for i in range(nx//2):
                    gap_eff = gap_edge if (j == ny) else gap
                    for k in [kerf/2, -kerf/2]:
                        start_pos = (cell_width*(2*i) + gap_eff/2, cell_height*j + k)
                        end_pos = (cell_width*(2*i + 2) - gap_eff/2, cell_height*j + k)
                        p.add_graphic_line([start_pos, end_pos], layer=layer)
                    if True:  # Add left arc
                        center = (cell_width*(2*i) + gap_eff/2, cell_height*j)
                        p.add_graphic_arc(center, kerf/2, -np.pi/2, -3*np.pi/2, layer=layer)
                    if i != (nx//2):  # Add right arc
                        center = (cell_width*(2*i + 2) - gap_eff/2, cell_height*j)
                        p.add_graphic_arc(center, kerf/2, np.pi/2, -np.pi/2, layer=layer)

        # Define vertical cuts
        for i in range(0, nx + 1):
            if i%2 == 0:
                gap_eff = gap_edge if (i == 0 or i == nx) else gap
                for j in range(ny//2 + 1):
                    for k in [kerf/2, -kerf/2]:
                        start_pos = (cell_width*i + k, max(0., cell_height*(2*j - 1) + gap_eff/2))
                        end_pos = (cell_width*i + k, min(top_edge_y, cell_height*(2*j + 1) - gap_eff/2))
                        p.add_graphic_line([start_pos, end_pos], layer=layer)
                    if True:  # Add bottom arc
                        center = (cell_width*i, max(0., cell_height*(2*j - 1) + gap_eff/2))
                        p.add_graphic_arc(center, kerf/2, -np.pi, 0, layer=layer)
                    if j != (ny//2):  # Add top arc
                        center = (cell_width*i, min(top_edge_y, cell_height*(2*j + 1) - gap_eff/2))
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
        for j in range(ny):
            if j%2 == 0:
                center = (i, cell_height*(j + 1) - kerf/2 - BOARD_EDGE_SPACING_EFF - M2_COURTYARD_DIAMETER/2)
            else:
                center = (i, cell_height*j + kerf/2 + BOARD_EDGE_SPACING_EFF + M2_COURTYARD_DIAMETER/2)
            p.add_M2_drill(center, plated=False)
    for i in range(nx):
        if i%2 == 1:
            center = (cell_width*(i + 1) - kerf/2 - BOARD_EDGE_SPACING_EFF - M2_COURTYARD_DIAMETER/2, height)
        else:
            center = (cell_width*i + kerf/2 + BOARD_EDGE_SPACING_EFF + M2_COURTYARD_DIAMETER/2, height)
        p.add_M2_drill(center, plated=False)

    # Define border
    for layer in ["Edge.Cuts", "Eco2.User"]:
        p0 = (left_edge_x, bottom_edge_y)
        p1 = (right_edge_x, bottom_edge_y)
        p2 = (right_edge_x, top_edge_y)
        p3 = (left_edge_x, top_edge_y)
        p.add_graphic_line([p0, p1], layer=layer)

        #Define cut edges
        y_edges = [p1[1]]
        x_edges = [p0[0]]
        for j in range(1, ny, 2):
            y_edges.append(cell_height*j - kerf/2)
            y_edges.append(cell_height*j + kerf/2)
        y_edges.append(p2[1])
        for i in range(0, nx, 2):
            x_edges.append(cell_width*i - kerf/2)
            x_edges.append(cell_width*i + kerf/2)
        x_edges.append(p2[0])

        # Add cut edges
        for j in range(0, len(y_edges) - 1, 2):
            p.add_graphic_line([(right_edge_x, y_edges[j]), (right_edge_x, y_edges[j + 1])], layer=layer)
        # p.add_graphic_line([p2, p3], layer=layer)
        for i in range(0, len(y_edges) - 1, 2):
            p.add_graphic_line([(x_edges[i], top_edge_y), (x_edges[i + 1], top_edge_y)], layer=layer)
        for j in range(0, len(y_edges) - 1, 2):
            p.add_graphic_line([(left_edge_x, y_edges[j]), (left_edge_x, y_edges[j + 1])], layer=layer)

    return p


def generate_square_wiring(p: PCBPattern, width, height, nx, ny, buffer_height, kerf, gap):
    assert (nx%2 == 0)
    assert (ny%2 == 0)
    # Derived constants
    cell_width = width/nx
    cell_height = height/ny

    trace_width = LINESPACE
    trace_spacing = 2*LINESPACE
    pad_spacing_x = trace_width*(ny//2) + trace_spacing*(ny//2 - 1) + 2*BOARD_EDGE_SPACING_EFF
    pad_spacing_y = pad_spacing_x  # 2*LINESPACE*(ny//2 - 1) + 2*BOARD_EDGE_SPACING_EFF
    pad_width = cell_width - kerf - 2*pad_spacing_x
    pad_height = cell_height - kerf - 2*pad_spacing_y
    pad_corner_radius = cell_width/10.
    N_corner = 10
    trace_radius = pad_corner_radius  # min(pad_corner_radius, kerf)/2
    via_offset = pad_corner_radius + 0.1
    mask_inset = 0.1

    print("Pad Width: {}, Pad Height: {}".format(pad_width, pad_height))

    # Add auxetic pads
    for layer in ["F", "B"]:
        for i in range(nx):
            for j in range(ny):
                x = cell_width*i + kerf/2 + pad_spacing_x
                y = cell_height*j + kerf/2 + pad_spacing_y
                p.add_fill_zone_rounded_rectangle((x, y), (x + pad_width, y + pad_height), pad_corner_radius, N_corner,
                                                  layer=layer + ".Cu")
                p.add_fill_zone_rounded_rectangle((x + mask_inset, y + mask_inset),
                                                  (x + pad_width - mask_inset, y + pad_height - mask_inset),
                                                  pad_corner_radius, N_corner, layer=layer + ".Mask")

    # Add pin headers
    pin_nx, pin_ny = 5, 2
    pin_spacing = 2.54
    for i in range(nx):
        pin_header_width = (pin_nx - 1)*pin_spacing + pcb_layout.PIN_HEADER_DIAMETER
        pin_header_height = (pin_ny - 1)*pin_spacing + pcb_layout.PIN_HEADER_DIAMETER
        bottom_left_pt = (cell_width*(i + 1/2) + kerf/2 - pin_header_width/2, -buffer_height/2 + pin_header_height/2)
        p.add_pin_header(bottom_left_pt, pin_nx, pin_ny, spacing=pin_spacing, net_names=["1 main"]*pin_nx*pin_ny)

    def pin_header_loc(i, n):  # Location of pin header in column i with pin #n (0 closer to pads and farthest left)
        bottom_left_pt = (cell_width*(i + 1/2) + kerf/2 - pin_header_width/2, -buffer_height/2 + pin_header_height/2)
        dx = pin_spacing*(n%pin_nx)
        dy = pin_spacing*(n//pin_nx)
        return (bottom_left_pt[0] + dx, bottom_left_pt[1] - dy)  # flip dx and dy so pins 0-(n-1) are closest to pads

    ############################################################################################################
    # Add wires
    ############################################################################################################
    for i in range(nx):
        # Add first wire (just a straight line to the pad)
        pin_loc = pin_header_loc(i, 0)
        p.add_trace([pin_loc, (pin_loc[0], kerf/2 + pad_spacing_y + 0.1)], trace_width)

        # Add rest of wires (note that the wires flip-flop right/left sides based on i%2
        for n in range(1, ny):
            # Choose layer for wires
            if n < ny//2:
                layer = "F.Cu"
            else:
                layer = "B.Cu"

            n_rel = n % (ny//2) + 1
            if (n%2 == 1 and i%2 == 0) or (n%2 == 0 and i%2 == 1):
                x_offset = trace_width*(n_rel//2 + 1/2) + trace_spacing*(n_rel//2)
                # x_offset_flipped = trace_width*(ny//2 - n_rel//2 - 1/2) + trace_spacing*(ny//2 - n_rel//2)
                x_offset_flipped = pad_spacing_x - BOARD_EDGE_SPACING_EFF - x_offset
            else:
                # x_offset = trace_width*(ny//2 - n_rel//2 - 1/2) + trace_spacing*(ny//2 - n_rel//2)
                x_offset_flipped = trace_width*(n_rel//2 + 1/2) + trace_spacing*(n_rel//2)
                x_offset = pad_spacing_x - BOARD_EDGE_SPACING_EFF - x_offset_flipped
            right_x = cell_width*i + kerf/2 + pad_spacing_x + pad_width + BOARD_EDGE_SPACING_EFF + x_offset
            left_x = cell_width*i + kerf/2 + x_offset
            pin_loc = pin_header_loc(i, n)
            start_trace_radius = trace_radius/5
            if n < ny//2:
                if n%2 == 1:
                    y_start1 = -2*x_offset
                    y_start = -2*x_offset - start_trace_radius
                    pts = [pin_loc, (pin_loc[0], y_start1), (right_x, y_start)] if i%2 == 0 else \
                        [pin_loc, (pin_loc[0], y_start1), (left_x, y_start)]
                else:
                    y_start1 = -buffer_height/2 + PIN_HEADER_DIAMETER/2 + 2*x_offset
                    y_start = -2*x_offset - start_trace_radius
                    pts = [pin_loc, (pin_loc[0], y_start1), (right_x, y_start)] if i%2 == 0 else \
                        [pin_loc, (pin_loc[0], y_start1), (left_x, y_start)]
            else:
                y_start = -buffer_height/2 - pin_spacing/2 - PIN_HEADER_DIAMETER - 2*x_offset
                pts = [pin_loc, (pin_loc[0], y_start), (right_x, y_start)] if i%2 == 0 else \
                    [pin_loc, (pin_loc[0], y_start), (left_x, y_start)]
            p.add_trace_rounded(pts, trace_width, start_trace_radius/5, N_corner, layer=layer)
            pts = [pts[-1]]
            for j in range(1, n + 1):
                if j == n:
                    y = cell_height*j + kerf/2 + pad_spacing_y
                    if (j%2 == 1 and i%2 == 0) or (j%2 == 0 and i%2 == 1):
                        right_x2 = cell_width*i + kerf/2 + pad_spacing_x + pad_width - pad_corner_radius
                        pts += [(right_x, y), (right_x2, y + pad_corner_radius)]
                    else:
                        left_x2 = cell_width*i + kerf/2 + pad_corner_radius
                        pts += [(left_x, y), (left_x2, y + pad_corner_radius)]
                else:
                    if (j%2 == 1 and i%2 == 0) or (j%2 == 0 and i%2 == 1):
                        y = cell_height*j + kerf/2 + pad_spacing_y + pad_height + BOARD_EDGE_SPACING_EFF + x_offset
                        pts += [(right_x, y), (left_x, y)]
                    else:
                        y = cell_height*j + kerf/2 + pad_spacing_y + pad_height + x_offset_flipped
                        # y = cell_height*j + kerf/2 + pad_spacing_y + pad_height + BOARD_EDGE_SPACING_EFF + x_offset_flipped
                        pts += [(left_x, y), (right_x, y)]

            # if n >= (ny//2):
            #     print(n, n_rel, x_offset, x_offset_flipped, right_x, left_x)
            p.add_trace_rounded(pts, trace_width, trace_radius, N_corner, layer=layer)

            # Add vias (note that the vias flip-flop right/left sides based on i%2
            # The first via will be on the same side as the second via (cause my routing is weird)
            j = 0
            x = cell_width*i + kerf/2 + pad_spacing_x + pad_corner_radius
            y = cell_height*j + kerf/2 + pad_spacing_y + pad_corner_radius
            p.add_via((x, y))
            for j in range(1, n+1):
                if (j%2 == 1 and i%2 == 0) or (j%2 == 0 and i%2 == 1):
                    x = cell_width*i + kerf/2 + pad_spacing_x + via_offset
                    y = cell_height*j + kerf/2 + pad_spacing_y + via_offset
                else:
                    x = cell_width*i + kerf/2 + pad_spacing_x + pad_width - via_offset
                    y = cell_height*j + kerf/2 + pad_spacing_y + via_offset
                p.add_via((x, y))

    return p


if __name__ == '__main__':
    width = 200.
    height = 200.
    nx = 10
    ny = 10
    buffer_height = 10.  # mm, extra length on end to use as a handle
    kerf = 3.  # mm
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
    p = generate_square_wiring(p, width, height, nx, ny, buffer_height, kerf, gap)
    # pyperclip.copy(out)
    x_buffer = max(kerf/2 + gap, M2_HOLE_DIAMETER/2 + BOARD_EDGE_SPACING_EFF)

    kicad_filename = "C:/Users/ahadrauf/Desktop/Research/pcb_wire_testing_setup/pcb_wire_testing_setup.kicad_pcb"
    dxf_cut_filename = "C:/Users/ahadrauf/Desktop/Research/pcb_wire_testing_setup/pcb_wire_testing_setup_cut.dxf"
    dxf_etch_filename = "C:/Users/ahadrauf/Desktop/Research/pcb_wire_testing_setup/pcb_wire_testing_setup_etch.dxf"
    p.generate_kicad(kicad_filename, save=True, offset_x=x_buffer, offset_y=buffer_height)
    p.generate_dxf(dxf_cut_filename, dxf_etch_filename, save=True, offset_x=x_buffer, offset_y=buffer_height)
    # with open(filename, 'w') as f:
    #     f.write(out)
