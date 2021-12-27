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
        self.polygons = []
        self.graphic_lines = []
        self.graphic_arcs = []
        self.graphic_arcs_dxf = []  # for M2 etch/cut boundaries
        self.m2 = []
        self.pin_headers = []
        self.vias = []
        self.text = []
        self.extras = ""  # Extra items to add to end of layout file
        # self.kicad = ""  # text that gets written into the KiCAD file
        #
        # self.kicad += pcb_layout.add_header()

    def add_trace(self, pts, width, layer="F.Cu"):
        """
        Adds a trace with sharp edges to the layout
        :param pts: List of points
        :param width: Width of trace (ignored in DXF)
        :param layer: Trace layer
        :return: None
        """
        self.traces += [(pts, width, layer)]

    def add_trace_rounded(self, pts, width, radius, n, layer="F.Cu"):
        """
        Adds a trace with rounded edges to the layout. Curved edges are generated using quadratic Bezier curves.
        :param pts: List of points
        :param width: Width of trace (ignored in DXF)
        :param radius: Rounding radius
        :param n: The number of straight line segments to cut the arc into. 1 implies a straight line.
        :param layer: Trace layer
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
            bezier_pts = self.quadratic_bezier_curve(p0, p1, p2, n + 2)  # n+2 including the start/end points

            # Add line segment + curve
            rounded_pts += [curr, p0]
            rounded_pts += bezier_pts[1:-1]  # omit the start/end points
            curr = p2
        rounded_pts += [curr, pts[-1]]  # Add the last straight line segment
        return self.add_trace(rounded_pts, width, layer)

    def add_fill_zone_polygon(self, pts, min_thickness=0.01, layer="F.Cu"):
        """
        Add fill zone
        In KiCad, click Place > Zone, then right click inside a zone > Zone > Fill All to fill the zone
        :param pts: Points to make up the polygon
        :param min_thickness: Minimum polygon thickness
        :param layer: Polygon layer
        :return: None
        """
        self.polygons += [(pts, min_thickness, layer)]

    def add_fill_zone_rectangle(self, topleft, bottomright, layer="F.Cu"):
        """
        Adds fill zone as a rectangle
        :param topleft: Top left corner of the rectangle
        :param bottomright: Bottom right corner of the rectangle
        :param layer: Polygon layer
        :return: None
        """
        x1, y1 = topleft
        x2, y2 = bottomright
        pts = [(x1, y1), (x1, y2), (x2, y2), (x2, y1)]
        return self.add_fill_zone_polygon(pts, layer=layer)

    def add_fill_zone_rounded_rectangle(self, topleft, bottomright, corner_radius, n=4, layer="F.Cu"):
        """
        Adds fill zone as a rounded rectangle
        :param topleft: Top left corner of the rectangle
        :param bottomright: Bottom right corner of the rectangle
        :param corner_radius: Radius of curvature of the corner
        :param n: Number of points in the rounded corners
        :param layer: Polygon layer
        :return: None
        """
        x1, y1 = topleft
        x2, y2 = bottomright
        x, y = min(x1, x2), min(y1, y2)
        width, height = abs(x1 - x2), abs(y1 - y2)
        pts = [(x + corner_radius, y), (x + width - corner_radius, y)]
        pts += [(x + width - corner_radius*(1 - np.sin(theta)), y + corner_radius*(1 - np.cos(theta)))
                for theta in np.linspace(0., np.pi/2, n)]
        pts += [(x + width, y + corner_radius), (x + width, y + height - corner_radius)]
        pts += [
            (x + width - corner_radius*(1 - np.cos(theta)), y + height - corner_radius*(1 - np.sin(theta)))
            for theta in np.linspace(0., np.pi/2, n)]
        pts += [(x + width - corner_radius, y + height), (x + corner_radius, y + height)]
        pts += [(x + corner_radius*(1 - np.sin(theta)), y + height - corner_radius*(1 - np.cos(theta)))
                for theta in np.linspace(0., np.pi/2, n)]
        pts += [(x, y + height - corner_radius), (x, y + corner_radius)]
        pts += [(x + corner_radius*(1 - np.cos(theta)), y + corner_radius*(1 - np.sin(theta)))
                for theta in np.linspace(0., np.pi/2, n)]
        return self.add_fill_zone_polygon(pts, layer=layer)

    def add_graphic_line(self, pts, layer="Edge.Cuts"):
        """
        Adds a graphic line
        :param pts: Points that make up the graphic line
        :param layer: Graphic layer (usually either Edge.Cuts or Eco.User2)
        :return: None
        """
        self.graphic_lines += [(pts, layer)]

    def add_graphic_arc(self, center, radius, start_angle, end_angle, layer="Edge.Cuts"):
        """
        Adds a graphic arc (only good for graphic layers, like Edge.Cuts)
        :param center: Center of arc
        :param radius: Radius of arc
        :param start_angle: Start angle of arc (radians, CCW from +x axis)
        :param end_angle: End angle of arc (radians, CCW from +x axis)
        :param layer: Trace layer
        :return: None
        """
        self.graphic_arcs += [(center, radius, start_angle, end_angle, layer)]

    def add_text(self, txt, center_loc, angleCCW=0, scale=0.5, thickness=0.125, layer="F.SilkS"):
        """
        Adds a text object to the desired layer
        :param txt: The text to insert
        :param center_loc: The location of the center of the text
        :param angleCCW: Rotation angle of text (radians, CCW from +x axis)
        :param scale: Scale of text
        :param thickness: Line thickness of text
        :param layer: Layer for text
        :return: None
        """
        self.text += [(txt, center_loc, angleCCW, scale, thickness, layer)]

    def add_M2_drill(self, center, plated):
        """
        Adds an M2 drill to the layout
        :param center: Center of the M2 drill
        :param plated: Whether the M2 drill is plated or not
        :return: None
        """
        self.m2 += [(center, plated)]
        self.graphic_arcs_dxf += [(center, pcb_layout.M2_HOLE_DIAMETER/2, 0, 2*np.pi, "Edge.Cuts")]

    def add_pin_header(self, top_left_pt, nx, ny, spacing=2.54, net_names=(), linestart='  '):
        """
        Add a pin header to the layout
        :param top_left_pt: The top left corner of the pin header (before rotation)
        :param nx: # of pins in the x direction
        :param ny: # of pins in the y direction
        :param spacing: Spacing between pins (mm)
        :param linestart: Line start
        :return: None
        """
        self.pin_headers += [(top_left_pt, nx, ny, spacing, net_names)]
        for n in range(nx*ny):
            center = (top_left_pt[0] + spacing*(n%nx), top_left_pt[1] + spacing*(n//nx))
            self.graphic_arcs_dxf += [(center, pcb_layout.PIN_HEADER_DIAMETER/2, 0, 2*np.pi, "Edge.Cuts")]

    def add_via(self, pt, size=0.8, drill=0.4, layers=("F.Cu", "B.Cu")):
        """
        Add a via to the layout
        :param pt: Center of the via
        :param size: Outer size of the via (plated radius)
        :param drill: Drill size of the via
        :param layers: Layers to intersect
        :return: None
        """
        self.vias += [(pt, size, drill, layers)]

    def add_object(self, desc):
        """
        If you generate a KiCAD script via some other function (e.g. pcb_layout/), you can add it to the end of the file
        via this method
        WARNING: This method won't apply the offset_x and offset_y terms when creating the final PCB. Add your desired
        offset_x and offset_y when generating the object description
        :param desc: The object description
        :return: None
        """
        self.extras += desc

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

    ############################################################################################################
    # Convert the PCB object to desired file format
    ############################################################################################################
    def generate_kicad(self, outfile: str, save=True, offset_x=0, offset_y=0):
        """
        Generates the KiCAD script for the PCBPattern object
        :param outfile: File location to save the KiCAD script to (should end in .kicad_pcb)
        :param save: True if you want to overwrite the KiCAD file
        :param offset_x: Offset_x to all points
        :param offset_y: Offset_y to all points
        :return: KiCAD script
        """
        out = pcb_layout.add_header()

        for pts, width, layer in self.traces:
            out += pcb_layout.add_trace(self.offset_xy(pts, offset_x, offset_y), width, layer)
        for pts, min_thickness, layer in self.polygons:
            out += pcb_layout.add_fill_zone_polygon(self.offset_xy(pts, offset_x, offset_y), min_thickness, layer)
        for pts, layer in self.graphic_lines:
            out += pcb_layout.add_boundary(self.offset_xy(pts, offset_x, offset_y), layer)
        for center, radius, start_angle, end_angle, layer in self.graphic_arcs:
            out += pcb_layout.add_arc(self.offset_xy(center, offset_x, offset_y), radius, start_angle, end_angle, layer)
        for center, plated in self.m2:
            if plated:
                out += pcb_layout.add_M2_drill_plated(self.offset_xy(center, offset_x, offset_y))
            else:
                out += pcb_layout.add_M2_drill_nonplated(self.offset_xy(center, offset_x, offset_y))
        for top_left_pt, nx, ny, spacing, net_names in self.pin_headers:
            out += pcb_layout.add_pin_header(self.offset_xy(top_left_pt, offset_x, offset_y), nx, ny, spacing,
                                             net_names)
        for pt, size, drill, layers in self.vias:
            out += pcb_layout.add_via(self.offset_xy(pt, offset_x, offset_y), size, drill, layers)
        out += self.extras

        out += pcb_layout.add_footer()

        if save:
            with open(outfile, 'w') as f:
                f.write(out)

    def generate_dxf(self, cut_outfile: str, etch_outfile: str,
                     cut_layers=("Edge.Cuts"),
                     etch_layers=("F.Cu"),
                     version='R2010', save=True, offset_x=0, offset_y=0):
        """
        Generates two DXF files for the PCBPattern object
        The first DXF file is for the edge cuts
        The second DXF file is for the areas to etch
        :param cut_outfile: File location to save the cut KiCAD script to (should end in .dxf)
        :param etch_outfile: File location to save the etch KiCAD script to (should end in .dxf)
        :param cut_layers: The layers to add when generating the cut DXF
        :param etch_layers: The layers to add when generating the etch DXF
        :param version: DXF file version. R2010 tends to work well with SolidWorks.
        :param save: True if you want to overwrite the KiCAD file
        :param offset_x: Offset_x to all points
        :param offset_y: Offset_y to all points
        :return: KiCAD script
        """
        doc_cut = ezdxf.new(version)
        msp_cut = doc_cut.modelspace()  # add new entities to the modelspace
        doc_cut.layers.new(name='TOP', dxfattribs={'lineweight': 0.0254})
        doc_etch = ezdxf.new(version)
        msp_etch = doc_etch.modelspace()  # add new entities to the modelspace
        doc_etch.layers.new(name='TOP', dxfattribs={'lineweight': 0.0254})

        def add_line(msp, p1, p2):
            return msp.add_line(self.offset_xy(p1, offset_x, offset_y),
                                self.offset_xy(p2, offset_x, offset_y), dxfattribs={'layer': 'TOP'})

        def add_lines(msp, pts):
            return [add_line(msp, pts[i], pts[i + 1]) for i in range(len(pts) - 1)]

        def add_arc(msp, center, radius, start_angle, end_angle):
            return msp.add_arc(center=self.offset_xy(center, offset_x, offset_y), radius=radius,
                               start_angle=np.rad2deg(start_angle), end_angle=np.rad2deg(end_angle),
                               is_counter_clockwise=end_angle >= start_angle, dxfattribs={'layer': 'TOP'})

        def add_polygon(msp, pts, closed=True):
            return msp.add_polyline2d(pts, close=closed, dxfattribs={'layer': 'TOP'})

        for pts, width, layer in self.traces:
            if layer in cut_layers:
                add_lines(msp_cut, pts)
            # if layer in etch_layers:
            #     add_lines(msp_etch, pts)
        for pts, min_thickness, layer in self.polygons:
            if layer in cut_layers:
                add_polygon(msp_cut, pts + [pts[0]], False)
            if layer in etch_layers:
                # add_polygon(msp_etch, pts, False)
                add_lines(msp_etch, pts + [pts[0]])
        for pts, layer in self.graphic_lines:
            if layer in cut_layers:
                add_lines(msp_cut, pts)
            if layer in etch_layers:
                add_lines(msp_etch, pts)
        for center, radius, start_angle, end_angle, layer in self.graphic_arcs:
            if layer in cut_layers:
                add_arc(msp_cut, center, radius, start_angle, end_angle)
            if layer in etch_layers:
                add_arc(msp_etch, center, radius, start_angle, end_angle)
        for center, radius, start_angle, end_angle, layer in self.graphic_arcs_dxf:
            if layer in cut_layers:
                add_arc(msp_cut, center, radius, start_angle, end_angle)
            if layer in etch_layers:
                add_arc(msp_etch, center, radius, start_angle, end_angle)

        if save:
            doc_cut.saveas(cut_outfile)
            doc_etch.saveas(etch_outfile)
        return doc_cut, doc_etch
