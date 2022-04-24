import numpy as np
from pcb_layout import *
from pcb_layout_plus_dxf import *
from datetime import datetime


def generate_test_pcb(p: PCBPattern):
    N_range = np.array([1, 3, 5])
    w_range = np.array([3., 6., 9.])*MIL_TO_MM
    kerf = 3
    gaps = np.array([LINESPACE, 2*LINESPACE, LINESPACE])
    kerf_board_edge_range = np.array([9*MIL_TO_MM,
                                      10*MIL_TO_MM,
                                      12*MIL_TO_MM])
    kerf_board_edge_default = BOARD_EDGE_SPACING_EFF
    N_corner = 10
    text_scale = 0.45
    nx, ny = 3, 4

    l_nom = kerf + 2*BOARD_EDGE_SPACING_EFF
    m2_drill_diameter = 2.45
    m2_offset = 1.65*max(m2_drill_diameter/2, kerf/2)
    w_bondpad = 8.
    h_bondpad = 8.
    w_buffer = 4.5
    h_buffer = 5.5 + 2*m2_offset
    outside_buffer = 2.5
    panel_spacing = 0.3
    boundary_gap = 2.5
    via_radius = 0.4
    linestart = '  '
    total_width = len(N_range)*w_bondpad + (len(N_range) - 1)*w_buffer
    total_height = ny*(2*h_bondpad + l_nom) + (ny - 1)*h_buffer + m2_offset*2
    text_width = 6.75*text_scale  # 4.064  # measured in KiCad
    text_height = 0.508*text_scale  # measured in KiCad

    print("Total Width", nx*total_width + nx*outside_buffer + (nx - 1)*w_buffer)
    print("Total Height", total_height + 2*outside_buffer)

    gap = gaps[1]
    kerf = 3
    w = w_range[1]
    N = N_range[1]
    adhesive = False
    backside_copper = False
    inset_soldermask = True
    normal_last_beam = True
    kerf_board_edge = kerf_board_edge_default  # = kerf_board_edge_range[w_idx]

    soldermask_buffer = 5*MIL_TO_MM if inset_soldermask else 0

    r_corner = gap/2
    l = kerf + 2*kerf_board_edge
    x_offset = 0
    cut_radius = (l - 2*kerf_board_edge)/2  # 1.5*l/5

    ##############################################################################################
    # Add main copper pads
    ##############################################################################################
    x = x_offset
    y = 0
    net = "1 main"
    if backside_copper:
        layers = ["F.Cu", "B.Cu"]
    else:
        layers = ["F.Cu"]
    for layer in layers:
        p.add_fill_zone_rectangle((x, y), (x + w_bondpad, y + h_bondpad), layer=layer, net=net)
        p.add_fill_zone_rectangle((x, y + h_bondpad + l), (x + w_bondpad, y + l + 2*h_bondpad), layer=layer, net=net)
    p.add_fill_zone_rectangle((x + soldermask_buffer, y + soldermask_buffer),
                              (x + w_bondpad - soldermask_buffer, y + h_bondpad - soldermask_buffer),
                              layer="F.Mask", net=net)
    p.add_fill_zone_rectangle((x + soldermask_buffer, y + h_bondpad + l + soldermask_buffer),
                              (x + w_bondpad - soldermask_buffer, y + l + 2*h_bondpad - soldermask_buffer),
                              layer="F.Mask", net=net)

    ##############################################################################################
    # Add wires
    ##############################################################################################
    for n in range(N):
        topleft = (x + (gap + w)*n, y + h_bondpad)
        bottomright = (x + (gap + w)*n + w, y + h_bondpad + l)
        print(topleft, bottomright, gap, w)
        # Add wire
        for layer in layers:
            p.add_fill_zone_rectangle((topleft[0], topleft[1]), (bottomright[0], bottomright[1]),
                                      layer=layer, net="0 main")

        # Added rounded corners
        for layer in layers:
            corner_radius = cut_radius if (n == N - 1 and not normal_last_beam) else r_corner
            # Bottomright shows up as the top in eDrawingsPro (angles show up in the orientation you'd normally think, though)
            # Right corners
            p.add_graphic_arc(center=(bottomright[0] + corner_radius, bottomright[1] - corner_radius),
                              radius=corner_radius, start_angle=np.pi, end_angle=np.pi/2, layer=layer, etch=True)
            p.add_graphic_arc(center=(bottomright[0] + corner_radius, topleft[1] + corner_radius),
                              radius=corner_radius, start_angle=np.pi, end_angle=3*np.pi/2, layer=layer, etch=True)
            if n != 0:  # Left corners
                p.add_graphic_arc(center=(topleft[0] - corner_radius, bottomright[1] - corner_radius),
                                  radius=corner_radius, start_angle=np.pi/2, end_angle=0, layer=layer, etch=True)
                p.add_graphic_arc(center=(topleft[0] - corner_radius, topleft[1] + corner_radius),
                                  radius=corner_radius, start_angle=3*np.pi/2, end_angle=2*np.pi, layer=layer, etch=True)
            # p.add_graphic_arc(center=(bottomright[0] + corner_radius, bottomright[1] - corner_radius),
            #                   radius=corner_radius, start_angle=np.pi, end_angle=3*np.pi/2, layer=layer, etch=True)
            # p.add_graphic_arc(center=(bottomright[0] + corner_radius, topleft[1] - corner_radius),
            #                   radius=corner_radius, start_angle=np.pi, end_angle=np.pi/2, layer=layer, etch=True)
            # if n != 0:  # Left corners
            #     p.add_graphic_arc(center=(topleft[0] - corner_radius, bottomright[1] - corner_radius),
            #                       radius=corner_radius, start_angle=np.pi, end_angle=np.pi/2, layer=layer, etch=True)
            #     p.add_graphic_arc(center=(topleft[0] - corner_radius, topleft[1] - corner_radius),
            #                       radius=corner_radius, start_angle=np.pi/2, end_angle=0, layer=layer, etch=True)

        # Define offset for the bottom-right corner
        # offset = [(0, 0), (r_corner, 0)]
        # offset += [(r_corner*(1 - np.sin(idt*np.pi/2/N_corner)),
        #             r_corner*(np.cos(idt*np.pi/2/N_corner) - 1)) for idt in range(N_corner + 1)]
        # # offset += [(-w/2, -r_corner)]
        # for layer in layers:
        #     if n != 0:
        #         pts = [(topleft[0] - pt[0], bottomright[1] + pt[1]) for pt in offset]
        #         p.add_fill_zone_polygon(pts, layer=layer, net="0 main")
        #
        #         pts = [(topleft[0] - pt[0], topleft[1] - pt[1]) for pt in offset]
        #         p.add_fill_zone_polygon(pts, layer=layer, net="0 main")
        #
        #     if n == N - 1 and not normal_last_beam:
        #         offset = [(0, 0), (cut_radius, 0)]
        #         offset += [(cut_radius*(1 - np.sin(idt*np.pi/2/N_corner)),
        #                     cut_radius*(np.cos(idt*np.pi/2/N_corner) - 1)) for idt in range(N_corner + 1)]
        #         # offset += [(-w/2, -cut_radius)]
        #     pts = [(bottomright[0] + pt[0], bottomright[1] + pt[1]) for pt in offset]
        #     p.add_fill_zone_polygon(pts, layer=layer, net="0 main")
        #
        #     pts = [(bottomright[0] + pt[0], topleft[1] - pt[1]) for pt in offset]
        #     p.add_fill_zone_polygon(pts, layer=layer, net="0 main")

    # if backside_copper:
    #     p.add_via((x + via_radius*2, y + via_radius*2))
    #     p.add_via((x + via_radius*2, y + 2*h_bondpad + l - via_radius*2))
    #
    # ##############################################################################################
    # # Add outer edges for each cut
    # ##############################################################################################
    y_buffer = l/2 - cut_radius
    inset = N*w + (N - 1)*gap + kerf_board_edge + cut_radius
    # print(inset, N, w, gap, BOARD_EDGE_SPACING_EFF)

    # for layer in ["Eco2.User", "F.SilkS"]:
    panel_spacing = 0.
    for layer in ["Edge.Cuts"]:
        p.add_graphic_line([(x - BOARD_EDGE_SPACING_EFF, y - BOARD_EDGE_SPACING_EFF),
                            (x - BOARD_EDGE_SPACING_EFF, y + l + 2*h_bondpad + BOARD_EDGE_SPACING_EFF),
                            (x - BOARD_EDGE_SPACING_EFF + panel_spacing, y + l + 2*h_bondpad + BOARD_EDGE_SPACING_EFF),
                            (x + w_bondpad - panel_spacing - 2*m2_offset,
                             y + l + 2*h_bondpad + BOARD_EDGE_SPACING_EFF)], layer=layer, cut=True, etch=True)
        p.add_graphic_arc((x + w_bondpad - 2*m2_offset,
                           y + l + 2*h_bondpad + BOARD_EDGE_SPACING_EFF + m2_offset), m2_offset, -np.pi/2, 0,
                          layer=layer, cut=True, etch=True)
        p.add_graphic_line([(x + w_bondpad - m2_offset, y + l + 2*h_bondpad + BOARD_EDGE_SPACING_EFF + m2_offset),
                            (x + w_bondpad - m2_offset, y + l + 2*h_bondpad + 2*m2_offset),
                            (x + w_bondpad - m2_offset + panel_spacing, y + l + 2*h_bondpad + 2*m2_offset),
                            (x + w_bondpad + boundary_gap, y + l + 2*h_bondpad + 2*m2_offset),
                            (x + w_bondpad + boundary_gap, y + l + 2*h_bondpad + 2*m2_offset - panel_spacing),
                            (x + w_bondpad + boundary_gap, y + l - y_buffer + h_bondpad + panel_spacing),
                            (x + w_bondpad + boundary_gap, y + l - y_buffer + h_bondpad),
                            (x + inset, y + l - y_buffer + h_bondpad)], layer=layer, cut=True, etch=True)
        p.add_graphic_line([(x - BOARD_EDGE_SPACING_EFF + panel_spacing, y - BOARD_EDGE_SPACING_EFF),
                            (x + w_bondpad - panel_spacing - 2*m2_offset, y - BOARD_EDGE_SPACING_EFF)], layer=layer,
                           cut=True, etch=True)
        p.add_graphic_arc((x + w_bondpad - 2*m2_offset,
                           y - BOARD_EDGE_SPACING_EFF - m2_offset), m2_offset, np.pi/2, 0, layer=layer, cut=True,
                          etch=True)
        p.add_graphic_line([(x + w_bondpad - m2_offset, y - BOARD_EDGE_SPACING_EFF - m2_offset),
                            (x + w_bondpad - m2_offset, y - 2*m2_offset),
                            (x + w_bondpad + boundary_gap, y - 2*m2_offset),
                            (x + w_bondpad + boundary_gap, y + y_buffer + h_bondpad),
                            (x + inset, y + y_buffer + h_bondpad)], layer=layer, cut=True, etch=True)
        p.add_graphic_arc((x + inset, y + 2.5*l/5 + h_bondpad), cut_radius, np.pi/2, 3*np.pi/2, layer=layer, cut=True,
                          etch=True)

        ##############################################################################################
        # Add drills
        ##############################################################################################
        p.add_M2_drill((x + w_bondpad, y - m2_offset), plated=True, etch=True)
        p.add_M2_drill((x + w_bondpad, y + 2*h_bondpad + l + m2_offset), plated=True, etch=True)

        ##############################################################################################
        # Add traces to connect to drills
        ##############################################################################################
        # Top cut boundary
        p.add_trace([(x + w_bondpad, y - m2_offset),
                     (x + w_bondpad, y),
                     (x + w_bondpad/2, y + w_bondpad/2)],
                    width=1, net=net, etch=True)
        # pts = p.offset_trace([(x + w_bondpad, y - m2_offset),
        #                       (x + w_bondpad, y),
        #                       (x + w_bondpad/2, y + w_bondpad/2)], w=1)
        # p.add_fill_zone_polygon(pts, net=net, etch=True)
        # Bottom cut boundary
        p.add_trace([(x + w_bondpad, y + 2*h_bondpad + l + m2_offset),
                     (x + w_bondpad, y + 2*h_bondpad + l),
                     (x + w_bondpad/2, y + 2*h_bondpad + l - w_bondpad/2)],
                    width=1, net=net, etch=True)
        # pts = p.offset_trace([(x + w_bondpad, y + 2*h_bondpad + l + m2_offset),
        #                       (x + w_bondpad, y + 2*h_bondpad + l),
        #                       (x + w_bondpad/2, y + 2*h_bondpad + l - w_bondpad/2)], w=1)
        # p.add_fill_zone_polygon(pts, net=net, etch=True)
        return p


if __name__ == '__main__':
    p = PCBPattern()
    p = generate_test_pcb(p)
    # pyperclip.copy(out)

    now = datetime.now()
    name_clarifier = "_singleflexsts_uvlasercutter"
    timestamp = now.strftime("%Y%m%d_%H_%M_%S") + name_clarifier

    # kicad_filename = "C:/Users/ahadrauf/Desktop/Research/pcb_wire_testing_setup/pcb_wire_testing_setup.kicad_pcb"
    dxf_cut_filename = "C:/Users/ahadrauf/Desktop/Research/pcb_wire_testing_setup/patterns/{}_cut.dxf".format(timestamp)
    dxf_etch_filename = "C:/Users/ahadrauf/Desktop/Research/pcb_wire_testing_setup/patterns/{}_etch.dxf".format(
        timestamp)
    offset_x = 0.
    offset_y = 0.
    # p.generate_kicad(kicad_filename, save=True, offset_x=x_buffer, offset_y=buffer_height)
    p.generate_dxf(dxf_cut_filename, dxf_etch_filename, save_cut=True, save_etch=True, offset_x=offset_x, offset_y=offset_y,
                   cut_layers=("Edge.Cuts", "Eco2.User"), etch_layers=("F.Cu", "Edge.Cuts", 'Eco2.User'),
                   merge_overlapping_polygons=(), include_traces_etch=True)
