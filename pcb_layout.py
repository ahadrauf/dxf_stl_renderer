import numpy as np


MIL_TO_MM = 0.0254
CUTOUT_WIDTH = 0.05  # default in KiCad
LINESPACE = 3*MIL_TO_MM  # defined by manufacturer
BOARD_EDGE_SPACING = 7*MIL_TO_MM + CUTOUT_WIDTH/2  # defined by manufacturer


def add_fill_zone_rectangle(topleft, bottomright, min_thickness=0.01, linestart='  '):
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
"""(zone (net 0) (net_name "") (layer F.Cu) (tstamp 0) (hatch edge 0.508)
  (connect_pads (clearance 0.508))
  (min_thickness 0.01)
  (fill yes (arc_segments 32) (thermal_gap 0.508) (thermal_bridge_width 0.508))
  (polygon
    (pts
      (xy {} {}) (xy {} {}) (xy {} {}) (xy {} {})
    )
  )
)""".format(x2, y2, x1, y2, x1, y1, x2, y1)
    # print(zone, end='')
    out = ""
    for line in zone.split('\n'):
        out += linestart + line + '\n'
        # print(linestart + line)
    return out


def add_fill_zone_polygon(pts, min_thickness=0.01, linestart='  '):
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
"""(zone (net 0) (net_name "") (layer F.Cu) (tstamp 0) (hatch edge 0.508)
  (connect_pads (clearance 0.508))
  (min_thickness 0.01)
  (fill yes (arc_segments 32) (thermal_gap 0.508) (thermal_bridge_width 0.508))
  (polygon
    (pts
      {}
    )
  )
)""".format(pts_str)
    # print(zone, end='')
    out = ""
    for line in zone.split('\n'):
        out += linestart + line + '\n'
        # print(linestart + line)
    return out


def add_boundary(pts, linestart='  '):
    out = ""
    for i in range(len(pts) - 1):
        start = pts[i]
        end = pts[i + 1]
        zone = "(gr_line (start {} {}) (end {} {}) (layer Edge.Cuts) (width 0.05))".format(start[0], start[1],
                                                                                           end[0], end[1])
        # print(line, end='')
        # print(linestart + zone)
        out += linestart + zone + '\n'
    return out


def add_text(txt, center_loc, angleCCW=0, linestart='  '):
    zone = \
"""(gr_text "{}" (at {} {} {}) (layer F.SilkS)
  (effects (font (size 0.5 0.5) (thickness 0.125)))
)""".format(txt, center_loc[0], center_loc[1], angleCCW)
    out = ""
    for line in zone.split('\n'):
        out += linestart + line + '\n'
        # print(linestart + line)
    return out


def add_line(pts, width=0.25, linestart='  '):
    for i in range(len(pts) - 1):
        start = pts[i]
        end = pts[i + 1]
        zone = "(segment (start {} {}) (end {} {}) (width {}) (layer F.Cu) (net 0))".format(start[0], start[1],
                                                                                            end[0], end[1], width)
        # print(linestart + zone)
        return linestart + zone + '\n'


def add_arc(center, radius, start_angle, end_angle, linestart='  '):
    end = (center[0] + radius*np.cos(start_angle),
           center[1] + radius*np.sin(start_angle))
    angle = np.rad2deg(end_angle - start_angle)
    zone = "(gr_arc (start {} {}) (end {} {}) (angle {}) (layer Edge.Cuts) (width {}}))".format(center[0], center[1],
                                                                                                end[0], end[1],
                                                                                                angle,
                                                                                                CUTOUT_WIDTH)
    # print(linestart + zone)
    return linestart + zone + '\n'

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
    (trace_clearance 0.2)
    (zone_clearance 0.508)
    (zone_45_only no)
    (trace_min 0.06)
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

  (net_class Default "This is the default net class."
    (clearance 0.2)
    (trace_width 0.25)
    (via_dia 0.8)
    (via_drill 0.4)
    (uvia_dia 0.3)
    (uvia_drill 0.1)
  )
"""
    # print(zone)
    return zone


def add_footer():
    zone = ")"
    # print(zone)
    return zone
