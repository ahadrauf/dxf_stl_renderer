from settings import *
from math import cos, sin, pi
import numpy as np
import svgwrite
import ezdxf
import ezdxf.units
import pattern
import pcb_layout


class PCBPattern:
    def __init__(self, setting=LaserCutter):
        self.setting = setting
        # self.lines = []
        # self.lines_dxf = []
        # self.circles_dxf = []
        # self.polygons = []
        # self.text = []
        self.traces = []
        self.arcs = []
        self.kicad = ""  # text that gets written into the KiCAD file

        self.kicad += pcb_layout.add_header()

    def add_trace(self, pts, width, layer="F.Cu"):
        """
        Adds a trace with sharp edges to the layout
        :param pts: List of points
        :param width: Width of trace (ignored in DXF)
        :param layer: Trace layer (DXF will create two separate files for the top and bottom layer)
        :return: None
        """
        self.traces += (pts, width, layer)

    def add_trace_rounded(self, pts, width, n, layer="F.Cu"):
        """
        Adds a trace with rounded edges to the layout. Curved edges are generated using quadratic Bezier curves.
        :param pts: List of points
        :param width: Width of trace (ignored in DXF)
        :param n: The number of straight line segments to cut the arc into. 1 implies a straight line.
        :param layer: Trace layer (DXF will create two separate files for the top and bottom layer)
        :return: None
        """
        angles = []
        for i in range(len(pts) - 1):
            angles += np.arctan2(pts[i + 1][1] - pts[i][1], pts[i + 1][0] - pts[i][0])

        rounded_pts = []
        curr = pts[0]
        for i in range(len())

    def add_graphic_arc(self, center, radius, start_angle, end_angle, layer="Edge.Cuts"):
        """
        Adds a graphic arc (only good for graphic layers, like Edge.Cuts)
        :param center: Center of arc
        :param radius: Radius of arc
        :param start_angle: Start angle of arc (radians, CCW from +x axis)
        :param end_angle: End angle of arc (radians, CCW from +y axis)
        :param layer: Trace layer (DXF will create two separate files for the top and bottom layer)
        :return: None
        """
        self.arcs += (center, radius, start_angle, end_angle, layer)

    ############################################################################################################
    # Helper functions
    ############################################################################################################
    @staticmethod
    def generate_discretized_arc(center, radius, start_angle, end_angle, n=4):
        """
        Generates the points (ends inclusive) for an discretized arc to a non-graphic layer.
        :param center: Center of arc
        :param radius: Radius of arc
        :param start_angle: Start angle of arc (radians, CCW from +x axis)
        :param end_angle: End angle of arc (radians, CCW from +y axis)
        :param n: The number of straight line segments to cut the arc into. 1 implies a straight line.
        :return: None
        """
        theta_range = np.linspace(start_angle, end_angle, n)
        pts = [(center[0] + radius*np.cos(theta), center[1] + radius*np.sin(theta)) for theta in theta_range]
        return pts

    @staticmethod
    def quadratic_bezier_curve(start_pt, control_pt, end_pt, n):
        """
        Evaluates the quadratic bezier curve with the specified start, control, and end points
        Note that the control point determines the orientation of the bezier curve
        Reference for the quadratic Bezier curve algorithm used:
        https://en.wikipedia.org/wiki/B%C3%A9zier_curve#Quadratic_B%C3%A9zier_curves
        :param start_pt: Start point (P0)
        :param control_pt: Control point (P1)
        :param end_pt: End point (P2)
        :param n: The number of straight line segments to cut the arc into.
        :return: List of points on the Bezier curve
        """
        t_range = np.linspace(0, 1, n)
        p0 = np.array(start_pt)
        p1 = np.array(control_pt)
        p2 = np.array(end_pt)
        pts = [(1 - t)**2*p0 + 2*(1 - t)*t*p1 + t**2*p2 for t in t_range]
        return pts

    def add_line(self, p1, p2, kerf=None, n=4, update_dxf=True):
        """
        Add a line to the pattern
        :param p1: The starting point of the line (if kerf != None, this starts on the outer radius of the kerf)
        :param p2: The ending point of the line (if kerf != None, this ends on the outer radius of the kerf)
        :param kerf: The kerf with which to cut the line. Use None for a straight line, or add a number for the radius of the kerf (mm).
        :param n: The number of cuts to make in the kerf's round edges. Only used if kerf != None.
        :param mode: The drawing mode
        :return: None
        """
        color = self.setting.COLOR[mode]
        linewidth = self.setting.LINEWIDTH[mode]
        if kerf is None:
            self.lines.append((p1, p2, color, linewidth))
            if update_dxf:
                self.lines_dxf.append((p1, p2, color, linewidth))
        else:
            theta = np.arctan2(p2[1] - p1[1], p2[0] - p1[0])
            R = np.array([[np.cos(theta), -np.sin(theta)],
                          [np.sin(theta), np.cos(theta)]])
            p1top = p1 + R@[kerf, kerf]
            p2top = p2 + R@[-kerf, kerf]
            p1bot = p1 + R@[kerf, -kerf]
            p2bot = p2 + R@[-kerf, -kerf]
            p1mid = p1 + R@[kerf, 0]
            p2mid = p2 + R@[-kerf, 0]
            self.lines.append((p1top, p2top, color, linewidth))
            self.lines_dxf.append((p1top, p2top, color, linewidth))
            self.add_circle(center=p2mid, radius=kerf, n=n, start_angle=theta + np.pi/2, end_angle=theta - np.pi/2,
                            mode=mode)
            self.lines.append((p2bot, p1bot, color, linewidth))
            self.lines_dxf.append((p2bot, p1bot, color, linewidth))
            self.add_circle(center=p1mid, radius=kerf, n=n, start_angle=theta - np.pi/2, end_angle=theta - 3*np.pi/2,
                            mode=mode)

    def add_lines(self, points, kerf=None, n=4, mode=LaserCutter.CUT, update_dxf=True):
        for i in range(len(points) - 1):
            self.add_line(points[i], points[i + 1], kerf, n, mode, update_dxf)

    def add_circle(self, center, radius, n=6, start_angle=0, end_angle=2*np.pi, mode=LaserCutter.CUT) -> None:
        theta_range = np.linspace(start_angle, end_angle, n)
        for i in range(n - 1):
            theta = theta_range[i]
            theta_next = theta_range[i + 1]
            p1 = (center[0] + radius*np.cos(theta), center[1] + radius*np.sin(theta))
            p2 = (center[0] + radius*np.cos(theta_next), center[1] + radius*np.sin(theta_next))
            self.add_line(p1, p2, mode=mode, update_dxf=False)
        self.circles_dxf.append((center, radius, start_angle, end_angle))

    def add_rectangle(self, topleft, bottomright, min_thickness=0.01, layer="F.Cu", linestart='  ') -> None:
        x1, y1 = topleft
        x2, y2 = bottomright
        self.polygons.append([(x1, y1), (x1, y2), (x2, y2), (x2, y1)])
        self.kicad += add_fill_zone_rectangle(topleft, bottomright, min_thickness, layer, linestart)

    def add_text(self, txt, center_loc, angleCCW=0, scale=0.5, thickness=0.125, linestart='  '):
        self.text.append((txt, center_loc, scale, angleCCW, thickness))
        self.kicad += add_text(txt, center_loc, angleCCW, scale, thickness, linestart)

    def generate_svg(self, outfile: str, save=True, offset_x=0, offset_y=0, default_linewidth=None):
        dwg = svgwrite.Drawing(outfile, profile='tiny')
        for p1, p2, color, linewidth in self.lines:
            p1mod = (p1[0] + offset_x, p1[1] + offset_y)
            p2mod = (p2[0] + offset_x, p2[1] + offset_y)
            if default_linewidth is not None:
                linewidth = default_linewidth
            dwg.add(dwg.line(p1mod, p2mod,
                             stroke=svgwrite.rgb(color[0], color[1], color[2]),
                             stroke_width=linewidth))
        if save:
            dwg.save()
        return dwg

    def generate_dxf(self, outfile: str, version='R2010', save=True, offset_x=0, offset_y=0):
        doc = ezdxf.new(version)
        msp = doc.modelspace()  # add new entities to the modelspace
        doc.layers.new(name='TOP', dxfattribs={'lineweight': 0.0254, 'color': 1})

        # for p1, p2, color, linewidth in self.lines:
        #     # line = msp.add_line(p1, p2, dxfattribs={'lineweight': linewidth})  # linewidth doesn't work
        #     line = msp.add_line(p1, p2, dxfattribs={'layer': 'TOP'})
        #     # line.rgb = color

        for p1, p2, color, linewidth in self.lines_dxf:
            p1mod = (p1[0] + offset_x, p1[1] + offset_y)
            p2mod = (p2[0] + offset_x, p2[1] + offset_y)
            line = msp.add_line(p1mod, p2mod, dxfattribs={'layer': 'TOP'})
        for center, radius, start_angle, end_angle in self.circles_dxf:
            centermod = (center[0] + offset_x, center[1] + offset_y)
            circle = msp.add_arc(center=centermod, radius=radius,
                                 start_angle=np.rad2deg(start_angle), end_angle=np.rad2deg(end_angle),
                                 is_counter_clockwise=end_angle >= start_angle, dxfattribs={'layer': 'TOP'})
        for polygon in self.polygons:
            poly = msp.add_polyline2d(polygon, close=True, dxfattribs={'layer': 'TOP'})
        for text in self.text:
            txt, center_loc, scale, angleCCW, thickness = text
            msp.add_text(txt, dxfattribs={'rotation': angleCCW, 'height': scale, 'width': thickness/0.125,
                                          'halign': 4, 'valign': 2})  # halign = 4 = Middle

        if save:
            doc.saveas(outfile)
        return doc

    def generate_stl(self, outfile: str, save=True):
        pass

    def generate_kicad_script(self, outfile: str, save=True):
        if save:
            with open(outfile, 'w') as f:
                f.write(self.kicad + add_footer())
        return self.kicad + add_footer()
