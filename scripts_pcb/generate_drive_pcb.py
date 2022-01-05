import numpy as np

import pcb_layout
from pcb_layout import *
from pcb_layout_plus_dxf import *
from datetime import datetime


def create_drive_pcb_layout(p: PCBPattern):
    net_names, net_classes, net_strings = generate_nets()
    print(net_names)
    print(net_classes)
    print(net_strings)
    teensy_digital_pins, teensy_3V3_pins, teensy_GND_pins, teensy_Vin_pin, teensy_extra_pins = teensy_pin_mapping()

    # Transistor dimensions
    STB12NM60N_angle = 90
    R1_dy = -12.5  # relative to center of transistor
    R2_dx = -1.55
    R2_dy = 15  # relative to center of transistor
    R1_angle = 90
    R2_angle = 180
    STB12NM60N_pad_dx = [-9, 9]  # relative to center of transistor
    STB12NM60N_pad_dy = [R1_dy, 6]  # relative to center of transistor

    # Transistor array dimensions
    nx, ny = 10, 4
    STB12NM60N_array_spacing_dx = 20
    STB12NM60N_array_spacing_dy = 36

    # Teensy dimensions
    teensy_center_pt = (-30, 120/2)

    # Extra dimensions
    pin_header_start_y = -15
    pin_header_spacing_y = 20
    pin_header_spacing = 2.54

    for i in range(ny):
        y_buffer = 0 if i < ny//2 else 3  # pushes the bottom 2 rows down a bit
        sgn_y = 1 if i < ny//2 else -1
        STB12NM60N_angle_eff = STB12NM60N_angle if i < ny//2 else (STB12NM60N_angle + 180)%360
        R1_angle_eff = R1_angle if i < ny//2 else (R1_angle + 180)%360
        # R2_angle_eff = R2_angle if i < ny//2 else (R2_angle + 180)%360
        R2_angle_eff = R2_angle

        STB12NM60N_pad_1 = STB12NM60N_pad_locations((0, 0), 1, angle=STB12NM60N_angle_eff)
        STB12NM60N_pad_2 = STB12NM60N_pad_locations((0, 0), 2, angle=STB12NM60N_angle_eff)
        STB12NM60N_pad_3 = STB12NM60N_pad_locations((0, 0), 3, angle=STB12NM60N_angle_eff)
        R1_pad1_loc = resistor1206_pad_locations((0, R1_dy), 1, angle=R1_angle)
        R1_pad2_loc = resistor1206_pad_locations((0, R1_dy), 2, angle=R1_angle)
        R2_pad1_loc = resistor1206_pad_locations((STB12NM60N_pad_1[0] + R2_dx, R2_dy), 1, angle=R2_angle_eff)
        print(R1_pad1_loc)
        R2_pad2_loc = resistor1206_pad_locations((STB12NM60N_pad_1[0] + R2_dx, R2_dy), 2, angle=R2_angle_eff)
        # print(R1_pad1_loc, R1_pad2_loc, R2_pad1_loc, R2_pad2_loc)
        # print(i, sgn_y, STB12NM60N_angle_eff, R1_angle_eff, R2_angle_eff)
        for j in range(nx):
            idx = nx*i + j + 1
            center_pt = (STB12NM60N_array_spacing_dx*j, STB12NM60N_array_spacing_dy*i + y_buffer)
            pad1_loc = (center_pt[0] + STB12NM60N_pad_1[0], center_pt[1] + STB12NM60N_pad_1[1])
            pad3_loc = (center_pt[0] + STB12NM60N_pad_3[0], center_pt[1] + STB12NM60N_pad_3[1])
            net_transistor_to_R1 = net_strings["/OUT_" + str(i + 1) + str(j + 1)]
            net_transistor_to_R2 = net_strings['"Net-(Q{}-Pad1)"'.format(idx)]
            net_GND = net_strings["/GND"]
            net_HV = net_strings["/HV"]
            net_CTRL = net_strings["/CTRL_" + str(i + 1) + str(j + 1)]
            transistor_reference = "U" + str(i + 1) + str(j + 1)
            R1_reference = "R" + str(i + 1) + str(j + 1) + "_1"
            R2_reference = "R" + str(i + 1) + str(j + 1) + "_2"
            p.add_STB12NM60N(center_pt=center_pt, angle=STB12NM60N_angle_eff, net_drain=net_transistor_to_R1,
                             net_source=net_GND, net_gate=net_transistor_to_R2, reference=transistor_reference)
            p.add_resistor_1206(center_pt=(center_pt[0], center_pt[1] + sgn_y*R1_dy), angle=R1_angle_eff, reference=R1_reference,
                                net1=net_transistor_to_R1, net2=net_HV, value="5M")
            p.add_resistor_1206(center_pt=(pad1_loc[0] + R2_dx, center_pt[1] + sgn_y*R2_dy), angle=R2_angle_eff,
                                reference=R2_reference, net1=net_transistor_to_R2, net2=net_CTRL, value="1k")

            # Add traces
            p.add_trace(pts=[center_pt, (center_pt[0] + R1_pad1_loc[0], center_pt[1] + sgn_y*R1_pad1_loc[1])], width=0.5)
            p.add_trace(pts=[pad1_loc, (center_pt[0] + R2_pad1_loc[0], center_pt[1] + sgn_y*R2_pad1_loc[1])], width=0.5)

            # Add pad on transistor drains
            p.add_fill_zone_rectangle(
                topleft=(center_pt[0] + STB12NM60N_pad_dx[0], center_pt[1] + sgn_y*STB12NM60N_pad_dy[1]),
                bottomright=(center_pt[0] + STB12NM60N_pad_dx[1], center_pt[1] + sgn_y*STB12NM60N_pad_dy[0]),
                net=net_transistor_to_R1)

            # Add via for transistor drain (output)
            via_pt = (center_pt[0] + STB12NM60N_pad_dx[1]/2, center_pt[1] + sgn_y*R1_dy*4/5)
            p.add_via(pt=via_pt, net=net_transistor_to_R1)

            # Add vias to transistor ground
            via_pt = (center_pt[0] + sgn_y*STB12NM60N_array_spacing_dx/2, pad3_loc[1])
            p.add_via(pt=via_pt, net=net_strings["/GND"])
            p.add_trace(pts=[pad3_loc, via_pt], width=0.5)

            # Adds vias to HV pad
            via_pt = (via_pt[0], center_pt[1] + sgn_y*(R1_dy - 1.55))
            p.add_via(pt=via_pt, net=net_strings["/HV"])
            p.add_trace(pts=[(center_pt[0], via_pt[1]), via_pt], width=0.5)

        # Add A05P5 voltage supplies
        if i == 0:
            dy = 0
        elif i == 1:
            dy = -7.5
        elif i == 2:
            dy = 10
        elif i == 3:
            dy = -7.5
        PS_loc = (-20, STB12NM60N_array_spacing_dy*i + sgn_y*(R1_dy - 1.55 - 1.57) + dy)
        p.add_A05P5(PS_loc, 0, "PS" + str(i + 1),
                    net_Vin_plus=net_strings["/HV_Vin"], net_Vin_minus=net_strings["/GND"],
                    net_Vctrl=net_strings["/HV_CTRL"], net_Vout_plus=net_strings["/HV"],
                    net_Vout_minus=net_strings["/GND"])

        # Add pins for power supplies
        net_names_PS = [net_strings["/HV_Vin"], net_strings["/GND"], net_strings["/HV_CTRL"]]
        refs = ["HV_Vin", "GND", "HV_CTRL"]
        ref_loc = (2.55, 0)
        for j, data in enumerate(zip(net_names_PS, refs)):
            net_name, ref = data
            pin_loc = (PS_loc[0] - 25, PS_loc[1] + 5*j)
            p.add_pin_header(pin_loc, net_names=net_name, references=ref, ref_loc=ref_loc)
        pin_loc = (PS_loc[0] + 7.5, PS_loc[1] + 1.57)
        p.add_pin_header(pin_loc, net_names=net_strings["/HV"], references="HV", ref_loc=ref_loc)

        # Add pin headers
        out_nets = [net_strings["/OUT_" + str(i + 1) + str(j + 1)] for j in range(nx)]
        shuffle = lambda arr, new_idx: [arr[i] for i in new_idx]
        # out_nets = shuffle(out_nets, [0, 5, 1, 6, 2, 7, 3, 8, 4, 9])
        out_nets = shuffle(out_nets, [5, 4, 6, 3, 7, 2, 8, 1, 9, 0])
        dy = i*pin_header_spacing_y if i%2 == 0 else ((i-1)*pin_header_spacing_y + (nx//2)*2.54)
        p.add_pin_header(
            top_left_pt=(STB12NM60N_array_spacing_dx*nx, pin_header_start_y + dy),
            nx=2, ny=5, spacing=2.54, net_names=out_nets)
        for idx in range(nx):
            if idx%2 == 0:
                pt = (STB12NM60N_array_spacing_dx*nx - pin_header_spacing,
                      pin_header_start_y + dy + (idx//2)*2.54)
                pin_pt = (pt[0] + pin_header_spacing, pt[1])
                ref_loc = (-2.25, 0)
            else:
                pt = (STB12NM60N_array_spacing_dx*nx + 2*pin_header_spacing,
                      pin_header_start_y + dy + (idx//2)*2.54)
                pin_pt = (pt[0] - pin_header_spacing, pt[1])
                ref_loc = (2.25, 0)
            p.add_pin_header(pt, net_names=out_nets[idx], references=out_nets[idx].split("_")[1], ref_loc=ref_loc)
            p.add_trace([pin_pt, pt], width=0.5, layer="B.Cu")

        # Adds a high voltage pad (actually a trace, so it doesn't interfere with the ground pad)
        left_x, right_x = STB12NM60N_pad_dx[0], STB12NM60N_array_spacing_dx*(nx - 1) + STB12NM60N_pad_dx[1]
        top_y = STB12NM60N_array_spacing_dy*i + y_buffer + sgn_y*STB12NM60N_pad_dy[0]
        bottom_y = top_y - sgn_y*125*MIL_TO_MM
        mid = (top_y + bottom_y)/2
        p.add_trace([(left_x, mid), (right_x, mid)], width=abs(top_y-bottom_y), layer="B.Cu")
        # p.add_fill_zone_rectangle((left_x, top_y), (right_x, bottom_y), net_strings["/HV"], layer="B.Cu")

    # Add Teensy
    teensy_digital_pins, teensy_3V3_pins, teensy_GND_pins, teensy_Vin_pin, teensy_extra_pins = teensy_pin_mapping()
    teensy_nets = []
    count_io = 0
    for i in range(1, 68):
        if (i in teensy_extra_pins) or (i == teensy_Vin_pin) or (i == 12) or (i == 13):
            teensy_nets += [net_strings['"Net-(U1-Pad{})"'.format(i)]]
        elif i in teensy_digital_pins:
            ix = count_io//nx + 1
            iy = count_io%nx + 1
            if ix == 1:  # swap order of 1
                iy = nx + 1 - iy
            if ix == 2:  # swap 2 with 4
                ix = 4
                iy = nx + 1 - iy
            elif ix == 3:  # swap 3 with 4
                ix = 3
            elif ix == 4:  # swap 4 with 2
                ix = 2
                iy = nx + 1 - iy
            teensy_nets += [net_strings["/CTRL_" + str(ix) + str(iy)]]
            count_io += 1
        elif i in teensy_3V3_pins:
            teensy_nets += [net_strings["/3V3"]]
        elif i in teensy_GND_pins:
            teensy_nets += [net_strings["/GND"]]
    p.add_teensy41(teensy_center_pt, 270, "Q1", teensy_nets)
    print(teensy_nets)

    # Add pins on either side of Teensy
    for i in range(1, 48 + 1):
        pad_loc = teensy_pad_locations(teensy_center_pt, i, angle=270)
        net_name = teensy_nets[i - 1]
        if i <= 24:
            pin_loc = (pad_loc[0] - pin_header_spacing, pad_loc[1])
            ref_loc = (-2.25, 0)
        else:
            pin_loc = (pad_loc[0] + pin_header_spacing, pad_loc[1])
            ref_loc = (2.25, 0)
        if "CTRL" in net_name:
            ref = net_name.split("_")[1]
        elif "Net" in net_name:
            ref = "_"
        else:
            ref = net_name[-3:]
        # ref = net_name[-2:] if ("OUT" in net_name) else ""
        p.add_pin_header(pin_loc, net_names=net_name, references=ref, ref_loc=ref_loc)
        # p.add_via(pin_loc, size=1.6, drill=1.1, net=net_name)
        p.add_trace([pad_loc, pin_loc], width=6*MIL_TO_MM)

    return p


def generate_nets():
    net_names = ["/GND", "/HV", "/HV_CTRL", "/HV_Vin", "/3V3"]
    net_classes = [1, 1, 1, 1, 1]

    # Add control wires for all the transistors
    for i in range(40):
        net_names += ["/CTRL_" + str(i//10 + 1) + str(i%10 + 1)]
        net_classes += [0]

    for i in range(40):
        net_names += ['"Net-(Q{}-Pad1)"'.format(i + 1),
                      "/OUT_" + str(i//10 + 1) + str(i%10 + 1)]  # Pad1 = gate, Pad2 = drain
        net_classes += [1, 1]

    # Add nets for all the Teensy connections that don't have an active use
    teensy_digital_pins, teensy_3V3_pins, teensy_GND_pins, teensy_Vin_pin, teensy_extra_pins = teensy_pin_mapping()
    for i in range(1, 68):
        # if (i in teensy_extra_pins) or (i == 48) or (i == 14) or (i == 35):
        if (i in teensy_extra_pins) or (i == teensy_Vin_pin) or (i == 12) or (i == 13):
            net_names += ['"Net-(U1-Pad{})"'.format(i)]
            net_classes += [0]

    # Add a random net for miscellaneous test connections
    net_names += ["Test"]
    net_classes += [1]

    net_strings = {net: str(i + 1) + " " + net for i, net in enumerate(net_names)}
    return net_names, net_classes, net_strings


def add_teensy(pt, angle):
    teensy_digital_pins, teensy_3V3_pins, teensy_GND_pins, teensy_Vin_pin, teensy_extra_pins = teensy_pin_mapping()


def teensy_pin_mapping():
    teensy_digital_pins = [2 + i for i in range(13)]  # pins 0-12
    teensy_digital_pins += [16 + i for i in range(9)]  # pins 42-32
    teensy_digital_pins += [25 + i for i in range(9)]
    teensy_digital_pins += [35 + i for i in range(11)]

    teensy_3V3_pins = [15, 46]
    teensy_GND_pins = [1, 34, 47]
    teensy_Vin_pin = 48
    teensy_extra_pins = list(range(49, 68))

    return teensy_digital_pins, teensy_3V3_pins, teensy_GND_pins, teensy_Vin_pin, teensy_extra_pins


def teensy_pad_locations(center_loc, pad, angle=0):
    dx = -29.21 + 2.54*((pad - 1)%24) if pad <= 24 else -29.21 + 2.54*((24 - pad)%24)
    dy = 7.62 if pad <= 24 else -7.62
    angle = np.deg2rad(angle)
    dx, dy = np.cos(angle)*dx + np.sin(angle)*dy, -np.sin(angle)*dx + np.cos(angle)*dy
    return (center_loc[0] + dx, center_loc[1] + dy)


def STB12NM60N_pad_locations(center_loc, pad, angle=0):
    if pad == 1:
        dx = -2.54
        dy = 10.275
    elif pad == 2:
        dx = dy = 0
    elif pad == 3:
        dx = 2.54
        dy = 10.275
    angle = np.deg2rad(angle - 90)
    dx, dy = np.cos(angle)*dx + np.sin(angle)*dy, -np.sin(angle)*dx + np.cos(angle)*dy
    return (center_loc[0] + dx, center_loc[1] + dy)


def resistor1206_pad_locations(center_loc, pad, angle=0):
    if pad == 1:
        dx = -1.55
    elif pad == 2:
        dx = 1.55
    dy = 0
    angle = np.deg2rad(angle)
    dx, dy = np.cos(angle)*dx + np.sin(angle)*dy, -np.sin(angle)*dx + np.cos(angle)*dy
    return (center_loc[0] + dx, center_loc[1] + dy)


if __name__ == '__main__':
    now = datetime.now()
    name_clarifier = "_drive_pcb"
    timestamp = now.strftime("%Y%m%d_%H_%M_%S") + name_clarifier
    print(timestamp)

    net_names, net_classes, net_strings = generate_nets()
    p = PCBPattern()
    p = create_drive_pcb_layout(p)

    # Create edge cuts
    left_x, right_x = -50, 210
    bottom_y, top_y = -20, 130
    p.add_graphic_line(pts=[(left_x, bottom_y), (left_x, top_y), (right_x, top_y), (right_x, bottom_y),
                            (left_x, bottom_y)], layer="Edge.Cuts")
    # Add ground plane
    p.add_fill_zone_rectangle((left_x, top_y), (right_x, bottom_y), net_strings["/GND"], layer="B.Cu")

    # p.add_A05P5((0, 0), 0, "PS1", net_Vin_plus=net_strings["/HV_Vin"], net_Vin_minus=net_strings["/GND"], net_Vctrl=net_strings["/HV_CTRL"], net_Vout_plus=net_strings["/HV"], net_Vout_minus=net_strings["/GND"])

    x_buffer = -left_x
    y_buffer = -bottom_y
    print("Size X, Size Y:", right_x - left_x, ", ", top_y - bottom_y)

    kicad_filename = "C:/Users/ahadrauf/Desktop/Research/pcb_wire_testing_setup/drive_circuit/pcb_drive_circuit/pcb_drive_circuit.kicad_pcb"
    # dxf_cut_filename = "C:/Users/ahadrauf/Desktop/Research/pcb_wire_testing_setup/pcb_wire_testing_setup_cut.dxf"
    # dxf_etch_filename = "C:/Users/ahadrauf/Desktop/Research/pcb_wire_testing_setup/pcb_wire_testing_setup_etch.dxf"
    p.generate_kicad(kicad_filename, save=True, offset_x=x_buffer, offset_y=y_buffer, net_names=net_names,
                     net_classes=net_classes, default_linewidth=6*MIL_TO_MM)
