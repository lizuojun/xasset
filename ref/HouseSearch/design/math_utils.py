
def check_same_pt(p1, p2, e=1e-5):
    if len(p1) == 0 or len(p2) == 0:
        return True

    a = [(p1[i] - p2[i])**2 for i in range(len(p1))]
    return sum(a) < e**2


def check_on_line(pt, line):
    p1, p2 = line
    if check_same_pt(p1, p2, 1e-5):
        if check_same_pt(p1, pt, 1e-5):
            return True
        else:
            return False
    pf = pt
    cross = (p2[0] - p1[0]) * (pf[0] - p1[0]) + (p2[1] - p1[1]) * (pf[1] - p1[1])
    if cross < 0:
        return False
    d2 = (p2[0] - p1[0]) * (p2[0] - p1[0]) + (p2[1] - p1[1]) * (p2[1] - p1[1])

    if abs(d2) < 0.0001:
        return False

    if cross > d2:
        return False
    r = cross / d2
    px = p1[0] + (p2[0] - p1[0]) * r
    py = p1[1] + (p2[1] - p1[1]) * r

    return ((pf[0] - px) * (pf[0] - px) + (py - pf[1]) * (py - pf[1])) <= 0.0001


# on_line_flag 当点在线上时 返回True/False
def check_pt_in_poly(pt, poly_pts, on_line_flag=False):
    n_cross = 0
    for idx, _ in enumerate(poly_pts[:-1]):
        p1 = poly_pts[idx]
        p2 = poly_pts[idx + 1]

        if check_on_line(pt, [p1, p2]):
            return on_line_flag

        if abs(p1[1] - p2[1]) < 0.01:
            continue
        if pt[1] < min(p1[1], p2[1]):
            continue
        if pt[1] >= max(p1[1], p2[1]):
            continue
        x = (pt[1] - p1[1]) * (p2[0] - p1[0]) / (p2[1] - p1[1]) + p1[0]
        if x > pt[0]:
            n_cross += 1
    if n_cross % 2 == 1:
        return True
    else:
        return False


def check_pt_on_poly(pt, poly_pts):
    for idx, _ in enumerate(poly_pts[:-1]):
        p1 = poly_pts[idx]
        p2 = poly_pts[idx + 1]

        if check_on_line(pt, [p1, p2]):
            return True

    return False

