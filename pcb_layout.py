import numpy as np
from utils import *


MIL_TO_MM = 0.0254
LINESPACE = 3*MIL_TO_MM  # defined by manufacturer
BOARD_EDGE_SPACING = 7*MIL_TO_MM  # defined by manufacturer

EDGECUT_WIDTH = 0.05  # default in KiCad
BOARD_EDGE_SPACING_EFF = BOARD_EDGE_SPACING + EDGECUT_WIDTH/2  # Since in KiCad, the edge cut has width

NET_NAME = "main"

def add_fill_zone_rectangle(topleft, bottomright, min_thickness=0.01, layer="F.Cu", linestart='  '):
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
"""(zone (net 1) (net_name "{}") (layer {}) (tstamp 0) (hatch edge 0.508)
  (connect_pads (clearance {}))
  (min_thickness {})
  (fill yes (arc_segments 32) (thermal_gap 0.508) (thermal_bridge_width 0.508))
  (polygon
    (pts
      (xy {} {}) (xy {} {}) (xy {} {}) (xy {} {})
    )
  )
)""".format(NET_NAME, layer, BOARD_EDGE_SPACING, LINESPACE/4, x2, y2, x1, y2, x1, y1, x2, y1)
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


def add_fill_zone_polygon(pts, min_thickness=0.01, layer="F.Cu", linestart='  '):
    """
    Add fill zone
    In KiCad, click Place > Zone, then right click inside a zone >
    :param topleft:
    :param bottomright:
    :param min_thickness:
    :param linestart:
    :return:
    """
    pts_str = " ".join(["(xy {} {})".format(pt[0], pt[1]) for pt in pts])
    zone = \
"""(zone (net 1) (net_name "{}") (layer {}) (tstamp 0) (hatch edge 0.508)
  (connect_pads (clearance {}))
  (min_thickness {})
  (fill yes (arc_segments 32) (thermal_gap 0.508) (thermal_bridge_width 0.508))
  (polygon
    (pts
      {}
    )
  )
)""".format(NET_NAME, layer, BOARD_EDGE_SPACING, LINESPACE/4, pts_str)
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


def add_text(txt, center_loc, angleCCW=0, scale=0.5, thickness=0.125, linestart='  '):
    zone = \
"""(gr_text "{}" (at {} {} {}) (layer F.SilkS)
  (effects (font (size {} {}) (thickness {})))
)""".format(txt, center_loc[0], center_loc[1], angleCCW, scale, scale, thickness)
    out = ""
    for line in zone.split('\n'):
        out += linestart + line + '\n'
        # print(linestart + line)
    return out


def add_trace(pts, width=LINESPACE, linestart='  '):
    out = ''
    for i in range(len(pts) - 1):
        start = pts[i]
        end = pts[i + 1]
        zone = "(segment (start {} {}) (end {} {}) (width {}) (layer F.Cu) (net 1))".format(start[0], start[1],
                                                                                            end[0], end[1], width)
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


def add_via(pt, size=0.8, drill=0.4, layers=("F.Cu", "B.Cu"), linestart='  '):
    zone = "(via (at {} {}) (size {}) (drill {}) (layers {} {}) (net 1))".format(pt[0], pt[1], size, drill,
                                                                                              layers[0], layers[1])
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

def add_header():
    zone = \
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
    (trace_clearance {})
    (zone_clearance {})
    (zone_45_only no)
    (trace_min {})
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

  (net 0 "")
  (net 1 "{}")

  (net_class Default "This is the default net class."
    (clearance {})
    (trace_width {})
    (via_dia 0.8)
    (via_drill 0.4)
    (uvia_dia 0.3)
    (uvia_drill 0.1)
  )
""".format(BOARD_EDGE_SPACING, BOARD_EDGE_SPACING, LINESPACE/4, NET_NAME, BOARD_EDGE_SPACING, LINESPACE)
    # print(zone)
    return zone


def add_footer():
    zone = ")"
    # print(zone)
    return zone

