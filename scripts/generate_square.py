from pattern import *
from settings import *
import numpy as np
from datetime import datetime

if __name__ == '__main__':
    now = datetime.now()
    name_clarifier = "_square"
    timestamp = now.strftime("%Y%m%d_%H_%M_%S") + name_clarifier
    print(timestamp)

    p = Pattern(setting=LaserCutter)
    p0 = (100, 100)
    p1 = (200, 100)
    p2 = (200, 200)
    p3 = (100, 200)
    p.add_line(p0, p1, kerf=10)
    p.add_line(p1, p2, kerf=20)
    p.add_line(p2, p3, kerf=20)

    # p.generate_svg('../patterns/' + timestamp + '.svg')
    p.generate_dxf('../patterns/' + timestamp + '.dxf', save=True)
