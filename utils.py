import numpy as np
import matplotlib.pyplot as plt


def generate_line(pt, theta):
    """
    Generate a line of the form Ax + By = C given that it passes through pt with angle CCW to the horizontal axis theta
    :param pt: The point the line passes through
    :param theta: The line's angle CCW to the horizontal axis from pt
    :return: [A, B, C]
    """
    slope = np.tan(theta)
    line = np.array([-slope, 1., pt[1] - pt[0]*slope])
    return line/np.linalg.norm(line[:2])


def generate_perpendicular_line(pt, theta):
    """
    Given that passes through pt with angle CCW to the horizontal axis theta, generate the equation of a line
    perpendicular to it with form Ax + By = C
    :param pt: The point the line passes through
    :param theta: The line's angle CCW to the horizontal axis from pt
    :return: [A, B, C]
    """
    inv_slope = -np.tan(theta)
    if np.isinf(inv_slope):
        slope = -1./np.tan(theta)
        line = np.array([-slope, 1., pt[1] - pt[0]*slope])
    else:
        inv_slope = -np.tan(theta)
        line = np.array([1., -inv_slope, pt[0] - inv_slope*pt[1]])
    return line/np.linalg.norm(line[:2])


def get_intersection(line1, line2):
    A = np.array([[line1[0], line1[1]],
                  [line2[0], line2[1]]])
    b = np.array([[line1[2]],
                  [line2[2]]])
    return np.ndarray.flatten(np.linalg.solve(A, b))


def offset_line(line, r):
    eps = 1e-20
    A, B, C = line
    slope = -A/(B + eps)
    perp_slope = B/(A + eps)
    theta = np.arctan(slope)
    orig_pt = (C/(A + eps), C/(B + eps))
    new_pt1 = (orig_pt[0] + r/np.sqrt(1 + perp_slope**2), orig_pt[1] + perp_slope*r/np.sqrt(1 + perp_slope**2))
    new_pt2 = (orig_pt[0] - r/np.sqrt(1 + perp_slope**2), orig_pt[1] - perp_slope*r/np.sqrt(1 + perp_slope**2))
    line1 = generate_line(new_pt1, theta)
    line2 = generate_line(new_pt2, theta)
    return line1, line2


def generate_arc(pt1, pt2, theta1, N):
    x1, y1 = pt1
    x2, y2 = pt2

    line1 = generate_perpendicular_line(pt1, theta1)
    midpoint = np.mean([pt1, pt2], axis=0)
    angle = np.arctan2(y2 - y1, x2 - x1)
    line2 = generate_perpendicular_line(midpoint, angle)
    center = get_intersection(line1, line2)
    radius = np.linalg.norm(center - pt1)

    th1 = np.arctan2(y1 - center[1], x1 - center[0])
    th2 = np.arctan2(y2 - center[1], x2 - center[0])
    pts = [(center[0] + radius*np.cos(t), center[1] + radius*np.sin(t)) for t in np.linspace(th1, th2, N)]
    return pts


def generate_arc_v2(pt1, pt2, theta1, theta2, r, quadrant, N):
    x1, y1 = pt1
    x2, y2 = pt2

    line1 = generate_line(pt1, theta1)
    line2 = generate_line(pt2, theta2)
    line11, line12 = offset_line(line1, r)
    line21, line22 = offset_line(line2, r)
    orig_int = get_intersection(line1, line2)
    pt1 = get_intersection(line11, line21)
    pt2 = get_intersection(line11, line22)
    pt3 = get_intersection(line12, line21)
    pt4 = get_intersection(line12, line22)
    pts = [pt1, pt2, pt3, pt4]

    for pt in pts:
        if quadrant == 1 and (pt[0] > orig_int[0] and pt[1] > orig_int[1]):
            center = pt
        if quadrant == 2 and (pt[0] < orig_int[0] and pt[1] > orig_int[1]):
            center = pt
        if quadrant == 3 and (pt[0] < orig_int[0] and pt[1] < orig_int[1]):
            center = pt
        if quadrant == 4 and (pt[0] > orig_int[0] and pt[1] < orig_int[1]):
            center = pt

    th1 = np.arctan2(y1 - center[1], x1 - center[0])
    th2 = np.arctan2(y2 - center[1], x2 - center[0])
    pts = [(center[0] + r*np.cos(t), center[1] + r*np.sin(t)) for t in np.linspace(th1, th2, N)]
    return pts


if __name__ == '__main__':
    pts = generate_arc_v2(np.array([0, 0]), np.array([1, 0]), np.pi/2, np.pi/2, 10)
    print(pts)
    plt.plot([x[0] for x in pts], [x[1] for x in pts])
    print('-----------')
    pts = generate_arc_v2(np.array([0, 0]), np.array([0, 1]), 0, 10)
    print(pts)
    plt.plot([x[0] for x in pts], [x[1] for x in pts])
    print('-----------')
    pts = generate_arc_v2(np.array([0, 0]), np.array([0, 1]), np.pi/4, 10)
    print(pts)
    plt.plot([x[0] for x in pts], [x[1] for x in pts])
    print('-----------')
    pts = generate_arc_v2(np.array([1, 0]), np.array([-1, 0]), np.pi/4, 10)
    print(pts)
    plt.plot([x[0] for x in pts], [x[1] for x in pts])
    print('-----------')
    pt = (0, 0)
    theta = np.pi/2
    r = 1
    line = generate_line(pt, theta)
    line1, line2 = offset_line(line, r)
    print(line)
    print(line1, line2)
    # plt.show()
