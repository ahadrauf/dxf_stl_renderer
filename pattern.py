from settings import *
from math import cos, sin, pi
import svgwrite

class Pattern:
    def __init__(self, setting=LaserCutter):
        self.setting = setting
        self.lines = []

    def add_line(self, p1, p2, mode=LaserCutter.CUT):
        color = self.setting.COLOR[mode]
        linewidth = self.setting.LINEWIDTH[mode]
        self.lines.append((p1, p2, color, linewidth))

    def add_circle(self, center, radius, n=10, mode=LaserCutter.CUT):
        for i in range(n):
            theta = (2*pi/n)*i
            theta_next = (2*pi/n)*(i+1)
            p1 = (center[0] + radius*cos(theta), center[1] + radius*sin(theta))
            p2 = (center[0] + radius*cos(theta_next), center[1] + radius*sin(theta_next))
            self.add_line(p1, p2, mode=mode)

    def generate_svg(self, outfile: str):
        dwg = svgwrite.Drawing(outfile, profile='tiny')
        for p1, p2, color, linewidth in self.lines:
            dwg.add(dwg.line(p1, p2,
                             stroke=svgwrite.rgb(color[0], color[1], color[2])))
        dwg.save()
