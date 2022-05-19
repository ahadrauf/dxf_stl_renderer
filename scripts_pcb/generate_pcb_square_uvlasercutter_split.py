"""
Generates a nxm grid of auxetic squares and their wiring
Requires that you change the auxetic square sizes, n, and m in the main() function at the bottom as well as the
    pin_nx and pin_ny variables in the wiring function
"""

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
    buffer_height_pins = buffer_height  # buffer_height + 6
    left_edge_x = -x_buffer
    right_edge_x = width + x_buffer
    bottom_edge_y = -x_buffer - buffer_height_pins
    top_edge_y = height + x_buffer

    total_width = right_edge_x - left_edge_x + 2*buffer_width
    total_height = top_edge_y - bottom_edge_y + buffer_height  # height + 2*buffer_height
    print("Total Width: {}, Total Height: {}".format(total_width, total_height))

    # Define horizontal cuts
    for layer in ["Edge.Cuts"]:  # , "Eco2.User"]:
    # for layer in ["F.SilkS"]:
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
                        if j == (ny // 2):
                            end_pos = (cell_width*i + k, top_edge_y)
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
    #     p.add_graphic_line([p1_extended, p2_extended], layer=layer)
    #     p.add_graphic_line([p2_extended, p3_extended], layer=layer)
    #     p.add_graphic_line([p3_extended, p0_extended], layer=layer)

    for layer in ["Edge.Cuts"]:
        # Define cut edges
        y_edges = [p1[1]]
        y_edges.append(p1[1] + 2*buffer_height_pins/3)  # add extra cut edges
        y_edges.append(p1[1] + 2*buffer_height_pins/3)  # add extra cut edges
        # x_edges = [p0[0]]
        x_edges = [p0[0] - buffer_width]
        for j in range(1, ny, 2):
            y_edges.append(cell_height*j - kerf/2)
            y_edges.append(cell_height*j + kerf/2)
            y_edges.append(cell_height*j + 2*cell_height/3)  # add extra cut edges
            y_edges.append(cell_height*j + 2*cell_height/3)  # add extra cut edges
            if j < ny - 1:
                y_edges.append(cell_height*j + 4*cell_height/3)
                y_edges.append(cell_height*j + 4*cell_height/3)
        y_edges.append(p2[1])
        for i in range(0, nx + 1, 2):
            x_edges.append(cell_width*i - kerf/2)
            x_edges.append(cell_width*i + kerf/2)
            if i != nx:
                x_edges.append(cell_width*i + 2*cell_width/3)  # add extra cut edges
                x_edges.append(cell_width*i + 2*cell_width/3)  # duplicate cut edge to create gap
                x_edges.append(cell_width*i + 4*cell_width/3)
                x_edges.append(cell_width*i + 4*cell_width/3)
        x_edges.append(p2[0] + buffer_width)

        # Add cut edges
        for j in range(0, len(y_edges) - 1, 2):
            p.add_graphic_line([(right_edge_x, max(bottom_edge_y, y_edges[j] + cutaway_gap)),
                                (right_edge_x, min(top_edge_y, y_edges[j + 1] - cutaway_gap))], layer=layer)
        # p.add_graphic_line([p2, p3], layer=layer)
        for i in range(0, len(x_edges) - 1, 2):
            p.add_graphic_line([(max(p0[0], x_edges[i] + cutaway_gap), top_edge_y),
                                (min(p1[0], x_edges[i + 1] - cutaway_gap), top_edge_y)], layer=layer)
        for j in range(0, len(y_edges) - 1, 2):
            p.add_graphic_line([(left_edge_x, max(bottom_edge_y, y_edges[j] + cutaway_gap)),
                                (left_edge_x, min(top_edge_y, y_edges[j + 1] - cutaway_gap))], layer=layer)

    return p


def generate_square_wiring(p: PCBPattern, width, height, nx, ny, buffer_height, kerf, gap):
    assert (nx%2 == 0)
    assert (ny%2 == 0)
    # Derived constants
    cell_width = width/nx
    cell_height = height/ny

    trace_width = 2*LINESPACE
    trace_spacing = 2*LINESPACE
    pad_spacing_x = trace_width*ny + trace_spacing*(ny - 1) + 2*BOARD_EDGE_SPACING_EFF
    pad_spacing_y = pad_spacing_x  # 2*LINESPACE*(ny//2 - 1) + 2*BOARD_EDGE_SPACING_EFF
    pad_width = cell_width - kerf - 2*pad_spacing_x
    pad_height = cell_height - kerf - 2*pad_spacing_y
    pad_corner_radius = cell_width/20.
    N_corner = 10
    trace_radius = pad_corner_radius  # min(pad_corner_radius, kerf)/2
    via_offset = cell_width/10. + 0.1
    mask_inset = 0.1

    net_names, net_classes, net_strings = generate_nets(nx, ny)

    print("Pad Width: {}, Pad Height: {}".format(pad_width, pad_height))

    ############################################################################################################
    # Add auxetic pads
    ############################################################################################################
    for layer in ["F", "B"]:
        for i in range(nx):
            for j in range(ny):
                if j == 0:
                    dx_left = pad_spacing_x/2 if i%2 == 0 else pad_spacing_x
                    dx_right = pad_spacing_x if i%2 == 0 else 3/2*pad_spacing_x
                    dy_bottom = pad_spacing_y/2
                    dy_top = 3/2*pad_spacing_y
                else:
                    dx_left = pad_spacing_x/2 if (i + j)%2 == 1 else pad_spacing_x
                    dx_right = pad_spacing_x if (i + j)%2 == 1 else 3/2*pad_spacing_x
                    dy_bottom = pad_spacing_y/2
                    dy_top = pad_spacing_y
                # dx_left, dx_right = pad_spacing_x, pad_spacing_x
                # dy_bottom, dy_top = pad_spacing_y, pad_spacing_y
                x = cell_width*i + kerf/2 + dx_left
                y = cell_height*j + kerf/2 + dy_bottom
                x_right = cell_width*i + kerf/2 + pad_width + dx_right
                y_top = cell_height*j + kerf/2 + pad_height + dy_top
                p.add_fill_zone_rounded_rectangle((x, y), (x_right, y_top), pad_corner_radius,
                                                  net=net_strings["/OUT_" + str(i + 1) + str(j + 1)], n=N_corner,
                                                  layer=layer + ".Cu")
                p.add_fill_zone_rounded_rectangle((x + mask_inset, y + mask_inset),
                                                  (x_right - mask_inset, y_top - mask_inset),
                                                  pad_corner_radius, net=net_strings["/OUT_" + str(i + 1) + str(j + 1)],
                                                  n=N_corner, layer=layer + ".Mask")

    ############################################################################################################
    # Add pin headers
    ############################################################################################################
    # pin_nx, pin_ny = 4, 1
    pin_nx, pin_ny = 5, 2
    pin_spacing = 2.54
    for i in range(nx):
        pin_header_width = (pin_nx - 1)*pin_spacing
        pin_header_height = (pin_ny - 1)*pin_spacing + pcb_layout.PIN_HEADER_DIAMETER
        # bottom_left_pt = (cell_width*(i + 1/2) + kerf/2 - pin_header_width/2 - pin_spacing/2,
        #                   -buffer_height/2 + pin_header_height/2)
        if i%2 == 0:
            bottom_left_pt = (cell_width*(i + 1) - pin_header_width - pin_spacing/2,
                              -buffer_height*2/3 + pin_header_height/2)
        else:
            bottom_left_pt = (cell_width*i + pin_spacing/2,
                              -buffer_height*2/3 + pin_header_height/2)

        out_nets = [net_strings["/OUT_" + str(i + 1) + str(j + 1)] for j in range(ny)]
        shuffle = lambda arr, new_idx: [arr[i] for i in new_idx]
        if i%2 == 0:
            # out_nets = shuffle(out_nets, [0, 9, 1, 8, 2, 7, 3, 6, 4, 5])
            new_idx = []
            for i in range(ny//2):
                new_idx += [i]
                new_idx += [ny - 1 - i]
            out_nets = shuffle(out_nets, new_idx)
        else:
            # out_nets = shuffle(out_nets, [4, 5, 3, 6, 2, 7, 1, 8, 0, 9])
            new_idx = []
            for i in reversed(range(ny//2)):
                new_idx += [i]
                new_idx += [ny - 1 - i]
            out_nets = shuffle(out_nets, new_idx)
        p.add_pin_header(bottom_left_pt, pin_nx, pin_ny, spacing=pin_spacing, net_names=out_nets, cut=False, etch=False)

    def pin_header_loc(i, n):  # Location of pin header in column i with pin #n (0 closer to pads and farthest left)
        # bottom_left_pt = (cell_width*(i + 1/2) + kerf/2 - pin_header_width/2 - pin_spacing/2,
        #                   -buffer_height/2 + pin_header_height/2)
        if i%2 == 0:
            bottom_left_pt = (cell_width*(i + 1) - pin_header_width - pin_spacing/2,
                              -buffer_height*2/3 + pin_header_height/2)
            dx = pin_spacing*n if n < pin_nx//2 else pin_spacing*(pin_nx - 1 - n%(pin_nx//2))
            x = bottom_left_pt[0] + dx
        else:
            bottom_left_pt = (cell_width*i + pin_spacing/2 + pin_spacing*(pin_nx - 1),
                              -buffer_height*2/3 + pin_header_height/2)
            dx = pin_spacing*n if n < pin_nx//2 else pin_spacing*(pin_nx - 1 - n%(pin_nx//2))
            x = bottom_left_pt[0] - dx
        # dx = pin_spacing*(n%pin_nx)  # this works for the 2-layer pin routing, not for 1-layer (ny = 1)
        dy = pin_spacing*(n//pin_nx)
        return (x, bottom_left_pt[1] - dy)  # flip dx and dy so pins 0-(n-1) are closest to pads

    ############################################################################################################
    # Add wires
    ############################################################################################################
    for i in range(nx):
        # Add first wire (just a straight line to the pad)
        pin_loc = pin_header_loc(i, 0)
        p.add_trace([pin_loc, (pin_loc[0], kerf/2 + pad_spacing_y/2 + 0.1)], trace_width,
                    net=net_strings["/OUT_" + str(i + 1) + str(1)], layer="F.Cu", etch=False)
        pts = Pattern.offset_trace([pin_loc, (pin_loc[0], kerf/2 + pad_spacing_y/2 + 0.1)], w=trace_width)
        p.add_fill_zone_polygon(pts, net=net_strings["/OUT_" + str(i + 1) + str(1)], layer="F.Cu", etch=True)

        # add fill region
        j = 0
        y_top = cell_height*j + kerf/2 + pad_spacing_y/2
        p0, p1, p2 = (pin_loc[0] - pad_corner_radius, y_top), (pin_loc[0], y_top), (pin_loc[0], y_top - pad_spacing_y)
        bezier_pts1 = Pattern.quadratic_bezier_curve(p0, p1, p2, N_corner + 2)
        p0, p1, p2 = (pin_loc[0] + pad_corner_radius, y_top), (pin_loc[0], y_top), (pin_loc[0], y_top - pad_spacing_y)
        bezier_pts2 = Pattern.quadratic_bezier_curve(p2, p1, p0, N_corner + 2)
        fill_pts = bezier_pts1 + bezier_pts2[1:]
        fill_pts += [(fill_pts[-1][0], fill_pts[-1][1] + 1), (fill_pts[0][0], fill_pts[0][1] + 1)]
        # p.add_fill_zone_polygon(pts=fill_pts, net=net_strings["/OUT_" + str(i + 1) + str(1)])

        # Add rest of wires (note that the wires flip-flop right/left sides based on i%2
        # [0, ny//2 - 1) = F.Cu
        # [ny//2, ny) = B.Cu
        # if ny//2 is odd, the leftmost B.Cu wire will be the first to reach its auxetic pad --> continue without
        #   skipping ny//2 - 1
        # if ny//2 is even, the rightmost B.Cu wire will be the first to reach its auxetic pad --> skip ny//2 - 1
        #   so the first B.Cu trace will be on the right

        for n in range(ny - 1):
            # Choose layer for wires
            layer = "F.Cu"

            if (n%2 == 0 and i%2 == 0) or (n%2 == 1 and i%2 == 1):
                x_offset = BOARD_EDGE_SPACING_EFF + trace_width*(n//2 + 1/2) + trace_spacing*(n//2)
                x_offset_flipped = pad_spacing_x - x_offset
            else:
                x_offset_flipped = BOARD_EDGE_SPACING_EFF + trace_width*(n//2 + 1/2) + trace_spacing*(
                        n//2)
                x_offset = pad_spacing_x - x_offset_flipped
            right_x = cell_width*i + kerf/2 + pad_spacing_x + pad_width + x_offset
            left_x = cell_width*i + kerf/2 + x_offset
            curr_net = net_strings["/OUT_" + str(i + 1) + str(n + 1)]

            # print(i, n, BOARD_EDGE_SPACING_EFF, trace_width, trace_spacing, x_offset, x_offset_flipped, left_x, right_x)
            pin_loc = pin_header_loc(i, n + 1)
            pts = [pin_loc]
            pts += [(right_x, 0)] if (i%2 == 0) else [(left_x, 0)]
            for j in range(1, n + 2):
                if j == n + 1:
                    y = cell_height*j + kerf/2 + pad_spacing_y
                    if (j%2 == 1 and i%2 == 0) or (j%2 == 0 and i%2 == 1):
                        right_x2 = cell_width*i + kerf/2 + pad_spacing_x + pad_width - pad_corner_radius
                        pts += [(right_x, y), (right_x2, y + pad_corner_radius)]

                        # add fill region
                        x_right = cell_width*i + kerf/2 + pad_spacing_x + pad_width
                        y_top = cell_height*j + kerf/2 + pad_spacing_y/2
                        p0, p1, p2 = (right_x2, y_top), (right_x, y_top), (right_x, y - pad_spacing_y)
                        bezier_pts1 = Pattern.quadratic_bezier_curve(p0, p1, p2, N_corner + 2)
                        p0, p1, p2 = (x_right, y + pad_corner_radius), (right_x, y + pad_corner_radius), \
                                     (right_x, y - pad_spacing_y)
                        bezier_pts2 = Pattern.quadratic_bezier_curve(p2, p1, p0, N_corner + 2)
                        fill_pts = bezier_pts1 + bezier_pts2[1:N_corner//2] + [(x_right, y + 3*pad_corner_radius)]
                        p.add_fill_zone_polygon(pts=fill_pts, net=curr_net, layer=layer)
                    else:
                        left_x2 = cell_width*i + kerf/2 + pad_spacing_x + pad_corner_radius
                        pts += [(left_x, y), (left_x2, y + pad_corner_radius)]

                        # add fill region
                        x_left = cell_width*i + kerf/2 + pad_spacing_x
                        y_top = cell_height*j + kerf/2 + pad_spacing_y/2
                        p0, p1, p2 = (left_x2, y_top), (left_x, y_top), (left_x, y - pad_spacing_y)
                        bezier_pts1 = Pattern.quadratic_bezier_curve(p0, p1, p2, N_corner + 2)
                        p0, p1, p2 = (x_left, y + pad_corner_radius), (left_x, y + pad_corner_radius), \
                                     (left_x, y - pad_spacing_y)
                        bezier_pts2 = Pattern.quadratic_bezier_curve(p2, p1, p0, N_corner + 2)
                        fill_pts = bezier_pts1 + bezier_pts2[1:N_corner//2] + [(x_left, y + 3*pad_corner_radius)]
                        p.add_fill_zone_polygon(pts=fill_pts, net=curr_net, layer=layer)
                else:
                    if (j%2 == 1 and i%2 == 0) or (j%2 == 0 and i%2 == 1):
                        y = cell_height*j + kerf/2 + pad_spacing_y + pad_height + x_offset
                        pts += [(right_x, y), (left_x, y)]
                    else:
                        y = cell_height*j + kerf/2 + pad_spacing_y + pad_height + x_offset_flipped
                        pts += [(left_x, y), (right_x, y)]

            # if n >= (ny//2):
            #     print(n, n_rel, x_offset, x_offset_flipped, right_x, left_x)
            p.add_trace_rounded(pts, trace_width, trace_radius, N_corner, net=curr_net, layer=layer, etch=False)
            pts = Pattern.generate_rounded_curve(pts, trace_radius, N_corner)
            pts = Pattern.offset_trace(pts, w=trace_width)
            p.add_fill_zone_polygon(pts, net=curr_net, layer=layer, etch=True)

        # Add vias (note that the vias flip-flop right/left sides based on i%2
        # The first via will be on the same side as the second via (cause my routing is weird)
        j = 0
        x = cell_width*i + kerf/2 + pad_spacing_x + pad_corner_radius
        y = cell_height*j + kerf/2 + pad_spacing_y + pad_corner_radius
        p.add_via((x, y), net=net_strings["/OUT_" + str(i + 1) + str(j + 1)], cut=False)
        for j in range(1, ny):
            if (j%2 == 1 and i%2 == 0) or (j%2 == 0 and i%2 == 1):
                x = cell_width*i + kerf/2 + pad_spacing_x + via_offset
                y = cell_height*j + kerf/2 + pad_spacing_y + via_offset
            else:
                x = cell_width*i + kerf/2 + pad_spacing_x + pad_width - via_offset
                y = cell_height*j + kerf/2 + pad_spacing_y + via_offset

            p.add_via((x, y), net=net_strings["/OUT_" + str(i + 1) + str(j + 1)], cut=False)

    return p


def generate_nets(nx, ny):
    net_names = []
    net_classes = []

    # Add control wires for all the transistors
    for i in range(nx*ny):
        net_names += ["/OUT_" + str(i//ny + 1) + str(i%ny + 1)]
        net_classes += [1]

    # Add a random net for miscellaneous test connections
    net_names += ["Test"]
    net_classes += [1]

    net_strings = {net: str(i + 1) + " " + net for i, net in enumerate(net_names)}
    return net_names, net_classes, net_strings


if __name__ == '__main__':
    width = 200.  # 200. # 50.
    height = 200.  # 200.  # 50.
    nx = 10  # 10  # 4
    ny = 10  # 10  # 4
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

    now = datetime.now()
    name_clarifier = "_square_pattern_nx={:d}xny={:d}_wx={:.2f}xwy={:.2f}_kerf={:.2f}_gap={:.2f}".format(
        nx, ny, cell_width, cell_height, kerf, gap
    )
    timestamp = now.strftime("%Y%m%d_%H_%M_%S") + name_clarifier
    print(timestamp)

    net_names, net_classes, net_strings = generate_nets(nx, ny)
    p = PCBPattern()
    p = generate_squarelv1_pattern(p, width, height, nx, ny, buffer_width, buffer_height, kerf, gap)
    p = generate_square_wiring(p, width, height, nx, ny, buffer_height_pins, kerf, gap)
    x_buffer = max(kerf/2 + gap, M2_HOLE_DIAMETER/2 + BOARD_EDGE_SPACING_EFF) + buffer_width
    print(x_buffer, buffer_height)

    now = datetime.now()
    name_clarifier = "_pcb_square_uvlasercutter"
    timestamp = now.strftime("%Y%m%d_%H_%M_%S") + name_clarifier
    # kicad_filename = "C:/Users/ahadrauf/Desktop/Research/pcb_wire_testing_setup/pcb_wire_testing_setup.kicad_pcb"
    dxf_cut_filename = "C:/Users/ahadrauf/Desktop/Research/pcb_wire_testing_setup/patterns/{}_cut.dxf".format(timestamp)
    dxf_etch_filename = "C:/Users/ahadrauf/Desktop/Research/pcb_wire_testing_setup/patterns/{}_etch.dxf".format(timestamp)
    # p.generate_kicad(kicad_filename, save=True, offset_x=x_buffer, offset_y=buffer_height,
    #                  net_names=net_names, net_classes=net_classes, default_linewidth=2*LINESPACE,
    #                  default_clearance=1.5*LINESPACE, power_linewidth=2*LINESPACE, power_clearance=1.5*LINESPACE)
    p.generate_dxf(dxf_cut_filename, dxf_etch_filename, save_cut=True, save_etch=True, offset_x=x_buffer, offset_y=buffer_height,
                   include_traces_etch=True, cut_layers=("Edge.Cuts", "Eco2.User"), etch_layers=("F.Cu", "Edge.Cuts", 'Eco2.User'))

    # with open(filename, 'w') as f:
    #     f.write(out)
