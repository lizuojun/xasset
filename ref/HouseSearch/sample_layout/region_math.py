import math


# 顺逆时针无所谓
# poly_pts 格式 [[x_0,y_0], [x_1,y_1], [x_2,y_2], ....] 首尾点不相等
# floor/pts 格式 [x0, y0, x1, y1, x2, y2, ...., x0, y0] # 首尾点相等


# 判断点在线上
def check_on_line(pt, line):
    """
    是否在线段上, 边界点判断包含

    :param pt: 输入点, 格式[x0, y0]
    :param line: 输入线段, 格式[[x0, y0], [x1, y1]】
    :return: True/False
            check_on_line([0.0, 0.0], [[0.0, 0.0], [0.0, 1.0]]) >> True
            check_on_line([0.0, -0.1], [[0.0, 0.0], [0.0, 1.0]]) >> False
    """
    p1, p2 = line
    pf = pt
    cross = (p2[0] - p1[0]) * (pf[0] - p1[0]) + (p2[1] - p1[1]) * (pf[1] - p1[1])
    if cross < 0:
        return False
    d2 = (p2[0] - p1[0]) * (p2[0] - p1[0]) + (p2[1] - p1[1]) * (p2[1] - p1[1])
    if cross > d2:
        return False
    r = cross / d2
    px = p1[0] + (p2[0] - p1[0]) * r
    py = p1[1] + (p2[1] - p1[1]) * r
    return ((pf[0] - px) * (pf[0] - px) + (py - pf[1]) * (py - pf[1])) <= 0.01


# on_line_flag 当点在多边形边上时 返回True/False
def check_pt_in_poly(pt, poly_pts, on_line_flag=False):
    """
    检查点 pt 是否在多边形 poly_pts 内部

    :param pt: 输入点 [x0, y0]
    :param poly_pts: 多边形格式 poly_pts = [[x0, y0], [x1, y1], [x2, y2]....]
    :param on_line_flag: 当点在多边形边上时 返回True/False
    :return: True/False
    """
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


# 计算点到直线的投影点，projected_pt_on_line保证该投影点是否一定在line上
def compute_pt_project_line(pt, base_line, projected_pt_on_line=True):
    """

    :param pt: 输入点 [x0, y0]
    :param base_line: 被投影线段 [[x0, y0], [x1, y1]]
    :param projected_pt_on_line: 保证该投影点是否一定在line上
    :return: 投影点 [x0, y0]
    """
    base_pt = base_line[0]
    pt_change = [pt[0] - base_pt[0], pt[1] - base_pt[1]]
    line_change = [[base_line[0][0] - base_pt[0], base_line[0][1] - base_pt[1]],
                   [base_line[1][0] - base_pt[0], base_line[1][1] - base_pt[1]]]

    t = (line_change[1][0] * pt_change[0] + line_change[1][1] * pt_change[1]) / (
            line_change[1][0] ** 2 + line_change[1][1] ** 2)

    if projected_pt_on_line:
        if t < 0:
            t = 0
        elif t > 1:
            t = 1

    return [line_change[1][0] * t + base_pt[0], line_change[1][1] * t + base_pt[1]]


# 将projected_line投影到base_line上, 计算投影后的长度，根据两条边的平均距离, 以及平移向量(从projected_line移动到base_line的向量)
def compute_line_line_project_length_and_dis(projected_line, base_line):
    projected_pt_0 = compute_pt_project_line(projected_line[0], base_line, projected_pt_on_line=True)
    projected_pt_1 = compute_pt_project_line(projected_line[1], base_line, projected_pt_on_line=True)

    line_length = math.sqrt((projected_pt_0[0] - projected_pt_1[0]) ** 2 + (projected_pt_0[1] - projected_pt_1[1]) ** 2)
    dis_0 = math.sqrt((projected_pt_0[0] - projected_line[0][0]) ** 2 + (projected_pt_0[1] - projected_line[0][1]) ** 2)
    dis_1 = math.sqrt((projected_pt_1[0] - projected_line[1][0]) ** 2 + (projected_pt_1[1] - projected_line[1][1]) ** 2)

    projected_pt_offset_0 = compute_pt_project_line(projected_line[0], base_line, projected_pt_on_line=False)
    projected_pt_offset_1 = compute_pt_project_line(projected_line[1], base_line, projected_pt_on_line=False)
    offset_vec_0 = [projected_pt_offset_0[0] - projected_line[0][0], projected_pt_offset_0[1] - projected_line[0][1]]
    offset_vec_1 = [projected_pt_offset_1[0] - projected_line[1][0], projected_pt_offset_1[1] - projected_line[1][1]]

    return line_length, 0.5 * (dis_0 + dis_1), \
           [0.5 * (offset_vec_0[0] + offset_vec_1[0]), 0.5 * (offset_vec_0[1] + offset_vec_1[1])]


# 返回两条边的夹角余弦值
def compute_line_line_cos_angle(line_one, line_two):
    line_one_base = [line_one[1][0] - line_one[0][0], line_one[1][1] - line_one[0][1]]

    line_two_base = [line_two[1][0] - line_two[0][0], line_two[1][1] - line_two[0][1]]

    line_one_norm = math.sqrt(line_one_base[0] ** 2 + line_one_base[1] ** 2)
    line_two_norm = math.sqrt(line_two_base[0] ** 2 + line_two_base[1] ** 2)

    if line_one_norm < 0.001 or line_two_norm < 0.001:
        return -1

    line_one_base = [line_one_base[0] / line_one_norm, line_one_base[1] / line_one_norm]
    line_two_base = [line_two_base[0] / line_two_norm, line_two_base[1] / line_two_norm]

    return line_one_base[0] * line_two_base[0] + line_one_base[1] * line_two_base[1]


if __name__ == '__main__':
    print(check_on_line([0.0, 0.0], [[0.0, 0.0], [0.0, 1.0]]))
    print(check_on_line([0.0, -0.1], [[0.0, 0.0], [0.0, 1.0]]))
