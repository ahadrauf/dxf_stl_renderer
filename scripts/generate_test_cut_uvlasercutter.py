from pattern import *
from settings import *
import numpy as np
from datetime import datetime

if __name__ == '__main__':
    now = datetime.now()
    name_clarifier = "_test_cut_uvlasercutter_outline"
    timestamp = now.strftime("%Y%m%d_%H_%M_%S") + name_clarifier
    print(timestamp)

    p = Pattern(setting=LaserCutter)
    # p.add_rectangle((0, 0), (10, 20))
    # p.add_line((15, 0), (15, 20), kerf=2)

    w, h = 60, 25
    edgegap = 2
    metalgap = 10
    p.add_rectangle((0, 0), (w, h))
    # p.add_rectangle((edgegap, edgegap), (w/2 - metalgap/2, h - edgegap))
    # p.add_rectangle((w/2 + metalgap/2, edgegap), (w - edgegap, h - edgegap))

    # p.generate_svg('../patterns/' + timestamp + '.svg')
    p.generate_dxf('../patterns/' + timestamp + '.dxf', save=True)
