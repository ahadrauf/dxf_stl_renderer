import numpy as np
from pcb_layout import *
import pyperclip

MIL_TO_MM = 0.0254


def generate_test_pcb():
    N_range = np.array([1, 3, 5])
    w_range = np.array([3., 6., 9.])*MIL_TO_MM
    l = 5.
    gap = 3.*MIL_TO_MM
    r_corner = 1.5*MIL_TO_MM
    N_corner = 5

    w_bondpad = 8.
    h_bondpad = 8.
    w_buffer = 5.
    h_buffer = 5.
    outside_buffer = 5.
    linestart = '  '
    total_width = len(N_range)*w_bondpad + (len(N_range) - 1)*w_buffer
    total_height = len(w_range)*(2*h_bondpad + l) + (len(w_range) - 1)*h_buffer
    text_width = 4.064  # measured in KiCad
    text_height = 0.508  # measured in KiCad

    print("Total Width", total_width + 2*gap)
    print("Total Height", total_height + 2*gap)
    out = ""

    for idx in range(len(N_range)):
        N = N_range[idx]
        for idy in range(len(w_range)):
            w = w_range[idy]
            # x = (w_bondpad + w_buffer)*idx + (gap + w)*N + text_width / 2
            # y = (h_bondpad*2 + l + h_buffer)*idy + h_bondpad + gap + text_height / 2
            x = (w_bondpad + w_buffer)*idx - text_height/2 - gap/2
            y = (h_bondpad*2 + l + h_buffer)*idy + h_bondpad/2 - text_width/2
            txt = "N={}, w={}".format(int(N), np.round(w/MIL_TO_MM).astype(np.int8))
            out += add_text(txt, (x, y), 90, linestart=linestart)

    out += add_boundary([(-outside_buffer, -outside_buffer),
                         (-outside_buffer, total_height + outside_buffer),
                         (total_width + outside_buffer, total_height + outside_buffer),
                         (total_width + outside_buffer, -outside_buffer),
                         (-outside_buffer, -outside_buffer)],
                        linestart=linestart)

    for idx in range(len(N_range)):
        N = N_range[idx]
        for idy in range(len(w_range)):
            w = w_range[idy]
            x = (w_bondpad + w_buffer)*idx
            y = (h_bondpad*2 + l + h_buffer)*idy
            out += add_fill_zone_rectangle((x, y), (x + w_bondpad, y + h_bondpad), linestart=linestart)
            out += add_fill_zone_rectangle((x, y + h_bondpad + l), (x + w_bondpad, y + l + 2*h_bondpad),
                                           linestart=linestart)
            for n in range(N):
                topleft = (x + (gap + w)*n, y + h_bondpad)
                bottomright = (x + (gap + w)*n + w, y + h_bondpad + l)
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

            # boundary_gap = 2.
            # radius = 1.5*l/5
            # inset = N*(gap + w) + radius
            # out += add_boundary([(x - boundary_gap, y - boundary_gap),
            #               (x - boundary_gap, y + l + 2*h_bondpad + boundary_gap),
            #               (x + w_bondpad + boundary_gap, y + l + 2*h_bondpad + boundary_gap),
            #               (x + w_bondpad + boundary_gap, y + 4*l/5 + h_bondpad),
            #               (x + inset, y + 4*l/5 + h_bondpad)], linestart=linestart)
            # out += add_boundary([(x - boundary_gap, y - boundary_gap),
            #               (x + w_bondpad + boundary_gap, y - boundary_gap),
            #               (x + w_bondpad + boundary_gap, y + l/5 + h_bondpad),
            #               (x + inset, y + l/5 + h_bondpad)], linestart=linestart)
            # out += add_arc((x + inset, y + 2.5*l/5 + h_bondpad), radius, np.pi/2, 3*np.pi/2, linestart=linestart)
    return out


if __name__ == '__main__':
    out = add_header()
    out += generate_test_pcb()
    out += add_footer()
    pyperclip.copy(out)

    filename = "C:/Users/ahadrauf/Desktop/Research/pcb_wire_testing_setup/pcb_wire_testing_setup.kicad_pcb"
    with open(filename, 'w') as f:
        f.write(out)