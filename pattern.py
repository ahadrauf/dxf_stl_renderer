from settings import *
from math import cos, sin, pi
import numpy as np
import svgwrite
import ezdxf
import ezdxf.units


class Pattern:
    def __init__(self, setting=LaserCutter):
        self.setting = setting
        self.lines = []
        self.lines_dxf = []
        self.circles_dxf = []
        self.polygons = []
        self.text = []

    def add_line(self, p1, p2, kerf=None, n=4, mode=LaserCutter.CUT, update_dxf=True):
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
            self.add_arc(center=p2mid, radius=kerf, n=n, start_angle=theta + np.pi/2, end_angle=theta - np.pi/2,
                         mode=mode)
            self.lines.append((p2bot, p1bot, color, linewidth))
            self.lines_dxf.append((p2bot, p1bot, color, linewidth))
            self.add_arc(center=p1mid, radius=kerf, n=n, start_angle=theta - np.pi/2, end_angle=theta - 3*np.pi/2,
                         mode=mode)

    def add_lines(self, points, kerf=None, n=4, mode=LaserCutter.CUT, update_dxf=True):
        for i in range(len(points) - 1):
            self.add_line(points[i], points[i + 1], kerf, n, mode, update_dxf)

    def add_circle(self, center, radius, n=6, mode=LaserCutter.CUT) -> None:
        self.add_arc(center, radius, n, start_angle=0, end_angle=2*np.pi, mode=mode)

    def add_arc(self, center, radius, n=6, start_angle=0, end_angle=2*np.pi, mode=LaserCutter.CUT) -> None:
        theta_range = np.linspace(start_angle, end_angle, n)
        for i in range(n - 1):
            theta = theta_range[i]
            theta_next = theta_range[i + 1]
            p1 = (center[0] + radius*np.cos(theta), center[1] + radius*np.sin(theta))
            p2 = (center[0] + radius*np.cos(theta_next), center[1] + radius*np.sin(theta_next))
            self.add_line(p1, p2, mode=mode, update_dxf=False)
        self.circles_dxf.append((center, radius, start_angle, end_angle))

    def add_rectangle(self, topleft, bottomright, mode=LaserCutter.CUT) -> None:
        x1, y1 = topleft
        x2, y2 = bottomright
        color = self.setting.COLOR[mode]
        linewidth = self.setting.LINEWIDTH[mode]
        self.polygons.append([[(x1, y1), (x1, y2), (x2, y2), (x2, y1)], color, linewidth])

    def add_text(self, pos, text, font_size=10, align="MIDDLE_CENTER"):
        self.text.append((pos, text, font_size, align))

    ################## Helper Functions ######################
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

    @staticmethod
    def generate_rounded_curve(pts, radius, n):
        """
        Generates a rounded curve based around the points pts
        :param pts: List of points
        :param radius: Rounding radius
        :param n: The number of straight line segments to cut the arc into. 1 implies a straight line.
        :return: None
        """
        angles = []
        for i in range(len(pts) - 1):
            angles += [np.arctan2(pts[i + 1][1] - pts[i][1], pts[i + 1][0] - pts[i][0])]

        rounded_pts = []
        curr = np.array(pts[0])
        for i in range(len(pts) - 2):
            theta = angles[i]
            p0 = np.array(pts[i + 1]) - radius*np.array([np.cos(theta), np.sin(theta)])
            p1 = np.array(pts[i + 1])
            theta_nxt = angles[i + 1]
            p2 = np.array(pts[i + 1]) + radius*np.array([np.cos(theta_nxt), np.sin(theta_nxt)])

            # Create Bezier curve
            bezier_pts = Pattern.quadratic_bezier_curve(p0, p1, p2, n + 2)  # n+2 including the start/end points

            # Add line segment + curve
            rounded_pts += [curr, p0]
            rounded_pts += bezier_pts[1:-1]  # omit the start/end points
            curr = p2
        rounded_pts += [curr, pts[-1]]  # Add the last straight line segment
        return rounded_pts

    @staticmethod
    def offset_xy(pts, offset_x, offset_y):
        """
        Offsets the list of points by adding offset_x and offset_y
        :param pts: List of points
        :param offset_x: Offset in the x direction to add
        :param offset_y: Offset in the y direction to add
        :return: List of shifted points
        """
        if np.issubdtype(type(pts[0]), np.number):  # if the pts field is just a single point
            return (pts[0] + offset_x, pts[1] + offset_y)
        return [(pt[0] + offset_x, pt[1] + offset_y) for pt in pts]

    @staticmethod
    def offset_trace(pts, w, round_ends=False):
        """
        Offsets a trace centered at the given points by its width w/2 on either side. Returns a closed curve.
        This method isn't particularly robust, and will likely fail on obtuse angles.
        :param pts: Center points of the trace
        :param w: Width of the trace (output offset by w/2 on either side)
        :return: A closed curve that encloses the offset trace
        """
        angles = []
        for i in range(len(pts) - 1):
            angles += [np.arctan2(pts[i + 1][1] - pts[i][1], pts[i + 1][0] - pts[i][0])]

        left_pts = []
        right_pts = []

        # Add the first point
        theta = angles[0]
        pt = pts[0]
        left_pts.append((pt[0] - w/2*np.sin(theta), pt[1] + w/2*np.cos(theta)))
        right_pts.append((pt[0] + w/2*np.sin(theta), pt[1] - w/2*np.cos(theta)))

        # Add the remaining points
        for i in range(len(pts) - 1):
            theta = angles[i]
            pt = pts[i + 1]
            left_pts.append((pt[0] - w/2*np.sin(theta), pt[1] + w/2*np.cos(theta)))
            right_pts.append((pt[0] + w/2*np.sin(theta), pt[1] - w/2*np.cos(theta)))

        # Add end caps if desired
        endcap1 = [left_pts[0]]
        endcap2 = []
        if round_ends:
            N = 6
            theta_rng = np.linspace(angles[0] + 3*np.pi/2, angles[0] + np.pi/2, N)
            center = pts[0]
            endcap1 = [(center[0] + w/2*np.cos(theta), center[1] + w/2*np.sin(theta)) for theta in theta_rng]
            theta_rng = np.linspace(angles[-1] - np.pi/2, angles[-1] + np.pi/2, N)
            center = pts[-1]
            endcap2 = [(center[0] + w/2*np.cos(theta), center[1] + w/2*np.sin(theta)) for theta in theta_rng]

        # Construct the closed polygon
        return left_pts + endcap2 + list(reversed(right_pts)) + endcap1

    ################## Generate Files ########################
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
        for pts, color, linewidth in self.polygons:
            if default_linewidth is not None:
                linewidth = default_linewidth
            for i in range(len(pts)):
                p1mod = (pts[i][0] + offset_x, pts[i][1] + offset_y)
                nxt = 0 if i == len(pts) - 1 else i + 1
                p2mod = (pts[nxt][0] + offset_x, pts[nxt][1] + offset_y)
                print(p1mod, p2mod)
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
            if start_angle != 0 or end_angle != 2*np.pi:
                circle = msp.add_arc(center=centermod, radius=radius,
                                     start_angle=np.rad2deg(start_angle), end_angle=np.rad2deg(end_angle),
                                     is_counter_clockwise=end_angle >= start_angle, dxfattribs={'layer': 'TOP'})
            else:
                circle = msp.add_circle(center=centermod, radius=radius, dxfattribs={'layer': 'TOP'})
        for pts, color, linewidth in self.polygons:
            poly = msp.add_polyline2d(pts, close=True, dxfattribs={'layer': 'TOP'})

        if save:
            doc.saveas(outfile)
        return doc

    def generate_stl(self, outfile: str, save=True):
        pass
