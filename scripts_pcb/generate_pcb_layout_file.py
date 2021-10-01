import numpy as np
from pcb_layout import *
import pyperclip


# MIL_TO_MM = 0.0254


def generate_test_pcb():
    N_range = np.array([1, 3, 5])
    w_range = np.array([3., 6., 9.])*MIL_TO_MM
    kerf = 3
    gaps = np.array([LINESPACE, 2*LINESPACE, LINESPACE])
    N_corner = 10
    text_scale = 0.45
    nx, ny = 3, 4

    l = kerf + 2*BOARD_EDGE_SPACING_EFF
    print(l)
    w_bondpad = 8.
    h_bondpad = 8.
    w_buffer = 5.
    h_buffer = 5.
    outside_buffer = 2
    soldermask_buffer = 5*MIL_TO_MM
    panel_spacing = BOARD_EDGE_SPACING_EFF*2
    linestart = '  '
    total_width = len(N_range)*w_bondpad + (len(N_range) - 1)*w_buffer
    total_height = len(w_range)*(2*h_bondpad + l) + (len(w_range) - 1)*h_buffer
    text_width = 6.75*text_scale  # 4.064  # measured in KiCad
    text_height = 0.508*text_scale  # measured in KiCad

    print("Total Width", len(gaps)*total_width + len(gaps)*outside_buffer + (len(gaps) - 1)*w_buffer)
    print("Total Height", total_height + 2*outside_buffer)
    out = ""

    for gap_idx in range(len(gaps)):
        gap = gaps[gap_idx]
        r_corner = gap/2
        x_offset = (total_width + w_buffer)*gap_idx
        # Add text labels to each array
        for idx in range(len(N_range)):
            N = N_range[idx]
            for idy in range(len(w_range)):
                w = w_range[idy]
                x = x_offset + (w_bondpad + w_buffer)*idx + w_bondpad + text_height/2 + BOARD_EDGE_SPACING_EFF*3
                # y = (h_bondpad*2 + l + h_buffer)*idy + h_bondpad/2 - text_width/2
                y = (h_bondpad*2 + l + h_buffer)*idy + text_width - text_width/3  # the final term = to move text up
                txt = "N={}, w={}, g={}".format(int(N), np.round(w/MIL_TO_MM).astype(np.int8),
                                                np.round(gap/MIL_TO_MM).astype(np.int8))
                out += add_text(txt, (x, y), 90, scale=text_scale, thickness=LINESPACE*1.5, linestart=linestart)

        for idx in range(len(N_range)):
            N = N_range[idx]
            for idy in range(len(w_range)):
                w = w_range[idy]
                x = x_offset + (w_bondpad + w_buffer)*idx
                y = (h_bondpad*2 + l + h_buffer)*idy
                out += add_fill_zone_rectangle((x, y), (x + w_bondpad, y + h_bondpad),
                                               layer="F.Cu", linestart=linestart)
                out += add_fill_zone_rectangle((x, y + h_bondpad + l), (x + w_bondpad, y + l + 2*h_bondpad),
                                               layer="F.Cu", linestart=linestart)
                out += add_fill_zone_rectangle((x + soldermask_buffer, y + soldermask_buffer),
                                               (x + w_bondpad - soldermask_buffer, y + h_bondpad - soldermask_buffer),
                                               layer="F.Mask", linestart=linestart)
                out += add_fill_zone_rectangle((x + soldermask_buffer, y + h_bondpad + l + soldermask_buffer),
                                               (x + w_bondpad - soldermask_buffer,
                                                y + l + 2*h_bondpad - soldermask_buffer),
                                               layer="F.Mask", linestart=linestart)
                for n in range(N):
                    topleft = (x + (gap + w)*n, y + h_bondpad)
                    bottomright = (x + (gap + w)*n + w, y + h_bondpad + l)
                    # Add wire
                    out += add_fill_zone_rectangle((topleft[0], topleft[1] - 0.1),
                                                   (bottomright[0], bottomright[1] + 0.1), linestart=linestart)

                    # Added rounded corners
                    # Define offset for the bottom-right corner
                    offset = [(-w/2, 0.1), (r_corner, 0.1)]
                    offset += [(r_corner*(1 - np.sin(idt*np.pi/2/N_corner)),
                                r_corner*(np.cos(idt*np.pi/2/N_corner) - 1)) for idt in range(N_corner + 1)]
                    offset += [(-w/2, -r_corner)]
                    pts = [(bottomright[0] + pt[0], bottomright[1] + pt[1]) for pt in offset]
                    out += add_fill_zone_polygon(pts, linestart=linestart)

                    pts = [(bottomright[0] + pt[0], topleft[1] - pt[1]) for pt in offset]
                    out += add_fill_zone_polygon(pts, linestart=linestart)

                    if n != 0:
                        pts = [(topleft[0] - pt[0], bottomright[1] + pt[1]) for pt in offset]
                        out += add_fill_zone_polygon(pts, linestart=linestart)

                        pts = [(topleft[0] - pt[0], topleft[1] + -pt[1]) for pt in offset]
                        out += add_fill_zone_polygon(pts, linestart=linestart)

                boundary_gap = 1.5
                radius = (l - 2*BOARD_EDGE_SPACING_EFF)/2  # 1.5*l/5
                y_buffer = l/2 - radius
                inset = N*w + (N - 1)*gap + BOARD_EDGE_SPACING_EFF + radius
                m2_drill_diameter = 2.2
                m2_offset_x = max(m2_drill_diameter/2, kerf/2)
                print(inset, N, w, gap, BOARD_EDGE_SPACING_EFF)

                # out += add_boundary([(x - boundary_gap, y - boundary_gap),
                #               (x - boundary_gap, y + l + 2*h_bondpad + boundary_gap),
                #               (x + w_bondpad + boundary_gap, y + l + 2*h_bondpad + boundary_gap),
                #               (x + w_bondpad + boundary_gap, y + 4*l/5 + h_bondpad),
                #               (x + inset, y + 4*l/5 + h_bondpad)], linestart=linestart)
                for layer in ["Eco2.User", "F.SilkS"]:
                    out += add_boundary([(x - boundary_gap, y - boundary_gap),
                                         (x - boundary_gap, y + l + 2*h_bondpad + boundary_gap)],
                                        layer=layer)
                    out += add_boundary([(x - boundary_gap + panel_spacing, y + l + 2*h_bondpad + boundary_gap),
                                         (x + w_bondpad + boundary_gap - panel_spacing,
                                          y + l + 2*h_bondpad + boundary_gap)], layer=layer)
                    out += add_boundary([(x + w_bondpad + boundary_gap, y + l + 2*h_bondpad + boundary_gap),
                                         (x + w_bondpad + boundary_gap, y + l - y_buffer + h_bondpad),
                                         (x + inset, y + l - y_buffer + h_bondpad)], layer=layer, linestart=linestart)
                    out += add_boundary([(x - boundary_gap + panel_spacing, y - boundary_gap),
                                         (x + w_bondpad + boundary_gap - panel_spacing, y - boundary_gap)],
                                        layer=layer)
                    out += add_boundary([(x + w_bondpad + boundary_gap, y - boundary_gap),
                                         (x + w_bondpad + boundary_gap, y + y_buffer + h_bondpad),
                                         (x + inset, y + y_buffer + h_bondpad)], layer=layer, linestart=linestart)
                    out += add_arc((x + inset, y + 2.5*l/5 + h_bondpad), radius, np.pi/2, 3*np.pi/2, layer=layer,
                                   linestart=linestart)

                out += add_M2_drill((x - BOARD_EDGE_SPACING_EFF - m2_offset_x, y + m2_drill_diameter))

    out += add_boundary([(-outside_buffer, -outside_buffer),
                         (-outside_buffer, total_height + outside_buffer),
                         (len(gaps)*total_width + (len(gaps) - 1)*w_buffer + outside_buffer,
                          total_height + outside_buffer),
                         (len(gaps)*total_width + (len(gaps) - 1)*w_buffer + outside_buffer, -outside_buffer),
                         (-outside_buffer, -outside_buffer)],
                        linestart=linestart)

    topleft = ((total_width + w_buffer)*(len(gaps) - 1) - boundary_gap, -boundary_gap)
    bottomright = (topleft[0] + total_width + 2*boundary_gap,
                   topleft[1] + (h_bondpad*2 + l)*len(w_range) + h_buffer*(len(w_range) - 1) + 2*boundary_gap)
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
