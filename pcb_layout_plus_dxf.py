from settings import *
from math import cos, sin, pi
import numpy as np
import svgwrite
import ezdxf
import ezdxf.units
from pattern import *
import pcb_layout
from shapely.geometry import Polygon
from shapely.ops import unary_union


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
        self.graphic_polygons = []
        self.m2 = []
        self.pin_headers = []
        self.vias = []
        self.text = []
        self.teensys = []
        self.A05P5s = []
        self.resistors_1206 = []
        self.STB12NM60Ns = []
        self.extras = ""  # Extra items to add to end of layout file
        # self.kicad = ""  # text that gets written into the KiCAD file
        #
        # self.kicad += pcb_layout.add_header()

    def add_trace(self, pts, width, net, layer="F.Cu", cut=False, etch=False):
        """
        Adds a trace with sharp edges to the layout
        :param pts: List of points
        :param width: Width of trace (ignored in DXF)
        :param layer: Trace layer
        :return: None
        """
        net_info = net.split(" ")
        net_number = int(net_info[0])
        # net_name = net_info[1]
        self.traces += [(pts, width, net_number, layer, cut, etch)]
        return pts

    def add_trace_rounded(self, pts, width, radius, n, net, layer="F.Cu", cut=False, etch=False):
        """
        Adds a trace with rounded edges to the layout. Curved edges are generated using quadratic Bezier curves.
        :param pts: List of points
        :param width: Width of trace (ignored in DXF)
        :param radius: Rounding radius
        :param n: The number of straight line segments to cut the arc into. 1 implies a straight line.
        :param layer: Trace layer
        :return: None
        """
        rounded_pts = Pattern.generate_rounded_curve(pts, radius, n)
        return self.add_trace(rounded_pts, width, net, layer, cut, etch)

    def add_fill_zone_polygon(self, pts, net, min_thickness=0.01, layer="F.Cu", cut=False, etch=True):
        """
        Add fill zone
        In KiCad, click Place > Zone, then right click inside a zone > Zone > Fill All to fill the zone
        :param pts: Points to make up the polygon
        :param min_thickness: Minimum polygon thickness
        :param layer: Polygon layer
        :return: The input points (might be useful for some functions that preprocess the points beforehand)
        """
        net_info = net.split(" ")
        net_number = int(net_info[0])
        net_name = net_info[1]
        self.polygons += [(pts, min_thickness, layer, net_number, net_name, cut, etch)]
        return pts

    def add_fill_zone_rounded_polygon(self, pts, net, min_thickness=0.01, layer="F.Cu", n=4, cut=False, etch=True):
        """
        Add fill zone
        In KiCad, click Place > Zone, then right click inside a zone > Zone > Fill All to fill the zone
        :param pts: Points to make up the polygon
        :param min_thickness: Minimum polygon thickness
        :param layer: Polygon layer
        :return: None
        """
        raise NotImplementedError
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

        return self.add_fill_zone_polygon(rounded_pts, net, min_thickness, layer, cut, etch)

    def add_fill_zone_rectangle(self, topleft, bottomright, net, layer="F.Cu", cut=False, etch=True):
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
        return self.add_fill_zone_polygon(pts, layer=layer, net=net, cut=cut, etch=etch)

    def add_fill_zone_rounded_rectangle(self, topleft, bottomright, corner_radius, net, n=4, layer="F.Cu", cut=False,
                                        etch=True):
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
        return self.add_fill_zone_polygon(pts, layer=layer, net=net, cut=cut, etch=etch)

    def add_graphic_line(self, pts, layer="Edge.Cuts", cut=True, etch=True):
        """
        Adds a graphic line
        :param pts: Points that make up the graphic line
        :param layer: Graphic layer (usually either Edge.Cuts or Eco.User2)
        :return: None
        """
        self.graphic_lines += [(pts, layer, cut, etch)]
        self.graphic_polygons += [(pts, pcb_layout.EDGECUT_WIDTH, layer, cut, etch)]

    def add_graphic_arc(self, center, radius, start_angle, end_angle, layer="Edge.Cuts", cut=True, etch=True, N=5):
        """
        Adds a graphic arc (only good for graphic layers, like Edge.Cuts)
        :param center: Center of arc
        :param radius: Radius of arc
        :param start_angle: Start angle of arc (radians, CCW from +x axis)
        :param end_angle: End angle of arc (radians, CCW from +x axis)
        :param layer: Trace layer
        :return: None
        """
        self.graphic_arcs += [(center, radius, start_angle, end_angle, layer, cut, etch)]

        pts = [(center[0] + radius*np.cos(angle), center[1] + radius*np.sin(angle))
               for angle in np.linspace(start_angle, end_angle, N)]
        self.graphic_polygons += [(pts, pcb_layout.EDGECUT_WIDTH, layer, cut, etch)]

    def add_graphic_polygon(self, pts, width=0.1, layer="F.Mask", cut=False, etch=False):
        """
        Adds a graphic polygon (only good for graphic layers, like F.Mask)
        :param pts: Corners of the polygon
        :param width: Width of the lines
        :param layer: Polygon layer
        :return: None
        """
        self.graphic_polygons += [(pts, width, layer, cut, etch)]

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

    def add_M2_drill(self, center, plated, cut=True, etch=False):
        """
        Adds an M2 drill to the layout
        :param center: Center of the M2 drill
        :param plated: Whether the M2 drill is plated or not
        :return: None
        """
        self.m2 += [(center, plated)]
        self.graphic_arcs_dxf += [(center, pcb_layout.M2_HOLE_DIAMETER/2, 0, 2*np.pi, "Edge.Cuts", cut, False)]
        if plated:
            self.graphic_arcs_dxf += [(center, 3.8/2, 0, 2*np.pi, "F.Cu", False, etch)]
            self.graphic_arcs_dxf += [(center, 3.8/2, 0, 2*np.pi, "B.Cu", False, etch)]

    def add_pin_header(self, top_left_pt, nx=1, ny=1, spacing=2.54, net_names=(), references=(), ref_loc=(-2.25, 0),
                       linestart='  ', cut=True, etch=False):
        """
        Add a pin header to the layout
        :param top_left_pt: The top left corner of the pin header (before rotation)
        :param nx: # of pins in the x direction
        :param ny: # of pins in the y direction
        :param spacing: Spacing between pins (mm)
        :param net_names: Net names for each pin
        :param references: Text to write below each pin header pin (only for single pin header)
        :param linestart: Line start
        :return: None
        """
        self.pin_headers += [(top_left_pt, nx, ny, spacing, net_names, references, ref_loc)]
        for n in range(nx*ny):
            center = (top_left_pt[0] + spacing*(n%nx), top_left_pt[1] + spacing*(n//nx))
            self.graphic_arcs_dxf += [(center, 1/2, 0, 2*np.pi, "Edge.Cuts", cut, False)]
            self.graphic_arcs_dxf += [(center, 1.7/2, 0, 2*np.pi, "F.Cu", False, etch)]

    def add_via(self, center_pt, size=0.8, drill=0.4, net="1 main", layers=("F.Cu", "B.Cu"), cut=True, etch=True):
        """
        Add a via to the layout
        :param center_pt: Center of the via
        :param size: Outer size of the via (plated radius)
        :param drill: Drill size of the via
        :param layers: Layers to intersect
        :return: None
        """
        net_info = net.split(" ")
        net_number = int(net_info[0])
        # net_name = net_info[1]
        self.vias += [(center_pt, size, drill, layers, net_number)]
        self.graphic_arcs_dxf += [(center_pt, size/2, 0, 2*np.pi, layers[0], False, etch)]
        self.graphic_arcs_dxf += [(center_pt, size/2, 0, 2*np.pi, layers[1], False, etch)]
        self.graphic_arcs_dxf += [(center_pt, drill/2, 0, 2*np.pi, "Edge.Cuts", cut, False)]

    def add_STB12NM60N(self, center_pt, angle, net_drain, net_source, net_gate, reference):
        """
        Adds a STB12NM60N high-voltage transistor to the board layout
        :param center_pt: Center of transistor layout
        :param angle: Angle (CCW from +x axis, degrees)
        :param net_drain: Net description of the drain (pad 2). Usually "6 "Net-(Q1-Pad2)""
        :param net_source: Net description of the source (pad 3). Usually "2 /GND"
        :param net_gate: Net description of the gate (pad 1). Usually "5 "Net-(Q1-Pad1)""
        :return: KiCAD description (string)
        """
        self.STB12NM60Ns += [(center_pt, angle, net_drain, net_source, net_gate, reference)]

    def add_resistor_1206(self, center_pt, angle, reference, net1, net2, value):
        """
        Add resistor with 1206 layout (12mm x 6 mm)
        :param center_pt: Center of resistor
        :param angle: Angle of component (CCW from +x axis, degrees)
        :param linestart: Formatting start of line
        :return: KiCAD description
        """
        self.resistors_1206 += [(center_pt, angle, reference, net1, net2, value)]

    def add_A05P5(self, center_pt, angle, reference, net_Vin_plus, net_Vin_minus, net_Vctrl, net_Vout_plus,
                  net_Vout_minus, value="A05P-5"):
        """
        Adds the A05P-5 DC-DC converter
        :param center_pt:
        :param angle:
        :param reference: Usually PSx (PS1)
        :param net_Vin_plus: Net description of the Vin+ pin (pin 1). Usually 0-5V. Formatted as "4 /Vin_HV1"
        :param net_Vin_minus: Net description of the Vin- pin (pin 2). Usually GND. Formatted as "2 /GND"
        :param net_Vctrl: Net description of the Vctrl pin (pin 5). 0-Vin_plus. Formatted as "1 /CTRL_HV1"
        :param net_Vout_plus: Net description of the Vout+ pin (pin 3). 0-500V. Formatted as "3 /HV1"
        :param net_Vout_minus: Net description of the Vout- pin (pin 4). Usually GND. Formatted as "2 /GND"
        :param value: Usually A05P-5
        :return: KiCAD description
        """
        self.A05P5s += [(center_pt, angle, reference, net_Vin_plus, net_Vin_minus, net_Vctrl, net_Vout_plus,
                         net_Vout_minus, value)]

    def add_teensy41(self, center_pt, angle, reference, net_names, value="Teensy4.1"):
        """
        Adds a Teensy 4.1 to the layout
        :param center_pt:
        :param angle: Angle (CCW from +x axis, degrees) (default = horizontal, USB to left)
        :param reference:
        :return:
        """
        self.teensys += [(center_pt, angle, reference, net_names, value)]

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
    def merge_overlapping_polygons(polygons):
        """
        Merge overlapping polygons
        :param polygons: A list of lists of points (List[List[Tuple]]), representing a list of polygons
        :return:
        """
        polygons2 = [Polygon(pts) for pts in polygons]
        return list(unary_union(polygons2).exterior.coords)

    ############################################################################################################
    # Convert the PCB object to desired file format
    ############################################################################################################
    def generate_kicad(self, outfile: str, save=True, offset_x=0, offset_y=0, net_names=("main",), net_classes=(0,),
                       default_clearance=pcb_layout.BOARD_EDGE_SPACING_EFF, default_linewidth=pcb_layout.LINESPACE,
                       power_clearance=pcb_layout.BOARD_EDGE_SPACING_EFF, power_linewidth=0.5):
        """
        Generates the KiCAD script for the PCBPattern object
        :param outfile: File location to save the KiCAD script to (should end in .kicad_pcb)
        :param save: True if you want to overwrite the KiCAD file
        :param offset_x: Offset_x to all points
        :param offset_y: Offset_y to all points
        :param net_names: A list of the names of all nets, in the order they should appear in the file
        :param net_classes: A list of the net classes of each net. 0 = Default net, 1 = Power net.
        :param default_clearance:
        :param default_linewidth:
        :param power_clearance:
        :param power_linewidth:
        :return: KiCAD script
        """
        out = pcb_layout.add_header(net_names=net_names, net_classes=net_classes, default_clearance=default_clearance,
                                    default_linewidth=default_linewidth, power_clearance=power_clearance,
                                    power_linewidth=power_linewidth)

        for pts, width, net_number, layer, cut, etch in self.traces:
            out += pcb_layout.add_trace(Pattern.offset_xy(pts, offset_x, offset_y), width, net_number=net_number,
                                        layer=layer)
        for pts, min_thickness, layer, net_number, net_name, cut, etch in self.polygons:
            out += pcb_layout.add_fill_zone_polygon(Pattern.offset_xy(pts, offset_x, offset_y), min_thickness, layer,
                                                    net_number, net_name)
        for pts, layer, cut, etch in self.graphic_lines:
            out += pcb_layout.add_boundary(Pattern.offset_xy(pts, offset_x, offset_y), layer)
        for center, radius, start_angle, end_angle, layer, cut, etch in self.graphic_arcs:
            out += pcb_layout.add_arc(Pattern.offset_xy(center, offset_x, offset_y), radius, start_angle, end_angle, layer)
        for center, plated, cut, etch in self.m2:
            if plated:
                out += pcb_layout.add_M2_drill_plated(Pattern.offset_xy(center, offset_x, offset_y))
            else:
                out += pcb_layout.add_M2_drill_nonplated(Pattern.offset_xy(center, offset_x, offset_y))
        for top_left_pt, nx, ny, spacing, net_names, references, ref_loc, cut, etch in self.pin_headers:
            if nx == ny == 1:
                net_name = net_names if type(net_names) == str else net_names[0]
                reference = references if type(references) == str else references[0]
                out += pcb_layout.add_pin_header_single(Pattern.offset_xy(top_left_pt, offset_x, offset_y),
                                                        net_name=net_name, reference=reference, ref_loc=ref_loc)
            else:
                out += pcb_layout.add_pin_header(Pattern.offset_xy(top_left_pt, offset_x, offset_y), nx, ny, spacing,
                                                 net_names)
        for pt, size, drill, layers, net_number in self.vias:
            out += pcb_layout.add_via(Pattern.offset_xy(pt, offset_x, offset_y), size, drill, layers, net_number)
        for center_pt, angle, net_drain, net_source, net_gate, reference in self.STB12NM60Ns:
            out += pcb_layout.add_STB12NM60N(Pattern.offset_xy(center_pt, offset_x, offset_y), angle, net_drain,
                                             net_source, net_gate, reference)
        for center_pt, angle, reference, net1, net2, value in self.resistors_1206:
            out += pcb_layout.add_resistor_1206(Pattern.offset_xy(center_pt, offset_x, offset_y), angle, reference, net1,
                                                net2, value)
        for center_pt, angle, reference, net_Vin_plus, net_Vin_minus, net_Vctrl, net_Vout_plus, net_Vout_minus, value in self.A05P5s:
            out += pcb_layout.add_A05P5(Pattern.offset_xy(center_pt, offset_x, offset_y), angle, reference, net_Vin_plus,
                                        net_Vin_minus, net_Vctrl, net_Vout_plus, net_Vout_minus, value)
        for center_pt, angle, reference, net_names, value in self.teensys:
            out += pcb_layout.add_teensy41(Pattern.offset_xy(center_pt, offset_x, offset_y), angle, reference, net_names,
                                           value)
        out += self.extras

        out += pcb_layout.add_footer()

        if save:
            with open(outfile, 'w') as f:
                f.write(out)
        else:
            print(out)

    def generate_dxf(self, cut_outfile: str, etch_outfile: str, cut_layers=("Edge.Cuts",), etch_layers=("F.Cu",),
                     version='R2010', save_cut=True, save_etch=True, offset_x=0, offset_y=0, include_traces_etch=False,
                     merge_overlapping_polygons=("F.Cu", "B.Cu")):
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
        :return: DXF file
        """
        doc_cut = ezdxf.new(version)
        msp_cut = doc_cut.modelspace()  # add new entities to the modelspace
        doc_cut.layers.new(name='TOP', dxfattribs={'lineweight': 0.0254})
        doc_etch = ezdxf.new(version)
        msp_etch = doc_etch.modelspace()  # add new entities to the modelspace
        doc_etch.layers.new(name='TOP', dxfattribs={'lineweight': 0.0254})

        def add_line(msp, p1, p2):
            return msp.add_line(Pattern.offset_xy(p1, offset_x, offset_y),
                                Pattern.offset_xy(p2, offset_x, offset_y), dxfattribs={'layer': 'TOP'})

        def add_lines(msp, pts):
            return [add_line(msp, pts[i], pts[i + 1]) for i in range(len(pts) - 1)]

        def add_arc(msp, center, radius, start_angle, end_angle):
            centermod = Pattern.offset_xy(center, offset_x, offset_y)
            if start_angle != 0 or end_angle != 2*np.pi:
                circle = msp.add_arc(center=centermod, radius=radius,
                               start_angle=np.rad2deg(start_angle), end_angle=np.rad2deg(end_angle),
                               is_counter_clockwise=end_angle >= start_angle, dxfattribs={'layer': 'TOP'})
            else:
                circle = msp.add_circle(center=centermod, radius=radius, dxfattribs={'layer': 'TOP'})
            return circle

        def add_polygon(msp, pts, closed=True):
            return msp.add_polyline2d(pts, close=closed, dxfattribs={'layer': 'TOP'})

        # Merge all the graphic polygons
        merged_polygons = {layer: [[]] for layer in merge_overlapping_polygons}

        # Process all the other data types
        for pts, width, net_number, layer, cut, etch in self.traces:
            if layer not in merge_overlapping_polygons:
                if layer in cut_layers and cut:
                    add_lines(msp_cut, pts)
                if layer in etch_layers and (etch and include_traces_etch):
                    add_lines(msp_etch, Pattern.offset_trace(pts, width))
            else:
                merged_polygons[layer][0] += [Polygon(Pattern.offset_trace(pts, width))]
                merged_polygons[layer][1:] = [cut, etch]
        for pts, min_thickness, layer, net_number, net_name, cut, etch in self.polygons:
            if layer not in merge_overlapping_polygons:
                if layer in cut_layers and cut:
                    add_polygon(msp_cut, pts + [pts[0]], False)
                if layer in etch_layers and etch:
                    # add_polygon(msp_etch, pts, False)
                    add_lines(msp_etch, pts + [pts[0]])
            else:
                merged_polygons[layer][0] += [Polygon(pts)]
                merged_polygons[layer][1:] = [cut, etch]
        for pts, layer, cut, etch in self.graphic_lines:
            if layer not in merge_overlapping_polygons:
                if layer in cut_layers and cut:
                    add_lines(msp_cut, pts)
                if layer in etch_layers and etch:
                    add_lines(msp_etch, pts)
            else:
                merged_polygons[layer][0] += [Polygon(pts)]
                merged_polygons[layer][1:] = [cut, etch]
        for center, radius, start_angle, end_angle, layer, cut, etch in self.graphic_arcs:
            if layer not in merge_overlapping_polygons:
                if layer in cut_layers and cut:
                    add_arc(msp_cut, center, radius, start_angle, end_angle)
                if layer in etch_layers and etch:
                    add_arc(msp_etch, center, radius, start_angle, end_angle)
            else:
                pts = [(center[0] + radius*np.cos(angle), center[1] + radius*np.sin(angle)) for angle in
                       np.linspace(start_angle, end_angle, 10)]
                merged_polygons[layer][0] += [Polygon(pts)]
                merged_polygons[layer][1:] = [cut, etch]
        for center, radius, start_angle, end_angle, layer, cut, etch in self.graphic_arcs_dxf:
            if layer not in merge_overlapping_polygons:
                if layer in cut_layers and cut:
                    add_arc(msp_cut, center, radius, start_angle, end_angle)
                if layer in etch_layers and etch:
                    add_arc(msp_etch, center, radius, start_angle, end_angle)
            else:
                pts = [(center[0] + radius*np.cos(angle), center[1] + radius*np.sin(angle)) for angle in
                       np.linspace(start_angle, end_angle, 10)]
                merged_polygons[layer][0] += [Polygon(pts)]
                merged_polygons[layer][1:] = [cut, etch]

        # Handle merged polygons
        print("Original polygons", merged_polygons)
        for layer in merge_overlapping_polygons:
            polygons = merged_polygons[layer]
            if len(polygons) > 1:
                print("Original polygons: Layer =", layer, ", Cut =", polygons[1], ", Etch =", polygons[2])
                polygons = polygons[0]
                # for polygon in polygons:
                #     print("Polygon pts =", list(polygon.exterior.coords))
                if len(polygons) != 0:
                    print(polygons)
                    merged = unary_union(polygons)
                    if type(merged) == Polygon:
                        merged_polygons[layer][0] = [merged]
                    else:  # MultiplePolygon
                        merged_polygons[layer][0] = list(merged.geoms)
                else:
                    merged_polygons.pop(layer)
            else:
                print("No polygons on layer", layer)
                merged_polygons.pop(layer)
        print("---------------------")
        # Add merged polygons
        for layer, info in merged_polygons.items():
            polygons, cut, etch = info
            print("Merged polygons: Layer =", layer, ", Cut =", cut, ", Etch =", etch)
            for polygon in polygons:
                pts = list(polygon.exterior.coords)
                # print("Polygon pts =", pts)
                if layer in cut_layers and cut:
                    add_polygon(msp_cut, pts + [pts[0]], False)
                if layer in etch_layers and etch:
                    add_lines(msp_etch, pts + [pts[0]])

        if save_cut:
            doc_cut.saveas(cut_outfile)
        if save_etch:
            doc_etch.saveas(etch_outfile)
        return doc_cut, doc_etch
