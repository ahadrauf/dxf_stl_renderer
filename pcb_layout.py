import numpy as np
from utils import *


MIL_TO_MM = 0.0254
LINESPACE = 3*MIL_TO_MM  # defined by manufacturer
BOARD_EDGE_SPACING = 7*MIL_TO_MM  # defined by manufacturer

EDGECUT_WIDTH = 0.05  # default in KiCad
BOARD_EDGE_SPACING_EFF = BOARD_EDGE_SPACING + EDGECUT_WIDTH/2  # Since in KiCad, the edge cut has width
M2_HOLE_DIAMETER = 2.2
M2_METAL_DIAMETER = 3.8
M2_COURTYARD_DIAMETER = 2.45*2
PIN_HEADER_DIAMETER = 1.7

NET_NAME = "main"


def add_fill_zone_rectangle(topleft, bottomright, min_thickness=0.01, layer="F.Cu", net_number=1, net_name="main", linestart='  '):
    """
    Add fill zone
    In KiCad, click Place > Zone, then right click inside a zone >
    :param topleft:
    :param bottomright:
    :param min_thickness:
    :param linestart:
    :return:
    """
    x1, y1 = topleft
    x2, y2 = bottomright
    zone = \
"""(zone (net {}) (net_name {}) (layer {}) (tstamp 0) (hatch edge 0.508)
  (connect_pads (clearance {}))
  (min_thickness {})
  (fill yes (arc_segments 32) (thermal_gap 0.508) (thermal_bridge_width 0.508))
  (polygon
    (pts
      (xy {} {}) (xy {} {}) (xy {} {}) (xy {} {})
    )
  )
)""".format(net_number, net_name, layer, BOARD_EDGE_SPACING, LINESPACE/4, x2, y2, x1, y2, x1, y1, x2, y1)
    # print(zone, end='')
    out = ""
    for line in zone.split('\n'):
        out += linestart + line + '\n'
        # print(linestart + line)
    return out


def add_fill_zone_rounded_rectangle(topleft, bottomright, corner_radius, N=10, layer="F.Cu", linestart='  '):
    """
    Add fill zone
    In KiCad, click Place > Zone, then right click inside a zone >
    :param topleft:
    :param bottomright:
    :param min_thickness:
    :param linestart:
    :return:
    """
    x1, y1 = topleft
    x2, y2 = bottomright
    x, y = min(x1, x2), min(y1, y2)
    width, height = abs(x1 - x2), abs(y1 - y2)
    pts = [(x + corner_radius, y), (x + width - corner_radius, y)]
    pts += [(x + width - corner_radius*(1 - np.sin(theta)), y + corner_radius*(1 - np.cos(theta)))
            for theta in np.linspace(0., np.pi/2, N)]
    pts += [(x + width, y + corner_radius), (x + width, y + height - corner_radius)]
    pts += [
        (x + width - corner_radius*(1 - np.cos(theta)), y + height - corner_radius*(1 - np.sin(theta)))
        for theta in np.linspace(0., np.pi/2, N)]
    pts += [(x + width - corner_radius, y + height), (x + corner_radius, y + height)]
    pts += [(x + corner_radius*(1 - np.sin(theta)), y + height - corner_radius*(1 - np.cos(theta)))
            for theta in np.linspace(0., np.pi/2, N)]
    pts += [(x, y + height - corner_radius), (x, y + corner_radius)]
    pts += [(x + corner_radius*(1 - np.cos(theta)), y + corner_radius*(1 - np.sin(theta)))
            for theta in np.linspace(0., np.pi/2, N)]
    return add_fill_zone_polygon(pts, layer=layer, linestart=linestart)


def add_fill_zone_polygon(pts, min_thickness=0.0254, layer="F.Cu", net_number=1, net_name="main", linestart='  '):
    """
    Add fill zone
    In KiCad, click Place > Zone, then right click inside a zone >
    :param pts:
    :param min_thickness:
    :param layer:
    :param linestart:
    :return:
    """
    pts_str = " ".join(["(xy {} {})".format(pt[0], pt[1]) for pt in pts])
    zone = \
"""(zone (net {}) (net_name {}) (layer {}) (tstamp 0) (hatch edge 0.508)
  (connect_pads (clearance {}))
  (min_thickness {})
  (fill yes (arc_segments 32) (thermal_gap 0.508) (thermal_bridge_width 0.508))
  (polygon
    (pts
      {}
    )
  )
)""".format(net_number, net_name, layer, max(BOARD_EDGE_SPACING_EFF, min_thickness), LINESPACE/4, pts_str)
    # print(zone, end='')
    out = ""
    for line in zone.split('\n'):
        out += linestart + line + '\n'
        # print(linestart + line)
    return out


def add_boundary(pts, layer="Edge.Cuts", linestart='  '):
    out = ""
    for i in range(len(pts) - 1):
        start = pts[i]
        end = pts[i + 1]
        zone = "(gr_line (start {} {}) (end {} {}) (layer {}) (width 0.05))".format(start[0], start[1],
                                                                                           end[0], end[1],
                                                                                    layer)
        # print(line, end='')
        # print(linestart + zone)
        out += linestart + zone + '\n'
    return out


def add_text(txt, center_loc, angleCCW=0, scale=0.5, thickness=0.125, layer="F.SilkS", linestart='  '):
    zone = \
"""(gr_text "{}" (at {} {} {}) (layer {})
  (effects (font (size {} {}) (thickness {})))
)""".format(txt, center_loc[0], center_loc[1], angleCCW, layer, scale, scale, thickness)
    out = ""
    for line in zone.split('\n'):
        out += linestart + line + '\n'
        # print(linestart + line)
    return out


def add_trace(pts, width=LINESPACE, layer="F.Cu", net_number=1, linestart='  '):
    out = ''
    for i in range(len(pts) - 1):
        start = pts[i]
        end = pts[i + 1]
        zone = "(segment (start {} {}) (end {} {}) (width {}) (layer {}) (net {}))".format(start[0], start[1],
                                                                                          end[0], end[1], width,
                                                                                          layer, net_number)
        # print(linestart + zone)
        out += linestart + zone + '\n'
    return out


def add_arc(center, radius, start_angle, end_angle, layer="Edge.Cuts", linestart='  '):
    end = (center[0] + radius*np.cos(start_angle),
           center[1] + radius*np.sin(start_angle))
    angle = np.rad2deg(end_angle - start_angle)
    zone = "(gr_arc (start {} {}) (end {} {}) (angle {}) (layer {}) (width {}))".format(center[0], center[1],
                                                                                                end[0], end[1],
                                                                                                angle, layer,
                                                                                                EDGECUT_WIDTH)
    # print(linestart + zone)
    return linestart + zone + '\n'

def add_graphic_polygon(pts, width=0.1, layer="F.Mask", linestart='  '):
    pts_str = "(xy {} {}) "
    zone = "(gr_poly (pts (xy 11.811 27.94) (xy 9.017 27.813) (xy 8.763 25.146) (xy 13.208 25.019)) (layer F.Mask) (width 0.1))"
    print("Unimplemented")
    raise NotImplementedError("graphic polygon not implemented yet")


def add_via(pt, size=0.8, drill=0.4, layers=("F.Cu", "B.Cu"), net_number=1, linestart='  '):
    zone = "(via (at {} {}) (size {}) (drill {}) (layers {} {}) (net {}))".format(pt[0], pt[1], size, drill,
                                                                                            layers[0], layers[1],
                                                                                            net_number)
    return linestart + zone + '\n'

def add_M2_drill_nonplated(pt, linestart='  '):
    zone = \
"""(module MountingHole:MountingHole_2.2mm_M2 (layer F.Cu) (tedit 56D1B4CB) (tstamp 61566CFB)
  (at {} {})
  (descr "Mounting Hole 2.2mm, no annular, M2")
  (tags "mounting hole 2.2mm no annular m2")
  (attr virtual)
  (fp_circle (center 0 0) (end 2.2 0) (layer Cmts.User) (width 0.15))
  (fp_circle (center 0 0) (end 2.45 0) (layer F.CrtYd) (width 0.05))
  (pad 1 np_thru_hole circle (at 0 0) (size 2.2 2.2) (drill 2.2) (layers *.Cu *.Mask))
)""".format(pt[0], pt[1])
    out = ""
    for line in zone.split('\n'):
        out += linestart + line + '\n'
    return out

def add_M2_drill_plated(pt, linestart='  '):
    zone = \
"""(module MountingHole:MountingHole_2.2mm_M2 (layer F.Cu) (tedit 56D1B4CB) (tstamp 61566CFB)
  (at {} {})
  (descr "Mounting Hole 2.2mm, no annular, M2")
  (tags "mounting hole 2.2mm no annular m2")
  (attr virtual)
  (fp_circle (center 0 0) (end 2.2 0) (layer Cmts.User) (width 0.15))
  (fp_circle (center 0 0) (end 2.45 0) (layer F.CrtYd) (width 0.05))
  (pad 1 thru_hole circle (at 0 0) (size 3.8 3.8) (drill 2.2) (layers *.Cu *.Mask) (net 1 {}))
)""".format(pt[0], pt[1], NET_NAME)
    out = ""
    for line in zone.split('\n'):
        out += linestart + line + '\n'
    return out
# """
# fp_circle (center 0 0) (end 1.9 0) (layer Cmts.User) (width 0.15))
#     (fp_circle (center 0 0) (end 2.15 0) (layer F.CrtYd) (width 0.05))
#     (pad 1 thru_hole circle (at 0 0) (size 3.8 3.8) (drill 2.2) (layers *.Cu *.Mask))
#     """

def add_pin_header(top_left_pt, nx, ny, spacing=2.54, net_names=(), linestart='  '):
    """
    Add a pin header to the layout
    :param top_left_pt: The top left corner of the pin header
    :param nx: # of pins in the x direction
    :param ny: # of pins in the y direction
    :param spacing: Spacing between pins (mm)
    :param linestart: Line start
    :return: Pin header KiCAD description
    """
    angle = 90 if (nx > ny) else 0
    nx, ny = min(nx, ny), max(nx, ny)
    zone_start = \
"""(module Connector_PinHeader_{:0>1.2f}mm:PinHeader_{}x{:0>2d}_P{:0>1.2f}mm_Vertical (layer F.Cu) (tedit 59FED5CC) (tstamp 61BABEFE)
  (at {} {} {})
  (descr "Through hole straight pin header, {}x{:0>2d}, {:0>1.2f}mm pitch, single row")
  (tags "Through hole pin header THT {}x{:0>2d} {:0>1.2f}mm single row")
""".format(spacing, nx, ny, spacing, top_left_pt[0], top_left_pt[1], angle, nx, ny, spacing, nx, ny, spacing)
    zone_end = \
"""(model ${KISYS3DMOD}/Connector_PinHeader_{:0>1.2f}mm.3dshapes/PinHeader_{}x{:0>2d}_P{:0>1.2f}mm_Vertical.wrl
    (at (xyz 0 0 0))
    (scale (xyz 1 1 1))
    (rotate (xyz 0 0 0))
  )
)""".format(spacing, nx, ny, spacing, KISYS3DMOD="{KISYS3DMOD}")
    def pad(n):
        shape = "rect" if n == 1 else "oval"
        return "  (pad {} thru_hole {} (at {} {} {}) (size 1.7 1.7) (drill 1) (layers *.Cu *.Mask))".format(n, shape,
                                                                                                            spacing*((n-1)%nx),
                                                                                                   spacing*((n-1)//nx),
                                                                                                   angle)
    def pad_with_net_name(n, name):
        shape = "rect" if n == 1 else "oval"
        return "  (pad {} thru_hole {} (at {} {} {}) (size 1.7 1.7) (drill 1) (layers *.Cu *.Mask) (net {}))".format(n, shape,
                                                                                                            spacing*((n - 1)%nx),
                                                                                                            spacing*((n - 1)//nx),
                                                                                                            angle, name)
    out = ""
    for line in zone_start.split('\n'):
        out += linestart + line + '\n'
    if len(net_names) == 0:
        for n in reversed(range(1, nx*ny + 1)):
            out += linestart + pad(n) + '\n'
    else:
        for n, name in zip(reversed(range(1, nx*ny + 1)), reversed(net_names)):
            out += linestart + pad_with_net_name(n, name) + '\n'
    for line in zone_end.split('\n'):
        out += linestart + line + '\n'
    return out


def add_pin_header_single(center_pt, net_name="", reference="REF**", ref_loc=(0, 2.25), linestart = '  '):
    net = "\n    (net {})".format(net_name) if net_name != "" else ""
    zone = \
"""(module Connector_Pin:Pin_D1.0mm_L10.0mm (layer F.Cu) (tedit 61D25885) (tstamp 61D25884)
  (at {x} {y})
  (descr "solder Pin_ diameter 1.0mm, hole diameter 1.0mm (press fit), length 10.0mm")
  (tags "solder Pin_ press fit")
  (fp_text reference {reference} (at {ref_loc_x} {ref_loc_y}) (layer F.SilkS)
    (effects (font (size 1 1) (thickness 0.15)))
  )
  (fp_text value Pin_D1.0mm_L10.0mm (at 0 -2.05) (layer F.Fab)
    (effects (font (size 1 1) (thickness 0.15)))
  )
  (fp_text user %R (at 0 2.25) (layer F.Fab)
    (effects (font (size 1 1) (thickness 0.15)))
  )
  (fp_circle (center 0 0) (end 1.5 0) (layer F.CrtYd) (width 0.05))
  (fp_circle (center 0 0) (end 0.5 0) (layer F.Fab) (width 0.12))
  (fp_circle (center 0 0) (end 1 0) (layer F.Fab) (width 0.12))
  (fp_circle (center 0 0) (end 1.25 0.05) (layer F.SilkS) (width 0.12))
  (pad 1 thru_hole circle (at 0 0) (size 1.7 1.7) (drill 1) (layers *.Cu *.Mask) {net})
  (model ${KISYS3DMOD}/Connector_Pin.3dshapes/Pin_D1.0mm_L10.0mm.wrl
    (at (xyz 0 0 0))
    (scale (xyz 1 1 1))
    (rotate (xyz 0 0 0))
  )
)""".format(x=center_pt[0], y=center_pt[1], net=net, reference=reference, ref_loc_x=ref_loc[0], ref_loc_y=ref_loc[1],
            KISYS3DMOD="{KISYS3DMOD}")
    out = ""
    for line in zone.split('\n'):
        out += linestart + line + '\n'
    return out


def add_STB12NM60N(center_pt, angle, net_drain, net_source, net_gate, reference, linestart='  '):
    """
    Adds a STB12NM60N high-voltage transistor to the board layout
    :param center_pt: Center of transistor layout
    :param angle: Angle (CCW from +x axis, degrees)
    :param net_drain: Net description of the drain (pad 2). Usually "6 "Net-(Q1-Pad2)""
    :param net_source: Net description of the source (pad 3). Usually "2 /GND"
    :param net_gate: Net description of the gate (pad 1). Usually "5 "Net-(Q1-Pad1)""
    :return: KiCAD description (string)
    """
    zone = \
"""(module Custom:TO-263-2-D2PAK (layer F.Cu) (tedit 61C8FCDD) (tstamp 61CA4E48)
  (at {x} {y} {angle})
  (descr "TO-263 / D2PAK / DDPAK SMD package, http://www.infineon.com/cms/en/product/packages/PG-TO263/PG-TO263-3-1/")
  (tags "D2PAK DDPAK TO-263 D2PAK-3 TO-263-3 SOT-404")
  (path /61C9CE68)
  (attr smd)
  (fp_text reference {reference} (at 0 -9 {angle}) (layer F.SilkS)
    (effects (font (size 1 1) (thickness 0.15)))
  )
  (fp_text value STB12NM60N (at 2.54 10.16 {angle}) (layer F.Fab)
    (effects (font (size 1 1) (thickness 0.15)))
  )
  (fp_line (start 8.128 -8.128) (end -13.208 -8.128) (layer F.CrtYd) (width 0.12))
  (fp_line (start 8.128 8.128) (end 8.128 -8.128) (layer F.CrtYd) (width 0.12))
  (fp_line (start -13.208 8.128) (end 8.128 8.128) (layer F.CrtYd) (width 0.12))
  (fp_line (start -13.208 -8.128) (end -13.208 8.128) (layer F.CrtYd) (width 0.12))
  (fp_line (start 6.35 7.46) (end 6.35 -7.62) (layer F.Fab) (width 0.1))
  (fp_line (start 7.62 7.62) (end 7.62 -7.62) (layer F.Fab) (width 0.12))
  (fp_line (start -5.08 7.62) (end 7.62 7.62) (layer F.Fab) (width 0.12))
  (fp_line (start -6.35 3.81) (end -12.7 3.81) (layer F.Fab) (width 0.12))
  (fp_line (start -12.7 3.81) (end -12.7 1.27) (layer F.Fab) (width 0.12))
  (fp_line (start -12.7 1.27) (end -6.35 1.27) (layer F.Fab) (width 0.12))
  (fp_line (start -6.35 -1.27) (end -12.7 -1.27) (layer F.Fab) (width 0.12))
  (fp_line (start -12.7 -1.27) (end -12.7 -3.81) (layer F.Fab) (width 0.12))
  (fp_line (start -12.7 -3.81) (end -6.35 -3.81) (layer F.Fab) (width 0.12))
  (fp_line (start 7.62 -7.62) (end -5.08 -7.62) (layer F.Fab) (width 0.12))
  (fp_line (start -5.08 -7.62) (end -6.35 -6.35) (layer F.Fab) (width 0.12))
  (fp_line (start -6.35 -6.35) (end -6.35 7.62) (layer F.Fab) (width 0.12))
  (fp_line (start -6.35 7.62) (end -5.08 7.62) (layer F.Fab) (width 0.12))
  (fp_line (start -2.794 -7.874) (end -6.604 -7.874) (layer F.SilkS) (width 0.12))
  (fp_line (start -6.604 -7.874) (end -6.604 -4.064) (layer F.SilkS) (width 0.12))
  (fp_line (start -6.604 -4.064) (end -12.7 -4.064) (layer F.SilkS) (width 0.12))
  (fp_line (start -8.89 4.064) (end -6.604 4.064) (layer F.SilkS) (width 0.12))
  (fp_line (start -6.604 4.064) (end -6.604 7.874) (layer F.SilkS) (width 0.12))
  (fp_line (start -6.604 7.874) (end -3.81 7.874) (layer F.SilkS) (width 0.12))
  (fp_text user %R (at -3.556 0 90) (layer F.Fab)
    (effects (font (size 1 1) (thickness 0.15)))
  )
  (pad 1 smd rect (at -10.275 -2.54 {angle}) (size 3.5 1.6) (layers F.Cu F.Paste F.Mask)
    (net {net_gate}))
  (pad 3 smd rect (at -10.275 2.54 {angle}) (size 3.5 1.6) (layers F.Cu F.Paste F.Mask)
    (net {net_source}))
  (pad 2 smd rect (at 0 0 {angle}) (size 9.75 12.2) (layers F.Cu F.Mask)
    (net {net_drain}))
  (model ${KISYS3DMOD}/Package_TO_SOT_SMD.3dshapes/TO-263-2.wrl
    (at (xyz -0.11811 0 0))
    (scale (xyz 1 1 1))
    (rotate (xyz 0 0 0))
  )
)""".format(x=center_pt[0], y=center_pt[1], angle=angle, net_drain=net_drain, net_source=net_source, net_gate=net_gate,
            reference=reference, KISYS3DMOD="{KISYS3DMOD}")
    out = ""
    for line in zone.split('\n'):
        out += linestart + line + '\n'
    return out


def add_resistor_1206(center_pt, angle, reference, net1, net2, value, linestart='  '):
    """
    Add resistor with 1206 layout (12mm x 6 mm)
    :param center_pt: Center of resistor
    :param angle: Angle of component (CCW from +x axis, degrees)
    :param linestart: Formatting start of line
    :return: KiCAD description
    """
    zone = \
"""(module Resistor_SMD:R_1206_3216Metric_Pad1.30x1.75mm_HandSolder (layer F.Cu) (tedit 5F68FEEE) (tstamp 61CA5312)
  (at {x} {y} {angle})
  (descr "Resistor SMD 1206 (3216 Metric), square (rectangular) end terminal, IPC_7351 nominal with elongated pad for handsoldering. (Body size source: IPC-SM-782 page 72, https://www.pcb-3d.com/wordpress/wp-content/uploads/ipc-sm-782a_amendment_1_and_2.pdf), generated with kicad-footprint-generator")
  (tags "resistor handsolder")
  (path /61CC59F8)
  (attr smd)
  (fp_text reference {reference} (at 0 -1.65 {angle}) (layer F.SilkS)
    (effects (font (size 1 1) (thickness 0.15)))
  )
  (fp_text value {value} (at 0 1.65 {angle}) (layer F.Fab)
    (effects (font (size 1 1) (thickness 0.15)))
  )
  (fp_text user %R (at 0 0 {angle}) (layer F.Fab)
    (effects (font (size 0.5 0.5) (thickness 0.08)))
  )
  (fp_line (start -1.6 0.8) (end -1.6 -0.8) (layer F.Fab) (width 0.1))
  (fp_line (start -1.6 -0.8) (end 1.6 -0.8) (layer F.Fab) (width 0.1))
  (fp_line (start 1.6 -0.8) (end 1.6 0.8) (layer F.Fab) (width 0.1))
  (fp_line (start 1.6 0.8) (end -1.6 0.8) (layer F.Fab) (width 0.1))
  (fp_line (start -0.727064 -0.91) (end 0.727064 -0.91) (layer F.SilkS) (width 0.12))
  (fp_line (start -0.727064 0.91) (end 0.727064 0.91) (layer F.SilkS) (width 0.12))
  (fp_line (start -2.45 1.12) (end -2.45 -1.12) (layer F.CrtYd) (width 0.05))
  (fp_line (start -2.45 -1.12) (end 2.45 -1.12) (layer F.CrtYd) (width 0.05))
  (fp_line (start 2.45 -1.12) (end 2.45 1.12) (layer F.CrtYd) (width 0.05))
  (fp_line (start 2.45 1.12) (end -2.45 1.12) (layer F.CrtYd) (width 0.05))
  (pad 2 smd roundrect (at 1.55 0 {angle}) (size 1.3 1.75) (layers F.Cu F.Paste F.Mask) (roundrect_rratio 0.192308)
    (net {net2}))
  (pad 1 smd roundrect (at -1.55 0 {angle}) (size 1.3 1.75) (layers F.Cu F.Paste F.Mask) (roundrect_rratio 0.192308)
    (net {net1}))
  (model ${KISYS3DMOD}/Resistor_SMD.3dshapes/R_1206_3216Metric.wrl
    (at (xyz 0 0 0))
    (scale (xyz 1 1 1))
    (rotate (xyz 0 0 0))
  )
)""".format(x=center_pt[0], y=center_pt[1], angle=angle, reference=reference, net1=net1, net2=net2, value=value,
            KISYS3DMOD="{KISYS3DMOD}")
    out = ""
    for line in zone.split('\n'):
        out += linestart + line + '\n'
    return out


def add_A05P5(center_pt, angle, reference, net_Vin_plus, net_Vin_minus, net_Vctrl, net_Vout_plus, net_Vout_minus,
              value="A05P-5", linestart='  '):
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
    :param linestart:
    :return: KiCAD description
    """
    zone = \
"""(module Custom:Converter_DCDC_XP_POWER_A05P-5_THT (layer F.Cu) (tedit 61C9B5D0) (tstamp 61CA4DF0)
 (at {x} {y} {angle})
 (descr "XP Power JTD Series DC-DC Converter")
  (tags "DCDC Isolated")
  (path /61C9B1A8)
  (fp_text reference {reference} (at -9.652 -3.048 {angle}) (layer F.SilkS)
    (effects (font (size 1 1) (thickness 0.15)))
  )
  (fp_text value {value} (at -8.89 11.684 {angle}) (layer F.Fab)
    (effects (font (size 1 1) (thickness 0.15)))
  )
  (fp_line (start -16 -1.52) (end 1.98 -1.52) (layer F.SilkS) (width 0.12))
  (fp_line (start 1.98 -1.52) (end 1.978001 10.155999) (layer F.SilkS) (width 0.12))
  (fp_line (start 1.978001 10.155999) (end -16.001999 10.155999) (layer F.SilkS) (width 0.12))
  (fp_poly (pts (xy -2.54 3.81) (xy 1.778 3.81) (xy 1.778 9.906) (xy -9.398 9.906)
    (xy -9.398 -1.27) (xy -2.54 -1.27)) (layer Cmts.User) (width 0.1))
  (fp_line (start -15.748 -1.778) (end 2.286 -1.778) (layer F.CrtYd) (width 0.12))
  (fp_line (start 2.286 -1.778) (end 2.286 10.414) (layer F.CrtYd) (width 0.12))
  (fp_line (start 2.286 10.414) (end -16.002 10.414) (layer F.CrtYd) (width 0.12))
  (fp_arc (start -15.748 4.318) (end -15.748 -1.778) (angle -177.614056) (layer F.CrtYd) (width 0.12))
  (fp_arc (start -16.002 4.318) (end -16.000001 -1.519999) (angle -180.0196286) (layer F.SilkS) (width 0.12))
  (fp_text user %R (at -5.08 4.572 90) (layer F.Fab)
    (effects (font (size 1 1) (thickness 0.15)))
  )
  (pad 5 thru_hole circle (at -12.8 8.38 {angle}) (size 2 2) (drill 1) (layers *.Cu *.Mask)
    (net {net_Vctrl}))
  (pad 4 thru_hole circle (at -10.92 1.57 {angle}) (size 2 2) (drill 1) (layers *.Cu *.Mask)
    (net {net_Vout_minus}))
  (pad 3 thru_hole circle (at 0 1.57 {angle}) (size 2 2) (drill 1) (layers *.Cu *.Mask)
    (net {net_Vout_plus}))
  (pad 2 thru_hole circle (at -11.68 5.97 {angle}) (size 2 2) (drill 1) (layers *.Cu *.Mask)
    (net {net_Vin_minus}))
  (pad 1 thru_hole roundrect (at -12.8 0 {angle}) (size 2 2) (drill 1) (layers *.Cu *.Mask) (roundrect_rratio 0.25)
    (net {net_Vin_plus}))
  (model ${KISYS3DMOD}/Converter_DCDC.3dshapes/Converter_DCDC_XP_POWER_JTDxxxxxxx_THT.wrl
    (at (xyz 0 0 0))
    (scale (xyz 1 1 1))
    (rotate (xyz 0 0 0))
  )
  (model ${KIPRJMOD}/drive_circuit_footprints/A01-20.STEP
    (offset (xyz 2 1.5 0))
    (scale (xyz 1 1 1))
    (rotate (xyz 90 180 0))
  )
)
""".format(x=center_pt[0], y=center_pt[1], angle=angle, reference=reference, value=value, net_Vin_plus=net_Vin_plus,
           net_Vin_minus=net_Vin_minus, net_Vctrl=net_Vctrl, net_Vout_plus=net_Vout_plus, net_Vout_minus=net_Vout_minus,
           KISYS3DMOD="{KISYS3DMOD}", KIPRJMOD="{KIPRJMOD}")
    out = ""
    for line in zone.split('\n'):
        out += linestart + line + '\n'
    return out


def add_teensy41(center_pt, angle, reference, net_names, value="Teensy4.1", linestart='  '):
    """
    Adds a Teensy 4.1 to the layout
    :param center_pt:
    :param angle: Angle (CCW from +x axis, degrees) (default = horizontal, USB to left)
    :param reference:
    :param value:
    :param linestart:
    :return:
    """
    nets = []
    for i in range(1, 68):
        net_name = "\n     (net {})".format(net_names[i-1])
        nets.append(net_name)
    angleleftturn = (angle - 90) % 360
    anglerightturn = (angle + 90) % 360
    angle180 = (angle + 180) % 360

    zone = \
"""(module Custom:Teensy41 (layer F.Cu) (tedit 5FD6DEAD) (tstamp 61CA5666)
   (at {x} {y} {angle})
   (path /61CA0929)
   (fp_text reference {reference} (at 0 -10.16) (layer F.SilkS)
     (effects (font (size 1 1) (thickness 0.15)))
   )
   (fp_text value {value} (at 0 10.16) (layer F.Fab)
     (effects (font (size 1 1) (thickness 0.15)))
   )
   (fp_poly (pts (xy 3.197 -0.307) (xy 2.943 -0.053) (xy 2.689 -0.434) (xy 2.943 -0.688)) (layer F.SilkS) (width 0.1))
   (fp_poly (pts (xy 2.816 0.074) (xy 2.562 0.328) (xy 2.308 -0.053) (xy 2.562 -0.307)) (layer F.SilkS) (width 0.1))
   (fp_poly (pts (xy 0.911 -0.688) (xy 0.657 -0.434) (xy 0.403 -0.815) (xy 0.657 -1.069)) (layer F.SilkS) (width 0.1))
   (fp_poly (pts (xy 1.292 -0.18) (xy 1.038 0.074) (xy 0.784 -0.307) (xy 1.038 -0.561)) (layer F.SilkS) (width 0.1))
   (fp_poly (pts (xy 1.673 0.328) (xy 1.419 0.582) (xy 1.165 0.201) (xy 1.419 -0.053)) (layer F.SilkS) (width 0.1))
   (fp_poly (pts (xy 1.673 -0.561) (xy 1.419 -0.307) (xy 1.165 -0.688) (xy 1.419 -0.942)) (layer F.SilkS) (width 0.1))
   (fp_poly (pts (xy 2.054 -0.053) (xy 1.8 0.201) (xy 1.546 -0.18) (xy 1.8 -0.434)) (layer F.SilkS) (width 0.1))
   (fp_poly (pts (xy 2.435 0.455) (xy 2.181 0.709) (xy 1.927 0.328) (xy 2.181 0.074)) (layer F.SilkS) (width 0.1))
   (fp_line (start -30.48 8.89) (end -30.48 -8.89) (layer F.SilkS) (width 0.15))
   (fp_line (start 30.48 8.89) (end -30.48 8.89) (layer F.SilkS) (width 0.15))
   (fp_line (start 30.48 -8.89) (end 30.48 8.89) (layer F.SilkS) (width 0.15))
   (fp_line (start -30.48 -8.89) (end 30.48 -8.89) (layer F.SilkS) (width 0.15))
   (fp_line (start -25.4 3.81) (end -30.48 3.81) (layer F.SilkS) (width 0.15))
   (fp_line (start -25.4 -3.81) (end -30.48 -3.81) (layer F.SilkS) (width 0.15))
   (fp_line (start -25.4 3.81) (end -25.4 -3.81) (layer F.SilkS) (width 0.15))
   (fp_line (start -31.75 -3.81) (end -30.48 -3.81) (layer F.SilkS) (width 0.15))
   (fp_line (start -31.75 3.81) (end -31.75 -3.81) (layer F.SilkS) (width 0.15))
   (fp_line (start -30.48 3.81) (end -31.75 3.81) (layer F.SilkS) (width 0.15))
   (fp_line (start 30.48 -6.35) (end 17.78 -6.35) (layer F.SilkS) (width 0.15))
   (fp_line (start 17.78 -6.35) (end 17.78 6.35) (layer F.SilkS) (width 0.15))
   (fp_line (start 17.78 6.35) (end 30.48 6.35) (layer F.SilkS) (width 0.15))
   (fp_line (start 30.48 -5.08) (end 29.21 -5.08) (layer F.SilkS) (width 0.15))
   (fp_line (start 29.21 -5.08) (end 29.21 5.08) (layer F.SilkS) (width 0.15))
   (fp_line (start 29.21 5.08) (end 30.48 5.08) (layer F.SilkS) (width 0.15))
   (fp_line (start 13.97 -1.27) (end 13.97 1.27) (layer F.SilkS) (width 0.15))
   (fp_line (start 13.97 1.27) (end 10.16 1.27) (layer F.SilkS) (width 0.15))
   (fp_line (start 10.16 1.27) (end 10.16 -1.27) (layer F.SilkS) (width 0.15))
   (fp_line (start 10.16 -1.27) (end 13.97 -1.27) (layer F.SilkS) (width 0.15))
   (fp_line (start -24.1808 3.2992) (end -11.4808 3.2992) (layer F.SilkS) (width 0.15))
   (fp_line (start -11.4808 3.2992) (end -11.4808 5.8392) (layer F.SilkS) (width 0.15))
   (fp_line (start -11.4808 5.8392) (end -24.1808 5.8392) (layer F.SilkS) (width 0.15))
   (fp_line (start -24.1808 5.8392) (end -24.1808 3.2992) (layer F.SilkS) (width 0.15))
   (fp_line (start -24.1808 3.2992) (end -21.6408 3.2992) (layer F.SilkS) (width 0.15))
   (fp_line (start -21.6408 3.2992) (end -21.6408 5.8392) (layer F.SilkS) (width 0.15))
   (fp_line (start -17.25 -6.1016) (end -17.25 -0.1016) (layer F.SilkS) (width 0.15))
   (fp_line (start -17.25 -0.1016) (end -13.25 -0.1016) (layer F.SilkS) (width 0.15))
   (fp_line (start -13.25 -0.1016) (end -13.25 -6.3516) (layer F.SilkS) (width 0.15))
   (fp_line (start -13.25 -6.3516) (end -17.25 -6.3516) (layer F.SilkS) (width 0.15))
   (fp_line (start -17.25 -6.3516) (end -17.25 -6.1016) (layer F.SilkS) (width 0.15))
   (fp_line (start -7.62 6.35) (end 5.08 6.35) (layer F.SilkS) (width 0.15))
   (fp_line (start 5.08 6.35) (end 5.08 -6.35) (layer F.SilkS) (width 0.15))
   (fp_line (start 5.08 -6.35) (end -7.62 -6.35) (layer F.SilkS) (width 0.15))
   (fp_line (start -7.62 -6.35) (end -7.62 6.35) (layer F.SilkS) (width 0.15))
   (fp_circle (center 12.065 0) (end 12.7 -0.635) (layer F.SilkS) (width 0.15))
   (fp_text user "USB Host" (at -18.4658 2.4892) (layer F.SilkS)
     (effects (font (size 1 1) (thickness 0.15)))
   )
   (fp_text user Ethernet (at -12.065 -3.2766 {angleleftturn}) (layer F.SilkS)
     (effects (font (size 1 1) (thickness 0.15)))
   )
   (fp_text user USB (at -26.67 0 {anglerightturn}) (layer F.SilkS)
     (effects (font (size 1 1) (thickness 0.15)))
   )
   (fp_text user "Micro SD" (at 24.13 0 {angle180}) (layer F.SilkS)
     (effects (font (size 1 1) (thickness 0.15)))
   )
   (fp_text user MIMXRT1062 (at -1.27 0 {anglerightturn}) (layer F.SilkS)
     (effects (font (size 0.7 0.7) (thickness 0.15)))
   )
   (fp_text user DVJ6A (at -2.54 -0.18 {anglerightturn}) (layer F.SilkS)
     (effects (font (size 0.7 0.7) (thickness 0.15)))
   )
   (pad 66 thru_hole circle (at -28.48 -1.27 {angle}) (size 1.3 1.3) (drill 0.8) (layers *.Cu *.Mask) {net66})
   (pad 67 thru_hole circle (at -28.48 1.27 {angle}) (size 1.3 1.3) (drill 0.8) (layers *.Cu *.Mask) {net67})
   (pad 54 thru_hole circle (at 16.51 -5.08 {angle}) (size 1.6 1.6) (drill 1.1) (layers *.Cu *.Mask) {net54})
   (pad 53 thru_hole circle (at 16.51 -2.54 {angle}) (size 1.6 1.6) (drill 1.1) (layers *.Cu *.Mask) {net53})
   (pad 52 thru_hole circle (at 16.51 0 {angle}) (size 1.6 1.6) (drill 1.1) (layers *.Cu *.Mask) {net52})
   (pad 51 thru_hole circle (at 16.51 2.54 {angle}) (size 1.6 1.6) (drill 1.1) (layers *.Cu *.Mask) {net51})
   (pad 50 thru_hole circle (at 16.51 5.08 {angle}) (size 1.6 1.6) (drill 1.1) (layers *.Cu *.Mask) {net50})
   (pad 62 thru_hole circle (at -16.24 -1.1816 {angle}) (size 1.3 1.3) (drill 0.8) (layers *.Cu *.Mask) {net62})
   (pad 63 thru_hole circle (at -14.24 -1.1816 {angle}) (size 1.3 1.3) (drill 0.8) (layers *.Cu *.Mask) {net63})
   (pad 64 thru_hole circle (at -14.24 -3.1816 {angle}) (size 1.3 1.3) (drill 0.8) (layers *.Cu *.Mask) {net64})
   (pad 61 thru_hole circle (at -16.24 -3.1816 {angle}) (size 1.3 1.3) (drill 0.8) (layers *.Cu *.Mask) {net61})
   (pad 65 thru_hole circle (at -14.24 -5.1816 {angle}) (size 1.3 1.3) (drill 0.8) (layers *.Cu *.Mask) {net65})
   (pad 60 thru_hole rect (at -16.24 -5.1816 {angle}) (size 1.3 1.3) (drill 0.8) (layers *.Cu *.Mask) {net60})
   (pad 17 thru_hole circle (at 11.43 7.62 {angle}) (size 1.6 1.6) (drill 1.1) (layers *.Cu *.Mask) {net17})
   (pad 18 thru_hole circle (at 13.97 7.62 {angle}) (size 1.6 1.6) (drill 1.1) (layers *.Cu *.Mask) {net18})
   (pad 19 thru_hole circle (at 16.51 7.62 {angle}) (size 1.6 1.6) (drill 1.1) (layers *.Cu *.Mask) {net19})
   (pad 20 thru_hole circle (at 19.05 7.62 {angle}) (size 1.6 1.6) (drill 1.1) (layers *.Cu *.Mask) {net20})
   (pad 16 thru_hole circle (at 8.89 7.62 {angle}) (size 1.6 1.6) (drill 1.1) (layers *.Cu *.Mask) {net16})
   (pad 15 thru_hole circle (at 6.35 7.62 {angle}) (size 1.6 1.6) (drill 1.1) (layers *.Cu *.Mask) {net15})
   (pad 14 thru_hole circle (at 3.81 7.62 {angle}) (size 1.6 1.6) (drill 1.1) (layers *.Cu *.Mask) {net14})
   (pad 21 thru_hole circle (at 21.59 7.62 {angle}) (size 1.6 1.6) (drill 1.1) (layers *.Cu *.Mask) {net21})
   (pad 22 thru_hole circle (at 24.13 7.62 {angle}) (size 1.6 1.6) (drill 1.1) (layers *.Cu *.Mask) {net22})
   (pad 23 thru_hole circle (at 26.67 7.62 {angle}) (size 1.6 1.6) (drill 1.1) (layers *.Cu *.Mask) {net23})
   (pad 24 thru_hole circle (at 29.21 7.62 {angle}) (size 1.6 1.6) (drill 1.1) (layers *.Cu *.Mask) {net24})
   (pad 25 thru_hole circle (at 29.21 -7.62 {angle}) (size 1.6 1.6) (drill 1.1) (layers *.Cu *.Mask) {net25})
   (pad 26 thru_hole circle (at 26.67 -7.62 {angle}) (size 1.6 1.6) (drill 1.1) (layers *.Cu *.Mask) {net26})
   (pad 27 thru_hole circle (at 24.13 -7.62 {angle}) (size 1.6 1.6) (drill 1.1) (layers *.Cu *.Mask) {net27})
   (pad 28 thru_hole circle (at 21.59 -7.62 {angle}) (size 1.6 1.6) (drill 1.1) (layers *.Cu *.Mask) {net28})
   (pad 29 thru_hole circle (at 19.05 -7.62 {angle}) (size 1.6 1.6) (drill 1.1) (layers *.Cu *.Mask) {net29})
   (pad 30 thru_hole circle (at 16.51 -7.62 {angle}) (size 1.6 1.6) (drill 1.1) (layers *.Cu *.Mask) {net30})
   (pad 31 thru_hole circle (at 13.97 -7.62 {angle}) (size 1.6 1.6) (drill 1.1) (layers *.Cu *.Mask) {net31})
   (pad 32 thru_hole circle (at 11.43 -7.62 {angle}) (size 1.6 1.6) (drill 1.1) (layers *.Cu *.Mask) {net32})
   (pad 33 thru_hole circle (at 8.89 -7.62 {angle}) (size 1.6 1.6) (drill 1.1) (layers *.Cu *.Mask) {net33})
   (pad 34 thru_hole circle (at 6.35 -7.62 {angle}) (size 1.6 1.6) (drill 1.1) (layers *.Cu *.Mask) {net34})
   (pad 13 thru_hole circle (at 1.27 7.62 {angle}) (size 1.6 1.6) (drill 1.1) (layers *.Cu *.Mask) {net13})
   (pad 12 thru_hole circle (at -1.27 7.62 {angle}) (size 1.6 1.6) (drill 1.1) (layers *.Cu *.Mask) {net12})
   (pad 11 thru_hole circle (at -3.81 7.62 {angle}) (size 1.6 1.6) (drill 1.1) (layers *.Cu *.Mask) {net11})
   (pad 10 thru_hole circle (at -6.35 7.62 {angle}) (size 1.6 1.6) (drill 1.1) (layers *.Cu *.Mask) {net10})
   (pad 9 thru_hole circle (at -8.89 7.62 {angle}) (size 1.6 1.6) (drill 1.1) (layers *.Cu *.Mask) {net9})
   (pad 8 thru_hole circle (at -11.43 7.62 {angle}) (size 1.6 1.6) (drill 1.1) (layers *.Cu *.Mask) {net8})
   (pad 7 thru_hole circle (at -13.97 7.62 {angle}) (size 1.6 1.6) (drill 1.1) (layers *.Cu *.Mask) {net7})
   (pad 6 thru_hole circle (at -16.51 7.62 {angle}) (size 1.6 1.6) (drill 1.1) (layers *.Cu *.Mask) {net6})
   (pad 5 thru_hole circle (at -19.05 7.62 {angle}) (size 1.6 1.6) (drill 1.1) (layers *.Cu *.Mask) {net5})
   (pad 4 thru_hole circle (at -21.59 7.62 {angle}) (size 1.6 1.6) (drill 1.1) (layers *.Cu *.Mask) {net4})
   (pad 3 thru_hole circle (at -24.13 7.62 {angle}) (size 1.6 1.6) (drill 1.1) (layers *.Cu *.Mask) {net3})
   (pad 2 thru_hole circle (at -26.67 7.62 {angle}) (size 1.6 1.6) (drill 1.1) (layers *.Cu *.Mask) {net2})
   (pad 1 thru_hole rect (at -29.21 7.62 {angle}) (size 1.6 1.6) (drill 1.1) (layers *.Cu *.Mask) {net1})
   (pad 35 thru_hole circle (at 3.81 -7.62 {angle}) (size 1.6 1.6) (drill 1.1) (layers *.Cu *.Mask) {net35})
   (pad 36 thru_hole circle (at 1.27 -7.62 {angle}) (size 1.6 1.6) (drill 1.1) (layers *.Cu *.Mask) {net36})
   (pad 37 thru_hole circle (at -1.27 -7.62 {angle}) (size 1.6 1.6) (drill 1.1) (layers *.Cu *.Mask) {net37})
   (pad 38 thru_hole circle (at -3.81 -7.62 {angle}) (size 1.6 1.6) (drill 1.1) (layers *.Cu *.Mask) {net38})
   (pad 39 thru_hole circle (at -6.35 -7.62 {angle}) (size 1.6 1.6) (drill 1.1) (layers *.Cu *.Mask) {net39})
   (pad 40 thru_hole circle (at -8.89 -7.62 {angle}) (size 1.6 1.6) (drill 1.1) (layers *.Cu *.Mask) {net40})
   (pad 41 thru_hole circle (at -11.43 -7.62 {angle}) (size 1.6 1.6) (drill 1.1) (layers *.Cu *.Mask) {net41})
   (pad 42 thru_hole circle (at -13.97 -7.62 {angle}) (size 1.6 1.6) (drill 1.1) (layers *.Cu *.Mask) {net42})
   (pad 43 thru_hole circle (at -16.51 -7.62 {angle}) (size 1.6 1.6) (drill 1.1) (layers *.Cu *.Mask) {net43})
   (pad 44 thru_hole circle (at -19.05 -7.62 {angle}) (size 1.6 1.6) (drill 1.1) (layers *.Cu *.Mask) {net44})
   (pad 45 thru_hole circle (at -21.59 -7.62 {angle}) (size 1.6 1.6) (drill 1.1) (layers *.Cu *.Mask) {net45})
   (pad 46 thru_hole circle (at -24.13 -7.62 {angle}) (size 1.6 1.6) (drill 1.1) (layers *.Cu *.Mask) {net46})
   (pad 47 thru_hole circle (at -26.67 -7.62 {angle}) (size 1.6 1.6) (drill 1.1) (layers *.Cu *.Mask) {net47})
   (pad 48 thru_hole circle (at -29.21 -7.62 {angle}) (size 1.6 1.6) (drill 1.1) (layers *.Cu *.Mask) {net48})
   (pad 55 thru_hole rect (at -22.9108 4.5692 {angle}) (size 1.6 1.6) (drill 1.1) (layers *.Cu *.Mask) {net55})
   (pad 56 thru_hole circle (at -20.3708 4.5692 {angle}) (size 1.6 1.6) (drill 1.1) (layers *.Cu *.Mask) {net56})
   (pad 57 thru_hole circle (at -17.8308 4.5692 {angle}) (size 1.6 1.6) (drill 1.1) (layers *.Cu *.Mask) {net57})
   (pad 58 thru_hole circle (at -15.2908 4.5692 {angle}) (size 1.6 1.6) (drill 1.1) (layers *.Cu *.Mask) {net58})
   (pad 59 thru_hole circle (at -12.7508 4.5692 {angle}) (size 1.6 1.6) (drill 1.1) (layers *.Cu *.Mask) {net59})
   (pad 49 thru_hole circle (at -26.67 -5.08 {angle}) (size 1.6 1.6) (drill 1.1) (layers *.Cu *.Mask) {net49})
   (model ${KICAD_USER_DIR}/teensy.pretty/Teensy_4.1_Assembly.STEP
     (offset (xyz 0 0 0.762))
     (scale (xyz 1 1 1))
     (rotate (xyz 0 0 0))
   )
)""".format(x=center_pt[0], y=center_pt[1], angle=angle, reference=reference, value=value,
            KICAD_USER_DIR="{KICAD_USER_DIR}", angleleftturn=angleleftturn, anglerightturn=anglerightturn,
            angle180=angle180,
            net1=nets[0], net2=nets[1], net3=nets[2], net4=nets[3], net5=nets[4], net6=nets[5],
            net7=nets[6], net8=nets[7], net9=nets[8], net10=nets[9], net11=nets[10], net12=nets[11],
            net13=nets[12], net14=nets[13], net15=nets[14], net16=nets[15], net17=nets[16], net18=nets[17],
            net19=nets[18], net20=nets[19], net21=nets[20], net22=nets[21], net23=nets[22], net24=nets[23],
            net25=nets[24], net26=nets[25], net27=nets[26], net28=nets[27], net29=nets[28], net30=nets[29],
            net31=nets[30], net32=nets[31], net33=nets[32], net34=nets[33], net35=nets[34], net36=nets[35],
            net37=nets[36], net38=nets[37], net39=nets[38], net40=nets[39], net41=nets[40], net42=nets[41],
            net43=nets[42], net44=nets[43], net45=nets[44], net46=nets[45], net47=nets[46], net48=nets[47],
            net49=nets[48], net50=nets[49], net51=nets[50], net52=nets[51], net53=nets[52], net54=nets[53],
            net55=nets[54], net56=nets[55], net57=nets[56], net58=nets[57], net59=nets[58], net60=nets[59],
            net61=nets[60], net62=nets[61], net63=nets[62], net64=nets[63], net65=nets[64], net66=nets[65],
            net67=nets[66])
    out = ""
    for line in zone.split('\n'):
        out += linestart + line + '\n'
    return out


def add_header(net_names=("main",), net_classes=(0,), default_clearance=BOARD_EDGE_SPACING_EFF,
               default_linewidth=LINESPACE, power_clearance=BOARD_EDGE_SPACING_EFF, power_linewidth=0.5):
    """
    Defines the KiCAD header
    :param net_names: A list of the names of all nets, in the order they should appear in the file
    :param net_classes: A list of the net classes of each net. 0 = Default net, 1 = Power net.
    :return: KiCAD header
    """
    net_desc = ""
    default_desc = ""
    power_desc = ""
    for i, zipped in enumerate(zip(net_names, net_classes)):
        net_name, net_class = zipped
        net_desc += "\n  (net " + str(i+1) + " " + net_name + ")"
        if net_class == 0:
            default_desc += "\n    (add_net " + net_name + ")"
        elif net_class == 1:
            power_desc += "\n    (add_net " + net_name + ")"
    if len(net_names) != 0:
        net_desc += "\n\n"


    start = \
"""(kicad_pcb (version 20171130) (host pcbnew "(5.1.10)-1")

  (general
    (thickness 1.6)
    (drawings 64)
    (tracks 0)
    (zones 0)
    (modules 0)
    (nets 1)
  )

  (page A4)
  (layers
    (0 F.Cu signal)
    (31 B.Cu signal)
    (32 B.Adhes user)
    (33 F.Adhes user)
    (34 B.Paste user)
    (35 F.Paste user)
    (36 B.SilkS user)
    (37 F.SilkS user)
    (38 B.Mask user)
    (39 F.Mask user)
    (40 Dwgs.User user)
    (41 Cmts.User user)
    (42 Eco1.User user)
    (43 Eco2.User user)
    (44 Edge.Cuts user)
    (45 Margin user)
    (46 B.CrtYd user)
    (47 F.CrtYd user)
    (48 B.Fab user)
    (49 F.Fab user)
  )

  (setup
    (last_trace_width 0.25)
    (trace_clearance {trace_clearance})
    (zone_clearance {zone_clearance})
    (zone_45_only no)
    (trace_min {trace_min})
    (via_size 0.8)
    (via_drill 0.4)
    (via_min_size 0.4)
    (via_min_drill 0.3)
    (uvia_size 0.3)
    (uvia_drill 0.1)
    (uvias_allowed no)
    (uvia_min_size 0.2)
    (uvia_min_drill 0.1)
    (edge_width 0.05)
    (segment_width 0.2)
    (pcb_text_width 0.3)
    (pcb_text_size 1.5 1.5)
    (mod_edge_width 0.12)
    (mod_text_size 1 1)
    (mod_text_width 0.15)
    (pad_size 1.524 1.524)
    (pad_drill 0.762)
    (pad_to_mask_clearance 0)
    (aux_axis_origin 0 0)
    (visible_elements 7FFFFFFF)
    (pcbplotparams
      (layerselection 0x010a8_7fffffff)
      (usegerberextensions false)
      (usegerberattributes true)
      (usegerberadvancedattributes true)
      (creategerberjobfile true)
      (excludeedgelayer true)
      (linewidth 0.100000)
      (plotframeref false)
      (viasonmask false)
      (mode 1)
      (useauxorigin false)
      (hpglpennumber 1)
      (hpglpenspeed 20)
      (hpglpendiameter 15.000000)
      (psnegative false)
      (psa4output false)
      (plotreference true)
      (plotvalue true)
      (plotinvisibletext false)
      (padsonsilk false)
      (subtractmaskfromsilk false)
      (outputformat 1)
      (mirror false)
      (drillshape 0)
      (scaleselection 1)
      (outputdirectory "C:/Users/ahadrauf/Desktop/Research/pcb_wire_testing_setup/"))
  )

  (net 0 "") {net_desc}""".format(trace_clearance=BOARD_EDGE_SPACING_EFF,
                                  zone_clearance=BOARD_EDGE_SPACING_EFF*2,
                                  trace_min=LINESPACE, net_desc=net_desc)

    end = \
"""  (net_class Default "This is the default net class."
    (clearance {})
    (trace_width {})
    (via_dia 0.8)
    (via_drill 0.4)
    (uvia_dia 0.3)
    (uvia_drill 0.1) {}
  )
  
  (net_class Power "For high power traces."
    (clearance {})
    (trace_width {})
    (via_dia 0.8)
    (via_drill 0.4)
    (uvia_dia 0.3)
    (uvia_drill 0.1) {}
  )
""".format(default_clearance, default_linewidth, default_desc, power_clearance, power_linewidth, power_desc)
    # print(zone)
    return start + end


def add_footer():
    zone = ")"
    # print(zone)
    return zone

