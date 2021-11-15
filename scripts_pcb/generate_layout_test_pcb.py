import numpy as np
from pcb_layout import *
import pyperclip


# MIL_TO_MM = 0.0254


def generate_test_pcb():
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
    out = ""

    for idx in range(nx):
        for w_idx in range(len(N_range)):
            for idy in range(ny):
                ##############################################################################################
                # Define parameters
                ##############################################################################################
                gap = gaps[idx] if (idx < 2 and idy < 3) else gaps[0]
                if idx == nx - 1 and idy == 0:
                    kerf = 1
                elif idx == nx - 1 and idy == 1:
                    kerf = 2
                else:
                    kerf = 3
                w = w_range[w_idx]
                N = N_range[idy] if idx < nx - 1 and idy < len(N_range) else N_range[0]
                adhesive = True if idx == nx - 1 and idy == ny - 1 else False
                backside_copper = True if idx == nx - 1 and idy == ny - 2 else False
                inset_soldermask = False if idx == 1 and idy == ny - 1 else True
                normal_last_beam = False if idx == 0 and idy == ny - 1 else True
                soldermask_buffer = 5*MIL_TO_MM if inset_soldermask else 0

                # if idx == 1 and w_idx == 0 and idy == 0:
                #     N = 10
                #     gap = gaps[0]
                if idx == 1 and idy == 0:
                    kerf_board_edge = kerf_board_edge_range[w_idx]
                else:
                    kerf_board_edge = kerf_board_edge_default

                r_corner = gap/2
                l = kerf + 2*kerf_board_edge
                x_offset = (total_width + w_buffer)*idx
                cut_radius = (l - 2*kerf_board_edge)/2  # 1.5*l/5

                ##############################################################################################
                # Add text labels to each array
                ##############################################################################################
                x = x_offset + (w_bondpad + w_buffer)*w_idx + w_bondpad + text_height/2 + BOARD_EDGE_SPACING_EFF*3
                y = (h_bondpad*2 + l_nom + h_buffer)*idy + text_width + 1.5
                txt = "N={},w={},g={},k={}".format(int(N), np.round(w/MIL_TO_MM).astype(np.int8),
                                                np.round(gap/MIL_TO_MM).astype(np.int8),
                                                   kerf)
                out += add_text(txt, (x, y), 90, scale=text_scale, thickness=LINESPACE*1.5, linestart=linestart)
                y += h_bondpad + l
                txt = "{}, {}, {}, {}, e={}".format("A" if adhesive else "NA",
                                                    "B" if backside_copper else "NB",
                                                    "S" if inset_soldermask else "NS",
                                                    "L" if normal_last_beam else "WL",
                                                    np.round(kerf_board_edge/MIL_TO_MM).astype(np.int8))
                out += add_text(txt, (x, y), 90, scale=text_scale, thickness=LINESPACE*1.5, linestart=linestart)

                ##############################################################################################
                # Add main copper pads
                ##############################################################################################
                x = x_offset + (w_bondpad + w_buffer)*w_idx
                y = (h_bondpad*2 + l_nom + h_buffer)*idy
                if backside_copper:
                    layers = ["F.Cu", "B.Cu"]
                else:
                    layers = ["F.Cu"]
                for layer in layers:
                    out += add_fill_zone_rectangle((x, y), (x + w_bondpad, y + h_bondpad),
                                                   layer=layer, linestart=linestart)
                    out += add_fill_zone_rectangle((x, y + h_bondpad + l), (x + w_bondpad, y + l + 2*h_bondpad),
                                                   layer=layer, linestart=linestart)
                out += add_fill_zone_rectangle((x + soldermask_buffer, y + soldermask_buffer),
                                               (x + w_bondpad - soldermask_buffer, y + h_bondpad - soldermask_buffer),
                                               layer="F.Mask", linestart=linestart)
                out += add_fill_zone_rectangle((x + soldermask_buffer, y + h_bondpad + l + soldermask_buffer),
                                               (x + w_bondpad - soldermask_buffer,
                                                y + l + 2*h_bondpad - soldermask_buffer),
                                               layer="F.Mask", linestart=linestart)

                ##############################################################################################
                # Add wires
                ##############################################################################################
                for n in range(N):
                    topleft = (x + (gap + w)*n, y + h_bondpad)
                    bottomright = (x + (gap + w)*n + w, y + h_bondpad + l)
                    # Add wire
                    for layer in layers:
                        out += add_fill_zone_rectangle((topleft[0], topleft[1] - 0.1),
                                                       (bottomright[0], bottomright[1] + 0.1), linestart=linestart,
                                                       layer=layer)

                    # Added rounded corners
                    # Define offset for the bottom-right corner
                    offset = [(-w/2, 0.1), (r_corner, 0.1)]
                    offset += [(r_corner*(1 - np.sin(idt*np.pi/2/N_corner)),
                                r_corner*(np.cos(idt*np.pi/2/N_corner) - 1)) for idt in range(N_corner + 1)]
                    offset += [(-w/2, -r_corner)]
                    for layer in layers:
                        if n != 0:
                            pts = [(topleft[0] - pt[0], bottomright[1] + pt[1]) for pt in offset]
                            out += add_fill_zone_polygon(pts, linestart=linestart, layer=layer)

                            pts = [(topleft[0] - pt[0], topleft[1] - pt[1]) for pt in offset]
                            out += add_fill_zone_polygon(pts, linestart=linestart, layer=layer)

                        if n == N - 1 and not normal_last_beam:
                            offset = [(-w/2, 0.1), (cut_radius, 0.1)]
                            offset += [(cut_radius*(1 - np.sin(idt*np.pi/2/N_corner)),
                                        cut_radius*(np.cos(idt*np.pi/2/N_corner) - 1)) for idt in range(N_corner + 1)]
                            offset += [(-w/2, -cut_radius)]
                        pts = [(bottomright[0] + pt[0], bottomright[1] + pt[1]) for pt in offset]
                        out += add_fill_zone_polygon(pts, linestart=linestart, layer=layer)

                        pts = [(bottomright[0] + pt[0], topleft[1] - pt[1]) for pt in offset]
                        out += add_fill_zone_polygon(pts, linestart=linestart, layer=layer)

                if backside_copper:
                    out += add_via((x + via_radius*2, y + via_radius*2))
                    out += add_via((x + via_radius*2, y + 2*h_bondpad + l - via_radius*2))

                ##############################################################################################
                # Add outer edges for each cut
                ##############################################################################################
                y_buffer = l/2 - cut_radius
                inset = N*w + (N - 1)*gap + kerf_board_edge + cut_radius
                # print(inset, N, w, gap, BOARD_EDGE_SPACING_EFF)

                # for layer in ["Eco2.User", "F.SilkS"]:
                for layer in ["Eco2.User"]:
                    out += add_boundary([(x - BOARD_EDGE_SPACING_EFF, y - BOARD_EDGE_SPACING_EFF),
                                         (x - BOARD_EDGE_SPACING_EFF, y + l + 2*h_bondpad + BOARD_EDGE_SPACING_EFF)],
                                        layer=layer)
                    # Bottom cut boundary
                    out += add_boundary([(x - BOARD_EDGE_SPACING_EFF + panel_spacing,
                                          y + l + 2*h_bondpad + BOARD_EDGE_SPACING_EFF),
                                         (x + w_bondpad - panel_spacing - 2*m2_offset,
                                          y + l + 2*h_bondpad + BOARD_EDGE_SPACING_EFF)], layer=layer)
                    out += add_arc((x + w_bondpad - 2*m2_offset,
                                    y + l + 2*h_bondpad + BOARD_EDGE_SPACING_EFF + m2_offset), m2_offset, -np.pi/2, 0,
                                   layer=layer,
                                   linestart=linestart)
                    out += add_boundary(
                        [(x + w_bondpad - m2_offset, y + l + 2*h_bondpad + BOARD_EDGE_SPACING_EFF + m2_offset),
                         (x + w_bondpad - m2_offset, y + l + 2*h_bondpad + 2*m2_offset)], layer=layer)
                    out += add_boundary([(x + w_bondpad - m2_offset + panel_spacing, y + l + 2*h_bondpad + 2*m2_offset),
                                         (x + w_bondpad + boundary_gap, y + l + 2*h_bondpad + 2*m2_offset)],
                                        layer=layer)
                    out += add_boundary(
                        [(x + w_bondpad + boundary_gap, y + l + 2*h_bondpad + 2*m2_offset - panel_spacing),
                         (x + w_bondpad + boundary_gap, y + l - y_buffer + h_bondpad + panel_spacing)],
                        layer=layer)
                    out += add_boundary([(x + w_bondpad + boundary_gap, y + l - y_buffer + h_bondpad),
                                         (x + inset, y + l - y_buffer + h_bondpad)], layer=layer, linestart=linestart)

                    # Top cut boundary
                    out += add_boundary([(x - BOARD_EDGE_SPACING_EFF + panel_spacing,
                                          y - BOARD_EDGE_SPACING_EFF),
                                         (x + w_bondpad - panel_spacing - 2*m2_offset,
                                          y - BOARD_EDGE_SPACING_EFF)], layer=layer)
                    out += add_arc((x + w_bondpad - 2*m2_offset,
                                    y - BOARD_EDGE_SPACING_EFF - m2_offset), m2_offset, np.pi/2, 0, layer=layer,
                                   linestart=linestart)
                    out += add_boundary([(x + w_bondpad - m2_offset, y - BOARD_EDGE_SPACING_EFF - m2_offset),
                                         (x + w_bondpad - m2_offset, y - 2*m2_offset)], layer=layer)
                    out += add_boundary([(x + w_bondpad - m2_offset + panel_spacing, y - 2*m2_offset),
                                         (x + w_bondpad + boundary_gap, y - 2*m2_offset)], layer=layer)
                    out += add_boundary([(x + w_bondpad + boundary_gap, y - 2*m2_offset + panel_spacing),
                                         (x + w_bondpad + boundary_gap, y + y_buffer + h_bondpad - panel_spacing)],
                                        layer=layer)
                    out += add_boundary([(x + w_bondpad + boundary_gap, y + y_buffer + h_bondpad),
                                         (x + inset, y + y_buffer + h_bondpad)], layer=layer, linestart=linestart)
                    out += add_arc((x + inset, y + 2.5*l/5 + h_bondpad), cut_radius, np.pi/2, 3*np.pi/2, layer=layer,
                                   linestart=linestart)

                ##############################################################################################
                # Add drills
                ##############################################################################################
                out += add_M2_drill_plated((x + w_bondpad, y - m2_offset))
                out += add_M2_drill_plated((x + w_bondpad, y + 2*h_bondpad + l + m2_offset))

                ##############################################################################################
                # Add traces to connect to drills
                ##############################################################################################
                # Top cut boundary
                out += add_trace([(x + w_bondpad, y - m2_offset),
                                  (x + w_bondpad, y),
                                  (x + w_bondpad/2, y + w_bondpad/2)],
                                 width=1)
                # Bottom cut boundary
                out += add_trace([(x + w_bondpad, y + 2*h_bondpad + l + m2_offset),
                                  (x + w_bondpad, y + 2*h_bondpad + l),
                                  (x + w_bondpad/2, y + 2*h_bondpad + l - w_bondpad/2)],
                                 width=1)

    ##############################################################################################
    # Add outside boundary
    ##############################################################################################
    out += add_boundary([(-outside_buffer/2, -outside_buffer - 1.5*m2_offset),
                         (-outside_buffer/2, total_height + outside_buffer - 0.5*m2_offset),
                         (nx*total_width + (nx - 1)*w_buffer + 1.5*outside_buffer, total_height + outside_buffer - 0.5*m2_offset),
                         (nx*total_width + (nx - 1)*w_buffer + 1.5*outside_buffer, -outside_buffer - 1.5*m2_offset),
                         (-outside_buffer/2, -outside_buffer - 1.5*m2_offset)],
                        linestart=linestart)
    out += add_boundary([(-outside_buffer/2, -outside_buffer - 1.5*m2_offset),
                         (-outside_buffer/2, total_height + outside_buffer - 0.5*m2_offset),
                         (nx*total_width + (nx - 1)*w_buffer + 1.5*outside_buffer,
                          total_height + outside_buffer - 0.5*m2_offset),
                         (nx*total_width + (nx - 1)*w_buffer + 1.5*outside_buffer, -outside_buffer - 1.5*m2_offset),
                         (-outside_buffer/2, -outside_buffer - 1.5*m2_offset)],
                        linestart=linestart, layer='Eco2.User')

    ##############################################################################################
    # Add adhesive test structure
    ##############################################################################################
    topleft = ((total_width + w_buffer)*(nx - 1) - BOARD_EDGE_SPACING_EFF,
               (h_bondpad*2 + l_nom + h_buffer)*(ny - 1) - boundary_gap - m2_offset)
    bottomright = (topleft[0] + total_width + boundary_gap + BOARD_EDGE_SPACING_EFF,
                   topleft[1] + (h_bondpad*2 + l_nom) + 2*boundary_gap + 2*m2_offset)
    out += add_fill_zone_rectangle(topleft, bottomright, layer='B.Adhes')
    return out


if __name__ == '__main__':
    out = add_header()
    out += generate_test_pcb()
    out += add_footer()
    # pyperclip.copy(out)

    filename = "C:/Users/ahadrauf/Desktop/Research/pcb_wire_testing_setup/pcb_wire_testing_setup.kicad_pcb"
    with open(filename, 'w') as f:
        f.write(out)
