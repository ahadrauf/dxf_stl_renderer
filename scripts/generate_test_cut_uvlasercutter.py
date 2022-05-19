from pattern import *
from settings import *
import numpy as np
from datetime import datetime


# def generate_square_grid(p: Pattern, topleft, size_x, size_y, nx, ny):
#     x, y = topleft
#     for i in range(nx + 1):
#         for j in range(ny + 1):
#             p.add_line(())

def generate_two_squares(p: Pattern, topleft, width, length,
                         include_left=True, include_top=True, include_right=True, include_bottom=True):
    x, y = topleft
    y_bottom = y + 2*length
    if include_top:
        p.add_line((x, y), (x + width, y))
    if include_left:
        p.add_line((x, y), (x, y_bottom))
    if include_bottom:
        p.add_line((x, y_bottom), (x + width, y_bottom))
    if include_right:
        p.add_line((x + width, y_bottom), (x + width, y))

    p.add_line((x, y + length), (x + width, y + length))

    return p


def generate_two_squares_buffer_length(p: Pattern, topleft, width, length, length_buffer,
                                       include_left=True, include_top=True, include_right=True, include_bottom=True,
                                       include_buffer_hole=True, buffer_hole_radius=1.2):
    x, y = topleft
    y_bottom = y + 2*length + length_buffer
    if include_top:
        p.add_line((x, y), (x + width, y))
    if include_left:
        p.add_line((x, y), (x, y_bottom))
    if include_bottom:
        p.add_line((x, y_bottom), (x + width, y_bottom))
    if include_right:
        p.add_line((x + width, y_bottom), (x + width, y))

    p.add_line((x, y + length), (x + width/2, y + length))
    p.add_line((x + width/2, y + length), (x + width/2, y + length + length_buffer))
    p.add_line((x + width/2, y + length + length_buffer), (x + width, y + length + length_buffer))

    if include_buffer_hole:
        p.add_circle((x + 3*width/4, y + length + length_buffer - 1.5*buffer_hole_radius), buffer_hole_radius)
        p.add_circle((x + width/4, y + length + 1.5*buffer_hole_radius), buffer_hole_radius)

    return p


if __name__ == '__main__':
    now = datetime.now()
    name_clarifier = "_ets_uvlasercutter_mylar"
    timestamp = now.strftime("%Y%m%d_%H_%M_%S") + name_clarifier
    print(timestamp)

    p = Pattern(setting=LaserCutter)
    # p.add_rectangle((0, 0), (10, 20))
    # p.add_line((15, 0), (15, 20), kerf=2)

    # p = generate_two_squares_buffer_length(p, (0, 0), 10, 10, 5, include_right=False)
    # p = generate_two_squares(p, (10, 0), 15, 15)
    # p = generate_two_squares_buffer_length(p, (0, 0), 12, 12, 13)
    # width = 17
    # p.add_lines([(12, 0), (12+2*width, 0), (12+2*width, 25), (12, 25)])
    # p.add_line((12+width, 0), (12+width, 25))
    width = 19.45
    p = generate_two_squares_buffer_length(p, (0, 0), width, width, 7.5)
    p = generate_two_squares(p, (width, 0), width, width, include_left=True)

    # w, h = 60, 25
    # edgegap = 2
    # metalgap = 10
    # p.add_rectangle((0, 0), (w, h))
    # p.add_rectangle((edgegap, edgegap), (w/2 - metalgap/2, h - edgegap))
    # p.add_rectangle((w/2 + metalgap/2, edgegap), (w - edgegap, h - edgegap))

    # p.generate_svg('../patterns/' + timestamp + '.svg')
    p.generate_dxf('../patterns/' + timestamp + '.dxf', save=True)
