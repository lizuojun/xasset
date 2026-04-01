import math


# 计算点到直线的投影点，projected_pt_on_line保证该投影点是否一定在line上
def compute_pt_project_line(pt, base_line, projected_pt_on_line=True):
    base_pt = base_line[0]
    pt_change = [pt[0] - base_pt[0],  pt[1] - base_pt[1]]
    line_change = [[base_line[0][0] - base_pt[0], base_line[0][1] - base_pt[1]],
                   [base_line[1][0] - base_pt[0], base_line[1][1] - base_pt[1]]]

    t = (line_change[1][0] * pt_change[0] + line_change[1][1] * pt_change[1]) / (line_change[1][0]**2 + line_change[1][1]**2)

    if projected_pt_on_line:
        if t < 0:
            t = 0
        elif t > 1:
            t = 1

    return [line_change[1][0]*t + base_pt[0], line_change[1][1]*t + base_pt[1]]


# 将projected_line投影到base_line上, 计算投影后的长度，根据两条边的平均距离, 以及平移向量(从projected_line移动到base_line的向量)
def compute_line_line_project_length_and_dis(projected_line, base_line):
    projected_pt_0 = compute_pt_project_line(projected_line[0], base_line, projected_pt_on_line=True)
    projected_pt_1 = compute_pt_project_line(projected_line[1], base_line, projected_pt_on_line=True)

    line_length = math.sqrt((projected_pt_0[0]-projected_pt_1[0])**2 + (projected_pt_0[1]-projected_pt_1[1])**2)
    dis_0 = math.sqrt((projected_pt_0[0] - projected_line[0][0]) ** 2 + (projected_pt_0[1] - projected_line[0][1]) ** 2)
    dis_1 = math.sqrt((projected_pt_1[0] - projected_line[1][0]) ** 2 + (projected_pt_1[1] - projected_line[1][1]) ** 2)

    projected_pt_offset_0 = compute_pt_project_line(projected_line[0], base_line, projected_pt_on_line=False)
    projected_pt_offset_1 = compute_pt_project_line(projected_line[1], base_line, projected_pt_on_line=False)
    offset_vec_0 = [projected_pt_offset_0[0] - projected_line[0][0], projected_pt_offset_0[1] - projected_line[0][1]]
    offset_vec_1 = [projected_pt_offset_1[0] - projected_line[1][0], projected_pt_offset_1[1] - projected_line[1][1]]

    return line_length, 0.5*(dis_0+dis_1), \
           [0.5*(offset_vec_0[0]+offset_vec_1[0]), 0.5*(offset_vec_0[1]+offset_vec_1[1])]


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


