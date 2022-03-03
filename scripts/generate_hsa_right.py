"""
Generate the pattern for a handed shearing auxetic, from
https://lillych.in/files/Chin-2018-robosoft_HSA_hands.pdf
https://lillych.in/files/Lipton-2018-science.pdf
"""
from pattern import *
from settings import *
import numpy as np
from datetime import datetime

def generate_hsa_right(width, N, angle, handlebar_height):
    """
    Generate a right-handed shearing auxetic
    :param width: Width of the overall design
    :param N: Number of times each wire wraps around the design
    :param angle: Angle of wires relative to the x axis
    :param handlebar_height: Extra height to add to the ends for handles
    :return: Pattern
    """
    p = Pattern(setting=LaserCutter)



    return p

if __name__ == '__main__':
    now = datetime.now()
    name_clarifier = "_test_cut_uvlasercutter_outline"
    timestamp = now.strftime("%Y%m%d_%H_%M_%S") + name_clarifier
    print(timestamp)
