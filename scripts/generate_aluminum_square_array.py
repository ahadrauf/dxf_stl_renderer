from pattern import *
from settings import *
import numpy as np
from datetime import datetime

INCH_TO_MM = 25.4


def generate_aluminum_square_array(nx, ny, cell_width, cell_height):
    p = Pattern()
    total_width = nx*cell_width
    total_height = ny*cell_height

    for i in range(nx + 1):
        p.add_line((cell_width*i, 0), (cell_width*i, total_height))
    for j in range(ny + 1):
        p.add_line((0, cell_height*j), (total_width, cell_height*j))



    return p


if __name__ == '__main__':
    nx = 5
    ny = 5
    cell_width = 15
    cell_height = 15
    sheet_width = 20*INCH_TO_MM
    sheet_height = 12*INCH_TO_MM

    print("Total Number of Cells", nx*ny)
    assert (nx*cell_width < sheet_width)
    assert (ny*cell_height < sheet_height)

    now = datetime.now()
    name_clarifier = "_epoxy_array_nx={}_ny={}_cellwidth={}_cellheight={}".format(nx, ny,
                                                                                            cell_width, cell_height)
    timestamp = now.strftime("%Y%m%d_%H_%M_%S") + name_clarifier
    print(timestamp)
    p = generate_aluminum_square_array(nx, ny, cell_width, cell_height)

    # p.generate_svg('../patterns/' + timestamp + '.svg', save=True, default_linewidth=1)
    p.generate_dxf('../patterns/' + timestamp + '.dxf', save=True)
