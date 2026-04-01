import math

from HouseSearch.design.math_utils import check_pt_in_poly
from HouseSearch.sample_refine.math_utils import compute_line_line_cos_angle, compute_line_line_project_length_and_dis
from HouseSearch.util import rot_to_ang

PI = 3.1415926


# 返回对应的group跟zone type
def get_group_zone_type(name):
    if name == "Meeting":
        return "Meeting", ""

    elif name == "Dining":
        return "Dining", ""

    elif name == "Media":
        return "Media", ""

    elif name == "Cabinet":
        return "Cabinet", ""

    elif name == "Hallway":
        return "Cabinet", "Hallway"

    elif name == "DiningCabinet":
        return "Cabinet", "DiningRoom"

    elif name == "Bed":
        return "Bed", ""

    elif name == "Armoire":
        return "Armoire", ""

    elif name == "Work":
        return "Work", "Library"

    else:
        return "Rest", ""


def compute_line_project_poly_parallel_line_dis(rect_line, floor_poly):
    min_dis = 1000.
    min_dis_project_length = 0.
    min_dis_project_vec = [0.0, 0.0]
    min_idx = -1
    min_dis_ploy_line = []

    num_floor_pts = len(floor_poly)
    for floor_line_idx in range(len(floor_poly)):
        floor_line = [floor_poly[floor_line_idx], floor_poly[(floor_line_idx + 1) % num_floor_pts]]

        # 只计算平行的或夹角小的
        if compute_line_line_cos_angle(rect_line, floor_line) > 0.7:
            length, dis, vec = compute_line_line_project_length_and_dis(rect_line, floor_line)

            # 有投影重合的最近距离
            if dis < min_dis and length > 0:
                min_dis = dis
                min_dis_project_length = length
                min_dis_project_vec = vec
                min_dis_ploy_line = floor_line

    return min_dis, min_dis_project_length, min_dis_project_vec, min_dis_ploy_line


def refine_group_rotation(group_data, floor_poly):
    half_size_x, half_size_y = group_data["size"][0] / 2., group_data["size"][2] / 2.
    left_top_pt = [group_data["position"][0] - half_size_x, group_data["position"][2] - half_size_y]
    right_bottom_pt = [group_data["position"][0] + half_size_x, group_data["position"][2] + half_size_y]

    left_bottom_pt = [left_top_pt[0], right_bottom_pt[1]]
    right_top_pt = [right_bottom_pt[0], left_top_pt[1]]

    key_point_list = [right_top_pt, left_top_pt, left_bottom_pt, right_bottom_pt, right_top_pt]

    # 判断在多边形中
    in_floor_pts_index = []
    for pt in key_point_list:
        in_floor_pts_index.append(check_pt_in_poly(pt, floor_poly, False))

    # 计算rect每条边到poly平行线段最近距离
    project_len_list = []
    for rect_line_idx in range(len(key_point_list) - 1):
        rect_line = [key_point_list[rect_line_idx], key_point_list[rect_line_idx + 1]]
        dis, project_length, vec, poly_line = compute_line_project_poly_parallel_line_dis(rect_line, floor_poly)
        project_len_list.append({"dis": dis, "p_len": project_length, "vec": vec, "line": poly_line})

    # 四条边选一个作为主方向
    # 先判断是x方向 y方向 的可能结果
    x_line_info_idx = 0
    if project_len_list[0]["dis"] > project_len_list[2]["dis"]:
        x_line_info_idx = 2

    y_line_info_idx = 1
    if project_len_list[1]["dis"] > project_len_list[3]["dis"]:
        y_line_info_idx = 3
    # 修复 media
    wall_attach = project_len_list[x_line_info_idx]["dis"] < 0.1 or project_len_list[y_line_info_idx]["dis"] < 0.1
    # 配置靠墙(床、工作区、电视区)、靠墙为主方向、
    if wall_attach and group_data["type"] in ["Bed", "Work"]:
        if project_len_list[x_line_info_idx]["dis"] < project_len_list[y_line_info_idx]["dis"]:
            rot_line_idx = x_line_info_idx

        else:
            rot_line_idx = y_line_info_idx
    else:
        # 长边为主方向
        if project_len_list[x_line_info_idx]["p_len"] > project_len_list[y_line_info_idx]["p_len"]:
            rot_line_idx = x_line_info_idx
        else:
            rot_line_idx = y_line_info_idx

        # 新增 玄关柜处理
        if group_data["zone"] == "Hallway" and group_data["type"] == "Cabinet":
            # 单边靠墙
            if project_len_list[rot_line_idx]["dis"] < 0.15:
                group_data["back_on_wall"] = True
            else:
                group_data["back_on_wall"] = False

    # 靠边处理
    near_wall = False
    if project_len_list[rot_line_idx]["dis"] < 0.3:
        near_wall = True
        group_data["position"][0] += project_len_list[rot_line_idx]["vec"][0]
        group_data["position"][2] += project_len_list[rot_line_idx]["vec"][1]

    # 距离近时直接靠墙
    elif project_len_list[rot_line_idx]["dis"] < 0.6 and group_data["type"] in ["Media", "Meeting", "Cabinet", "Bed"]:
        near_wall = True
        group_data["position"][0] += project_len_list[rot_line_idx]["vec"][0]
        group_data["position"][2] += project_len_list[rot_line_idx]["vec"][1]

    # 柜子逻辑处理/侧边靠墙问题
    if group_data["type"] in ["Cabinet"] and project_len_list[rot_line_idx]["dis"] > 0.6:
        if project_len_list[(rot_line_idx-1) % 4]["dis"] < project_len_list[(rot_line_idx+1) % 4]["dis"]:
            _near_wall_idx = (rot_line_idx-1) % 4
        else:
            _near_wall_idx = (rot_line_idx + 1) % 4
        if project_len_list[_near_wall_idx]["dis"] < 0.6:
            group_data["position"][0] += project_len_list[_near_wall_idx]["vec"][0]
            group_data["position"][2] += project_len_list[_near_wall_idx]["vec"][1]

    rot_ang_list = [0, PI / 2., PI, -PI / 2.]
    if rot_line_idx in [1, 3]:
        group_data["size"][2], group_data["size"][0] = group_data["size"][0], group_data["size"][2]

    rot_ang = rot_ang_list[rot_line_idx]
    group_data["rotation"] = [0, math.sin(rot_ang / 2.), 0, math.cos(rot_ang / 2.)]

    # 已经靠边处理
    if near_wall:
        group_data["back_rely_line"] = project_len_list[rot_line_idx]["line"]
    else:
        group_data["back_rely_line"] = []


def update_group_list_rotation(zone_list, entry_door_info=None):
    # 检查meeting media的朝向
    meeting = None
    media = None
    bed = None
    hallway_cabinet = None

    for zone in zone_list:
        if zone["type"] == "Meeting":
            meeting = zone
        elif zone["type"] == "Media":
            media = zone
        elif zone["type"] == "Bed":
            bed = zone
        elif zone["type"] == "Bed":
            bed = zone
        elif zone["type"] == "Cabinet" and zone["zone"] == "Hallway":
            hallway_cabinet = zone

    # 处理床悬空的朝向
    if bed and media:
        s = [abs(bed["rotation"][i] - media["rotation"][i]) for i in range(4)]
        # if sum(s) > 0.1:
        #     pass
        # else:
        ang = rot_to_ang(media["rotation"]) + PI
        bed["rotation"] = [0, math.sin(ang / 2.), 0, math.cos(ang / 2.)]

    # 处理沙发悬空的朝向
    if meeting and media:
        s = [abs(meeting["rotation"][i] - media["rotation"][i]) for i in range(4)]
        # if sum(s) > 0.1:
        #     pass
        # else:
        ang = rot_to_ang(media["rotation"]) + PI
        meeting["rotation"] = [0, math.sin(ang / 2.), 0, math.cos(ang / 2.)]

    # 处理玄关柜的朝向
    if entry_door_info and hallway_cabinet:
        if "back_on_wall" in hallway_cabinet and not hallway_cabinet["back_on_wall"]:
            cabinet_pos = hallway_cabinet["position"]
            door_pt = [0.5 * (entry_door_info["pts"][0] + entry_door_info["pts"][2]),
                       0.5 * (entry_door_info["pts"][1] + entry_door_info["pts"][3])]

            ang = rot_to_ang(hallway_cabinet["rotation"])

            cos_ang = math.cos(ang)
            sin_ang = math.sin(ang)

            base_pt_line = [-sin_ang, cos_ang]
            door_cabinet_line = [cabinet_pos[0] - door_pt[0], cabinet_pos[2] - door_pt[1]]
            door_cabinet_line_norm = math.sqrt(door_cabinet_line[0] ** 2 + door_cabinet_line[1] ** 2) + 0.001
            door_cabinet_line_norm = [door_cabinet_line[0] / door_cabinet_line_norm,
                                      door_cabinet_line[1] / door_cabinet_line_norm]

            # 判断玄关朝向向量与到门向量的夹角, 如果方向相反, 纠正
            if door_cabinet_line_norm[0] * base_pt_line[0] + door_cabinet_line_norm[1] * base_pt_line[1] < 0:
                hallway_cabinet["rotation"] = [0, math.sin(-ang / 2.), 0, math.cos(-ang / 2.)]


def draw_zone_list_process(room_data):
    zone_list = []
    room_data["region_info"] = []
    # 计算 入户门
    entry_door = None
    for door in room_data["door_info"]:
        if door["to"] == "":
            entry_door = door

    if "floor" not in room_data or len(room_data["floor"]) < 8:
        return

    if "zone_info" not in room_data or len(room_data["zone_info"]) < 1:
        return

    floor_pts = [[room_data["floor"][2 * i], room_data["floor"][2 * i + 1]] for i in
                 range(len(room_data["floor"]) // 2 - 1)]
    for zone in room_data["zone_info"]:
        if "input" in zone and zone["input"] == "draw":
            input_type = zone["type"]
            input_pts = zone["draw_pts"]
            group_name, zone_name = get_group_zone_type(input_type)
            size = [abs(input_pts[1][0] - input_pts[0][0]), 1.5, abs(input_pts[1][1] - input_pts[0][1])]
            pos = [0.5 * (input_pts[1][0] + input_pts[0][0]), 0.0, 0.5 * (input_pts[1][1] + input_pts[0][1])]
            zone_data = {"size": size, "position": pos, "rotation": [0, 0, 0, 1], "scale": [1, 1, 1],
                         "zone": zone_name, "type": group_name}
            refine_group_rotation(zone_data, floor_pts)

            zone_list.append(zone_data)

    update_group_list_rotation(zone_list, entry_door)

    if zone_list:
        room_data["region_info"] = zone_list


def show_room_data(room_data, group_list=None):
    import matplotlib.pyplot as plt
    from Extract.utils import rot_to_ang
    ax = plt.gca()

    ax.invert_yaxis()

    floor_pts = [[room_data["floor"][2 * i], room_data["floor"][2 * i + 1]] for i in
                 range(len(room_data["floor"]) // 2 - 1)]
    x = [i[0] for i in floor_pts] + [floor_pts[0][0]]
    y = [i[1] for i in floor_pts] + [floor_pts[0][1]]

    for group_data in room_data["region_info"]:
        ang = rot_to_ang(group_data["rotation"])
        half_size_x, half_size_y = group_data["size"][0] / 2., group_data["size"][2] / 2.
        if abs(ang - 1.57) < 0.1:
            half_size_x, half_size_y = group_data["size"][2] / 2., group_data["size"][0] / 2.
        if abs(ang + 1.57) < 0.1:
            half_size_x, half_size_y = group_data["size"][2] / 2., group_data["size"][0] / 2.

        left_top_pt = [group_data["position"][0] - half_size_x, group_data["position"][2] - half_size_y]
        right_bottom_pt = [group_data["position"][0] + half_size_x, group_data["position"][2] + half_size_y]

        left_bottom_pt = [left_top_pt[0], right_bottom_pt[1]]
        right_top_pt = [right_bottom_pt[0], left_top_pt[1]]

        key_point_list = [right_top_pt, left_top_pt, left_bottom_pt, right_bottom_pt, right_top_pt]

        if ang < -1.0:
            plt.arrow(group_data["position"][0], group_data["position"][2], -0.5,
                      0.0, width=0.05)
        elif abs(ang - 1.57) < 0.1:
            plt.arrow(group_data["position"][0], group_data["position"][2], 0.5,
                      0.0, width=0.05)
        elif abs(ang - 0.0) < 0.1:
            plt.arrow(group_data["position"][0], group_data["position"][2], 0.0,
                      0.5, width=0.05)
        else:
            plt.arrow(group_data["position"][0], group_data["position"][2], 0.0,
                      -0.5, width=0.05)

        z_x = [i[0] for i in key_point_list]
        z_y = [i[1] for i in key_point_list]

        plt.plot(z_x, z_y, color="red")

    if group_list:
        for group_data in group_list:
            ang = rot_to_ang(group_data["rotation"])
            half_size_x, half_size_y = group_data["size"][0] / 2., group_data["size"][2] / 2.
            if abs(ang - 1.57) < 0.1:
                half_size_x, half_size_y = group_data["size"][2] / 2., group_data["size"][0] / 2.
            if abs(ang + 1.57) < 0.1:
                half_size_x, half_size_y = group_data["size"][2] / 2., group_data["size"][0] / 2.

            left_top_pt = [group_data["position"][0] - half_size_x, group_data["position"][2] - half_size_y]
            right_bottom_pt = [group_data["position"][0] + half_size_x, group_data["position"][2] + half_size_y]

            left_bottom_pt = [left_top_pt[0], right_bottom_pt[1]]
            right_top_pt = [right_bottom_pt[0], left_top_pt[1]]

            key_point_list = [right_top_pt, left_top_pt, left_bottom_pt, right_bottom_pt, right_top_pt]

            z_x = [i[0] for i in key_point_list]
            z_y = [i[1] for i in key_point_list]

            plt.plot(z_x, z_y, color="green")

            group_pos = group_data["position"]
            group_offset = [group_data["offset"][0], group_data["offset"][2]]

            for obj in group_data["obj_list"]:
                if obj["role"] in ["table", "chair", "sofa", "side sofa", "bed", "armoire", "cabinet", "side table"]:
                    obj_source_ang = rot_to_ang(obj["normal_rotation"])
                    ang_final = obj_source_ang + ang
                    half_obj_size_x, half_obj_size_y = obj["size"][0] * obj["scale"][0] / 200., obj["size"][2] * \
                                                       obj["scale"][2] / 200.
                    if abs(ang_final - 1.57) < 0.1:
                        half_obj_size_x, half_obj_size_y = obj["size"][2] * obj["scale"][2] / 200., obj["size"][0] * \
                                                           obj["scale"][0] / 200.
                    if abs(ang_final + 1.57) < 0.1:
                        half_obj_size_x, half_obj_size_y = obj["size"][2] * obj["scale"][2] / 200., obj["size"][0] * \
                                                           obj["scale"][0] / 200.

                    cos_a = math.cos(ang)
                    sin_a = math.sin(ang)

                    origin_x = obj["normal_position"][0] + group_offset[0]
                    origin_z = obj["normal_position"][2] + group_offset[1]

                    obj["position"][0] = cos_a * origin_x - sin_a * origin_z + group_pos[0]
                    obj["position"][2] = cos_a * origin_z + sin_a * origin_x + group_pos[2]

                    left_top_pt = [obj["position"][0] - half_obj_size_x, obj["position"][2] - half_obj_size_y]
                    right_bottom_pt = [obj["position"][0] + half_obj_size_x, obj["position"][2] + half_obj_size_y]

                    left_bottom_pt = [left_top_pt[0], right_bottom_pt[1]]
                    right_top_pt = [right_bottom_pt[0], left_top_pt[1]]

                    key_point_list = [right_top_pt, left_top_pt, left_bottom_pt, right_bottom_pt, right_top_pt]

                    z_x = [i[0] for i in key_point_list]
                    z_y = [i[1] for i in key_point_list]

                    plt.plot(z_x, z_y, color="blue")

    plt.plot(x, y)
    plt.show()


if __name__ == '__main__':
    # input_room_case = {'area': 15.066600208937999, 'window_info': [{'width': 0.24, 'link': '', 'wall_idx': 5, 'to': '', 'main_pts': [[1.4833474999999998, -5.419606], [3.5407705, -5.419606]], 'pts': [1.4833474999999998, 5.4796059999999995, 3.5407705, 5.4796059999999995, 3.5407705, 5.359606, 1.4833474999999998, 5.359606], 'height': 0.6}], 'mirror': 1, 'baywindow_info': [], 'coordinate': 'xzy', 'link': ['LivingDiningRoom'], 'type': 'Bedroom', 'furniture_info': [], 'decorate_info': [], 'unit': 'cm', 'door_info': [{'width': 0.109321, 'link': 'LivingDiningRoom', 'wall_idx': 3, 'to': 'none-2260', 'main_pts': [[0.673793, -0.68104], [1.587997, -0.68104]], 'pts': [0.673793, 0.62104, 1.587997, 0.62104, 1.587997, 0.7410399999999999, 0.673793, 0.7410399999999999], 'height': 0}], 'alias': 'Bedroom-3897', 'material_info': {}, 'id': 'none-3897', 'hole_info': [], 'floor': [1.7572219999999998, 1.242235, 1.757222, 0.7410399999999998, 0.394674, 0.7410399999999998, 0.394674, 5.3596059999999985, 3.8880920000000003, 5.359606, 3.8880920000000008, 1.2422350000000004, 1.7572219999999998, 1.242235], 'wall_width': [0.24, 0.24, 0.24, 0.24, 0.24, 0.24], 'height': 2.8, 'zone_info': [{'draw_pts': [[0.8094451421788023, 2.422050425556039], [3.850286549804739, 5.299541642757708]], 'input': 'draw', 'type': 'Bed'}, {'draw_pts': [[1.7644189816607196, 1.2785921138053813], [3.862852017082715, 2.0450856177619183]], 'input': 'draw', 'type': 'Armoire'}]}
    # input_room_case = {
    #         "id": "LivingDiningRoom-4558",
    #         "type": "LivingDiningRoom",
    #         "floor": [
    #             -5.146676,
    #             -3.2676540000000003,
    #             -5.146676,
    #             3.3936219999999997,
    #             -1.529626,
    #             3.3936219999999993,
    #             -1.5296260000000002,
    #             0.2864119999999999,
    #             2.7532840000000003,
    #             0.28641199999999994,
    #             2.753284,
    #             -0.895257,
    #             -1.9285250000000003,
    #             -0.895257,
    #             -1.9285250000000003,
    #             -3.267654,
    #             -5.146676,
    #             -3.2676540000000003
    #         ],
    #         "door_info": [
    #             {
    #                 "pts": [
    #                     0.5038718678299999,
    #                     0.406412,
    #                     1.3436581321699999,
    #                     0.406412,
    #                     1.3436581321699999,
    #                     0.286412,
    #                     0.5038718678299999,
    #                     0.286412
    #                 ],
    #                 "to": "Bedroom-5393",
    #                 "width": 0.24,
    #                 "wall_idx": 0,
    #                 "main_pts": [
    #                     [
    #                         0.5038718678299999,
    #                         -0.346412
    #                     ],
    #                     [
    #                         1.3436581321699999,
    #                         -0.346412
    #                     ]
    #                 ],
    #                 "link": "Bedroom",
    #                 "height": 0
    #             },
    #             {
    #                 "pts": [
    #                     1.8265351810469999,
    #                     0.406412,
    #                     2.5823428189529998,
    #                     0.406412,
    #                     2.5823428189529998,
    #                     0.286412,
    #                     1.8265351810469999,
    #                     0.286412
    #                 ],
    #                 "to": "MasterBedroom-4196",
    #                 "width": 0.24,
    #                 "wall_idx": 0,
    #                 "main_pts": [
    #                     [
    #                         1.8265351810469999,
    #                         -0.346412
    #                     ],
    #                     [
    #                         2.5823428189529998,
    #                         -0.346412
    #                     ]
    #                 ],
    #                 "link": "MasterBedroom",
    #                 "height": 0
    #             },
    #             {
    #                 "pts": [
    #                     0.650834494264,
    #                     -1.015257,
    #                     1.3226635057360001,
    #                     -1.015257,
    #                     1.3226635057360001,
    #                     -0.895257,
    #                     0.650834494264,
    #                     -0.895257
    #                 ],
    #                 "to": "Bathroom-4953",
    #                 "width": 0.24,
    #                 "wall_idx": 2,
    #                 "main_pts": [
    #                     [
    #                         0.650834494264,
    #                         0.955257
    #                     ],
    #                     [
    #                         1.3226635057360001,
    #                         0.955257
    #                     ]
    #                 ],
    #                 "link": "Bathroom",
    #                 "height": 0
    #             },
    #             {
    #                 "pts": [
    #                     1.9734979259495002,
    #                     -1.015257,
    #                     2.6663220740505,
    #                     -1.015257,
    #                     2.6663220740505,
    #                     -0.895257,
    #                     1.9734979259495002,
    #                     -0.895257
    #                 ],
    #                 "to": "Library-3310",
    #                 "width": 0.24,
    #                 "wall_idx": 2,
    #                 "main_pts": [
    #                     [
    #                         1.9734979259495002,
    #                         0.955257
    #                     ],
    #                     [
    #                         2.6663220740505,
    #                         0.955257
    #                     ]
    #                 ],
    #                 "link": "Library",
    #                 "height": 0
    #             },
    #             {
    #                 "pts": [
    #                     -1.8085273245070286,
    #                     -1.8160382693483532,
    #                     -1.8085226754929713,
    #                     -2.5508517306516465,
    #                     -1.9285226754929714,
    #                     -2.5508517306516465,
    #                     -1.9285273245070287,
    #                     -1.8160382693483532
    #                 ],
    #                 "to": "Kitchen-3695",
    #                 "width": 0.24,
    #                 "wall_idx": 3,
    #                 "main_pts": [
    #                     [
    #                         -1.8685273245070286,
    #                         1.8160382693483532
    #                     ],
    #                     [
    #                         -1.8685226754929714,
    #                         2.5508517306516465
    #                     ]
    #                 ],
    #                 "link": "Kitchen",
    #                 "height": 0
    #             },
    #             {
    #                 "pts": [
    #                     -3.023231103399,
    #                     -3.387654,
    #                     -2.183444896601,
    #                     -3.387654,
    #                     -2.183444896601,
    #                     -3.267654,
    #                     -3.023231103399,
    #                     -3.267654
    #                 ],
    #                 "to": "",
    #                 "width": 0.24,
    #                 "wall_idx": 4,
    #                 "main_pts": [
    #                     [
    #                         -3.023231103399,
    #                         3.327654
    #                     ],
    #                     [
    #                         -2.183444896601,
    #                         3.327654
    #                     ]
    #                 ],
    #                 "link": "",
    #                 "height": 0
    #             },
    #             {
    #                 "pts": [
    #                     -4.311758618800001,
    #                     3.5136220000000002,
    #                     -1.9603553811999999,
    #                     3.5136220000000002,
    #                     -1.9603553811999999,
    #                     3.393622,
    #                     -4.311758618800001,
    #                     3.393622
    #                 ],
    #                 "to": "Balcony-5181",
    #                 "width": 0.24,
    #                 "wall_idx": 6,
    #                 "main_pts": [
    #                     [
    #                         -4.311758618800001,
    #                         -3.453622
    #                     ],
    #                     [
    #                         -1.9603553811999999,
    #                         -3.453622
    #                     ]
    #                 ],
    #                 "link": "Balcony",
    #                 "height": 0
    #             }
    #         ],
    #         "window_info": [],
    #         "hole_info": [],
    #         "baywindow_info": [],
    #         "wall_width": [
    #             0.24,
    #             0.24,
    #             0.24,
    #             0.24,
    #             0.24,
    #             0.24,
    #             0.24,
    #             0.24
    #         ],
    #         "furniture_info": [],
    #         "material_info": {
    #             "id": "LivingDiningRoom-4558",
    #             "type": "LivingDiningRoom",
    #             "floor": [
    #                 {
    #                     "jid": "9437af46-1820-432b-b882-a1455d4d1be9",
    #                     "texture_url": "https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/9437af46-1820-432b-b882-a1455d4d1be9/wallfloor.jpg",
    #                     "color": [
    #                         255,
    #                         255,
    #                         255
    #                     ],
    #                     "colorMode": "texture",
    #                     "size": [
    #                         3,
    #                         3
    #                     ],
    #                     "seam": False,
    #                     "material_id": "4560",
    #                     "area": 29.970551861687
    #                 }
    #             ],
    #             "wall": [
    #                 {
    #                     "jid": "c53afd8f-6b30-4d1b-8454-0138ff5d7147",
    #                     "texture_url": "",
    #                     "color": [
    #                         248,
    #                         249,
    #                         251
    #                     ],
    #                     "colorMode": "color",
    #                     "size": [
    #                         1,
    #                         1
    #                     ],
    #                     "seam": False,
    #                     "material_id": "2605",
    #                     "area": 29.602472
    #                 }
    #             ],
    #             "win_pocket": [],
    #             "door_pocket": []
    #         },
    #         "area": 28.208803541686997,
    #         "coordinate": "xzy",
    #         "unit": "cm",
    #         "height": 2.8,
    #         "alias": "LivingDiningRoom-4558",
    #         "mirror": 1,
    #         "link": [
    #             "Bedroom",
    #             "MasterBedroom",
    #             "Bathroom",
    #             "Library",
    #             "Kitchen",
    #             "",
    #             "Balcony"
    #         ],
    #         "decorate_info": [],
    #         "region_info": [
    #             {
    #                 "size": [
    #                     3.571875,
    #                     1.5,
    #                     1.9049999999999998
    #                 ],
    #                 "position": [
    #                     -4.194176000000001,
    #                     0.0,
    #                     1.3726715
    #                 ],
    #                 "rotation": [
    #                     0,
    #                     0.7071067717131209,
    #                     0,
    #                     0.7071067906599742
    #                 ],
    #                 "scale": [
    #                     1,
    #                     1,
    #                     1
    #                 ],
    #                 "zone": "",
    #                 "type": "Meeting",
    #                 "back_rely_line": [
    #                     [
    #                         -5.146676,
    #                         -3.2676540000000003
    #                     ],
    #                     [
    #                         -5.146676,
    #                         3.3936219999999997
    #                     ]
    #                 ]
    #             },
    #             {
    #                 "size": [
    #                     1.42875,
    #                     1.5,
    #                     1.42875
    #                 ],
    #                 "position": [
    #                     -4.292320999999999,
    #                     0.0,
    #                     -1.6038910000000004
    #                 ],
    #                 "rotation": [
    #                     0,
    #                     0.0,
    #                     0,
    #                     1.0
    #                 ],
    #                 "scale": [
    #                     1,
    #                     1,
    #                     1
    #                 ],
    #                 "zone": "",
    #                 "type": "Dining",
    #                 "back_rely_line": []
    #             },
    #             {
    #                 "size": [
    #                     3.1072099999999994,
    #                     1.5,
    #                     0.47625000000000006
    #                 ],
    #                 "position": [
    #                     -1.7677509999999999,
    #                     0.0,
    #                     1.8400170063805343
    #                 ],
    #                 "rotation": [
    #                     0,
    #                     -0.707106771713121,
    #                     0,
    #                     0.707106790659974
    #                 ],
    #                 "scale": [
    #                     1,
    #                     1,
    #                     1
    #                 ],
    #                 "zone": "",
    #                 "type": "Media",
    #                 "back_rely_line": [
    #                     [
    #                         -1.529626,
    #                         3.3936219999999993
    #                     ],
    #                     [
    #                         -1.5296260000000002,
    #                         0.2864119999999999
    #                     ]
    #                 ]
    #             },
    #             {
    #                 "size": [
    #                     0.7143750000000002,
    #                     1.5,
    #                     0.47624999999999984
    #                 ],
    #                 "position": [
    #                     -2.2682585000000004,
    #                     0.0,
    #                     3.155496999999999
    #                 ],
    #                 "rotation": [
    #                     0,
    #                     0.9999999999999997,
    #                     0,
    #                     2.6794896585028633e-08
    #                 ],
    #                 "scale": [
    #                     1,
    #                     1,
    #                     1
    #                 ],
    #                 "zone": "",
    #                 "type": "Cabinet",
    #                 "back_rely_line": [
    #                     [
    #                         -5.146676,
    #                         3.3936219999999997
    #                     ],
    #                     [
    #                         -1.529626,
    #                         3.3936219999999993
    #                     ]
    #                 ]
    #             },
    #             {
    #                 "size": [
    #                     0.714375,
    #                     1.5,
    #                     0.47625000000000006
    #                 ],
    #                 "position": [
    #                     -1.8868135000000001,
    #                     0.0,
    #                     0.0629839999999995
    #                 ],
    #                 "rotation": [
    #                     0,
    #                     0.0,
    #                     0,
    #                     1.0
    #                 ],
    #                 "scale": [
    #                     1,
    #                     1,
    #                     1
    #                 ],
    #                 "zone": "",
    #                 "type": "Cabinet",
    #                 "back_rely_line": []
    #             },
    #             {
    #                 "size": [
    #                     1.42875,
    #                     1.5,
    #                     0.4762500000000003
    #                 ],
    #                 "position": [
    #                     -4.292320999999999,
    #                     0.0,
    #                     -3.029529
    #                 ],
    #                 "rotation": [
    #                     0,
    #                     0.0,
    #                     0,
    #                     1.0
    #                 ],
    #                 "scale": [
    #                     1,
    #                     1,
    #                     1
    #                 ],
    #                 "zone": "Hallway",
    #                 "type": "Cabinet",
    #                 "back_rely_line": [
    #                     [
    #                         -1.9285250000000003,
    #                         -3.267654
    #                     ],
    #                     [
    #                         -5.146676,
    #                         -3.2676540000000003
    #                     ]
    #                 ]
    #             }
    #         ]
    #     }

    # draw_zone_list_process(input_room_case)
    input_room_case =       {
            "id": "Bedroom-4300",
            "type": "Bedroom",
            "style": "",
            "area": 24.9872,
            "height": 2.8,
            "coordinate": "xzy",
            "unit": "cm",
            "floor": [
                7.237382000000002,
                -2.657954,
                2.816687,
                -2.657954,
                2.816687,
                3.1325849999999997,
                7.237382000000001,
                3.1325849999999997,
                7.237382000000002,
                -2.657954
            ],
            "material": {
                "id": "Bedroom-4300",
                "type": "Bedroom",
                "floor": [
                    {
                        "jid": "23563d1a-a079-44e7-ab21-8eae20a93368",
                        "texture_url": "https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/23563d1a-a079-44e7-ab21-8eae20a93368/wallfloor_mini.jpg",
                        "color": [
                            255,
                            255,
                            255
                        ],
                        "colorMode": "texture",
                        "size": [
                            1.0799975233334098,
                            1.08
                        ],
                        "seam": [
                            "material",
                            "flooring - hardwood"
                        ],
                        "area": 24.989108472599998,
                        "lift": 0
                    }
                ],
                "wall": [
                    {
                        "jid": "3d2b3248-d675-40c1-8a65-10176d52379a",
                        "texture_url": "",
                        "color": [
                            250,
                            247,
                            237
                        ],
                        "colorMode": "color",
                        "size": [
                            1.0000000000000002,
                            1.0
                        ],
                        "seam": [
                            "material",
                            "paint"
                        ],
                        "wall": [
                            [
                                2.81669,
                                -1.1169
                            ],
                            [
                                2.81669,
                                2.63779
                            ]
                        ],
                        "height": 0.0,
                        "area": 10.513131999999999
                    },
                    {
                        "jid": "3d2b3248-d675-40c1-8a65-10176d52379a",
                        "texture_url": "",
                        "color": [
                            250,
                            247,
                            237
                        ],
                        "colorMode": "color",
                        "size": [
                            1.0000000000000002,
                            0.9999982549637556
                        ],
                        "seam": [
                            "material",
                            "paint"
                        ],
                        "wall": [
                            [
                                7.17738,
                                -2.65795
                            ],
                            [
                                7.17738,
                                3.07258
                            ]
                        ],
                        "height": 0.0,
                        "area": 16.045484
                    },
                    {
                        "jid": "3d2b3248-d675-40c1-8a65-10176d52379a",
                        "texture_url": "",
                        "color": [
                            250,
                            247,
                            237
                        ],
                        "colorMode": "color",
                        "size": [
                            1.0,
                            1.0
                        ],
                        "seam": [
                            "material",
                            "paint"
                        ],
                        "wall": [
                            [
                                2.81669,
                                2.63779
                            ],
                            [
                                2.81669,
                                3.07258
                            ]
                        ],
                        "height": 0.0,
                        "area": 1.217412
                    },
                    {
                        "jid": "3d2b3248-d675-40c1-8a65-10176d52379a",
                        "texture_url": "",
                        "color": [
                            250,
                            247,
                            237
                        ],
                        "colorMode": "color",
                        "size": [
                            1.0000000000000004,
                            1.0000000000000002
                        ],
                        "seam": [
                            "material",
                            "paint"
                        ],
                        "wall": [
                            [
                                2.81669,
                                -2.65795
                            ],
                            [
                                2.81669,
                                -1.1169
                            ]
                        ],
                        "height": 0.0,
                        "area": 2.63494
                    },
                    {
                        "jid": "3d2b3248-d675-40c1-8a65-10176d52379a",
                        "texture_url": "",
                        "color": [
                            250,
                            247,
                            237
                        ],
                        "colorMode": "color",
                        "size": [
                            1.0000000000000007,
                            1.0
                        ],
                        "seam": [
                            "material",
                            "paint"
                        ],
                        "wall": [
                            [
                                2.81669,
                                -2.65795
                            ],
                            [
                                7.17738,
                                -2.65795
                            ]
                        ],
                        "height": 0.0,
                        "area": 10.590487
                    },
                    {
                        "jid": "3d2b3248-d675-40c1-8a65-10176d52379a",
                        "texture_url": "",
                        "color": [
                            250,
                            247,
                            237
                        ],
                        "colorMode": "color",
                        "size": [
                            1.0000000000000018,
                            1.0000000000000002
                        ],
                        "seam": [
                            "material",
                            "paint"
                        ],
                        "wall": [
                            [
                                2.81669,
                                3.07258
                            ],
                            [
                                7.17738,
                                3.07258
                            ]
                        ],
                        "height": 0.0,
                        "area": 7.7978431518
                    }
                ],
                "ceiling": [
                    {
                        "jid": "c53afd8f-6b30-4d1b-8454-0138ff5d7147",
                        "texture_url": "",
                        "color": [
                            248,
                            249,
                            251
                        ],
                        "colorMode": "color",
                        "size": [
                            1.0000000000000004,
                            1.0
                        ],
                        "seam": [
                            "material",
                            "paint"
                        ],
                        "area": 24.989108472599998,
                        "lift": 2.8
                    }
                ],
                "win_pocket": [],
                "door_pocket": [
                    {
                        "jid": "local",
                        "texture_url": "https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/fa86be0c-a31f-4ba0-ac10-b8fa5d7d5e53/pocket_tex.jpg",
                        "color": [
                            255,
                            255,
                            255
                        ],
                        "colorMode": "texture",
                        "size": [
                            0.001,
                            0.001000000000000001
                        ],
                        "seam": False,
                        "area": 0,
                        "lift": 0
                    }
                ],
                "baseboard": [],
                "customized_ceiling": [
                    {
                        "id": "a591c378-7df6-42ee-98e9-1b892fc05c5c_47992.json",
                        "type": "CustomizedCeiling",
                        "size": [
                            436.07000000000005,
                            29.999999999999982,
                            573.053
                        ],
                        "position": [
                            4.9970300000000005,
                            2.5,
                            0.20731499999999992
                        ],
                        "rotation": [
                            0,
                            0,
                            0,
                            1
                        ],
                        "scale": [
                            1,
                            1,
                            1
                        ],
                        "style": "",
                        "valid": True,
                        "bounds": [
                            [
                                -2.1803500000000002,
                                2.1803500000000002
                            ],
                            [
                                -2.865265,
                                2.865265
                            ],
                            [
                                0.0,
                                0.2999999999999998
                            ]
                        ],
                        "coords": [
                            [
                                [
                                    2.18035,
                                    2.6652750000000003
                                ],
                                [
                                    2.18035,
                                    -2.865265
                                ],
                                [
                                    -2.1803500000000007,
                                    -2.865265
                                ],
                                [
                                    -2.1803500000000007,
                                    2.6652750000000003
                                ],
                                [
                                    -2.1803500000000007,
                                    2.865265
                                ],
                                [
                                    2.18035,
                                    2.865265
                                ],
                                [
                                    2.18035,
                                    2.6652750000000003
                                ]
                            ]
                        ],
                        "construct_id": "a591c378-7df6-42ee-98e9-1b892fc05c5c_47992",
                        "obj": "a591c378-7df6-42ee-98e9-1b892fc05c5c_47992.json",
                        "grid": [],
                        "edge": [],
                        "form": [],
                        "material": [
                            {
                                "jid": "c53afd8f-6b30-4d1b-8454-0138ff5d7147",
                                "texture_url": "",
                                "color": [
                                    248,
                                    249,
                                    251
                                ],
                                "colorMode": "color",
                                "size": [
                                    0.9999999911391385,
                                    1.0000023043281208
                                ],
                                "seam": [
                                    "material",
                                    "paint"
                                ],
                                "area": 24.989161778
                            }
                        ],
                        "attachment": [],
                        "house_id": "a591c378-7df6-42ee-98e9-1b892fc05c5c",
                        "room_id": "Bedroom-4300",
                        "uid_list": [
                            "47992customizedfeaturemodel_1/48003/customized_feature_model_48003",
                            "47992/customizedfeaturemodel_1/48003/customized_feature_model_48003<bottomFace>/0"
                        ],
                        "entityId": ""
                    },
                    {
                        "id": "cb313cff-628c-48eb-a1c7-27b1aa2c749d",
                        "type": "build element/ceiling molding",
                        "style": "Victorian",
                        "size": [
                            403.0,
                            32.2,
                            396.0
                        ],
                        "scale": [
                            1.06249,
                            1,
                            1.00013
                        ],
                        "position": [
                            4.99703,
                            2.478,
                            0.53156
                        ],
                        "rotation": [
                            0,
                            0.70711,
                            0,
                            0.70711
                        ],
                        "entityId": "50159"
                    }
                ],
                "background": [
                    {
                        "id": "9104d64b-4cb8-48fe-a05e-e0653286e0ff",
                        "type": "build element/background wall",
                        "style": "Victorian",
                        "size": [
                            280.0,
                            240.0,
                            1.80004
                        ],
                        "scale": [
                            1.63645,
                            1.04167,
                            1
                        ],
                        "position": [
                            2.82569,
                            0,
                            0.78156
                        ],
                        "rotation": [
                            0,
                            0.70711,
                            0,
                            0.70711
                        ],
                        "entityId": "50242"
                    }
                ]
            },
            "door_info": [
                {
                    "pts": [
                        3.21050606,
                        -2.7779540000000003,
                        3.96050594,
                        -2.7779540000000003,
                        3.96050594,
                        -2.657954,
                        3.21050606,
                        -2.657954
                    ],
                    "to": "Bathroom-11132",
                    "width": 0.1325,
                    "wall_idx": 0,
                    "main_pts": [
                        [
                            3.21050606,
                            2.717954
                        ],
                        [
                            3.96050594,
                            2.717954
                        ]
                    ],
                    "link": "Bathroom",
                    "height": 0
                },
                {
                    "pts": [
                        2.6966844692814087,
                        -1.6005099000080056,
                        2.696689530718591,
                        -2.400510099991994,
                        2.816689530718591,
                        -2.400510099991994,
                        2.816684469281409,
                        -1.6005099000080056
                    ],
                    "to": "LivingDiningRoom-2166",
                    "width": 0.1325,
                    "wall_idx": 1,
                    "main_pts": [
                        [
                            2.7566844692814088,
                            1.6005099000080056
                        ],
                        [
                            2.756689530718591,
                            2.400510099991994
                        ]
                    ],
                    "link": "LivingDiningRoom",
                    "height": 0
                }
            ],
            "hole_info": [],
            "window_info": [
                {
                    "pts": [
                        3.615003941375,
                        3.252585,
                        6.372486058624999,
                        3.252585,
                        6.372486058624999,
                        3.1325849999999997,
                        3.615003941375,
                        3.1325849999999997
                    ],
                    "to": "",
                    "width": 0.10026,
                    "wall_idx": 2,
                    "main_pts": [
                        [
                            3.615003941375,
                            -3.192585
                        ],
                        [
                            6.372486058624999,
                            -3.192585
                        ]
                    ],
                    "height": 0.6,
                    "link": ""
                }
            ],
            "baywindow_info": [],
            "furniture_info": [
                {
                    "id": "9853bd8e-26a3-4894-9a93-acc97eef2b57",
                    "type": "storage unit/armoire",
                    "style": "Contemporary",
                    "size": [
                        180.421,
                        213.251,
                        69.6588
                    ],
                    "scale": [
                        1.330222,
                        1.172327,
                        0.861341
                    ],
                    "position": [
                        5.977382,
                        0,
                        -2.357954
                    ],
                    "rotation": [
                        0,
                        -0.0,
                        0,
                        1.0
                    ],
                    "entityId": "48256",
                    "categories": [],
                    "relate": "wall",
                    "relate_role": "wall"
                },
                {
                    "id": "7749a447-e5fb-43d5-b5bd-c12907b85df0",
                    "type": "table/table",
                    "style": "Classic",
                    "size": [
                        118.591,
                        161.317,
                        46.5899
                    ],
                    "scale": [
                        1,
                        1,
                        1
                    ],
                    "position": [
                        3.049637,
                        0,
                        2.158228
                    ],
                    "rotation": [
                        0,
                        0.7071067811865475,
                        0,
                        0.7071067811865476
                    ],
                    "entityId": "47985",
                    "categories": [],
                    "relate": "wall",
                    "relate_role": "wall"
                },
                {
                    "id": "c725e9aa-bb7c-4149-b75e-bafd1864242e",
                    "type": "media unit/floor-based media unit",
                    "style": "Victorian",
                    "size": [
                        182.588,
                        49.6693,
                        41.2979
                    ],
                    "scale": [
                        1,
                        1,
                        1
                    ],
                    "position": [
                        3.023176,
                        0,
                        0.34973
                    ],
                    "rotation": [
                        0,
                        0.7071067811865475,
                        0,
                        0.7071067811865476
                    ],
                    "entityId": "50296",
                    "categories": [],
                    "relate": "wall",
                    "relate_role": "wall"
                },
                {
                    "id": "92f5872c-5f3c-4ca5-a1e8-597d5e1c61eb",
                    "type": "table/night table",
                    "style": "Victorian",
                    "size": [
                        62.2701,
                        65.253,
                        50.3716
                    ],
                    "scale": [
                        1,
                        1,
                        1
                    ],
                    "position": [
                        6.757675,
                        0,
                        1.90272
                    ],
                    "rotation": [
                        0,
                        -0.7071067811865475,
                        0,
                        0.7071067811865476
                    ],
                    "entityId": "47421",
                    "categories": [],
                    "turn": 0,
                    "turn_fix": 1
                },
                {
                    "id": "2f922f72-8eb5-4248-8f67-4df01314f7e6",
                    "type": "build element/background wall",
                    "style": "Victorian",
                    "size": [
                        533.01,
                        298.963,
                        23.49
                    ],
                    "scale": [
                        0.965908,
                        0.836224,
                        0.851426
                    ],
                    "position": [
                        7.109533,
                        0,
                        0.487826
                    ],
                    "rotation": [
                        0,
                        -0.7071067811865475,
                        0,
                        0.7071067811865476
                    ],
                    "entityId": "50439",
                    "categories": []
                },
                {
                    "id": "0ad6a468-c74c-4182-9fea-9afaed7175dc",
                    "type": "bed/king-size bed",
                    "style": "Victorian",
                    "size": [
                        250.787,
                        161.498,
                        216.344
                    ],
                    "scale": [
                        1,
                        1,
                        1
                    ],
                    "position": [
                        5.981264,
                        0,
                        0.4477
                    ],
                    "rotation": [
                        0,
                        -0.7071067811865475,
                        0,
                        0.7071067811865476
                    ],
                    "entityId": "47418",
                    "categories": [],
                    "relate": "wall",
                    "relate_role": "wall"
                },
                {
                    "id": "92f5872c-5f3c-4ca5-a1e8-597d5e1c61eb",
                    "type": "table/night table",
                    "style": "Victorian",
                    "size": [
                        62.2701,
                        65.253,
                        50.3716
                    ],
                    "scale": [
                        1,
                        1,
                        1
                    ],
                    "position": [
                        6.757675,
                        0,
                        -0.956503
                    ],
                    "rotation": [
                        0,
                        -0.7071067811865475,
                        0,
                        0.7071067811865476
                    ],
                    "entityId": "47420",
                    "categories": [],
                    "turn": 0,
                    "turn_fix": 1
                },
                {
                    "id": "830a09a0-8850-49a5-97c7-22256ec4f2f7",
                    "type": "lighting/chandelier",
                    "style": "Victorian",
                    "size": [
                        91.4039,
                        89.6853,
                        91.4039
                    ],
                    "scale": [
                        1,
                        1,
                        1
                    ],
                    "position": [
                        5.027034,
                        1.845241,
                        0.531559
                    ],
                    "rotation": [
                        0,
                        -0.0,
                        0,
                        1.0
                    ],
                    "entityId": "48184",
                    "categories": []
                },
                {
                    "id": "a8724c1b-4579-42fb-b08a-870e6241d442",
                    "type": "plants/plants - on top of others",
                    "style": "Victorian",
                    "size": [
                        45.262001037597656,
                        53.936798095703125,
                        49.12739944458008
                    ],
                    "scale": [
                        1,
                        1,
                        1
                    ],
                    "position": [
                        6.763896,
                        0.65253,
                        -0.909938
                    ],
                    "rotation": [
                        0,
                        -0.7071067811865475,
                        0,
                        0.7071067811865476
                    ],
                    "entityId": "50163",
                    "categories": [],
                    "category": "f168f93c-351e-4224-aa36-b08441933739"
                },
                {
                    "id": "d44e9710-ce30-4124-b584-d42623a1e64e",
                    "type": "accessory/accessory - on top of others",
                    "style": "Japanese",
                    "size": [
                        33.3519,
                        9.34044,
                        26.5126
                    ],
                    "scale": [
                        0.689616,
                        0.689616,
                        0.689616
                    ],
                    "position": [
                        6.783747,
                        0.652524,
                        1.916436
                    ],
                    "rotation": [
                        0,
                        -0.9696580811371891,
                        0,
                        0.24446514206598924
                    ],
                    "entityId": "50174",
                    "categories": []
                },
                {
                    "id": "85a8e011-e40c-4239-9ad6-1cf6781738da",
                    "type": "lighting/wall lamp",
                    "style": "Victorian",
                    "size": [
                        28.9203,
                        65.0103,
                        13.7656
                    ],
                    "scale": [
                        1,
                        1,
                        1
                    ],
                    "position": [
                        7.004834,
                        1.1,
                        1.932499
                    ],
                    "rotation": [
                        0,
                        -0.7071067811865475,
                        0,
                        0.7071067811865476
                    ],
                    "entityId": "50177",
                    "categories": []
                },
                {
                    "id": "85a8e011-e40c-4239-9ad6-1cf6781738da",
                    "type": "lighting/wall lamp",
                    "style": "Victorian",
                    "size": [
                        28.9203,
                        65.0103,
                        13.7656
                    ],
                    "scale": [
                        1,
                        1,
                        1
                    ],
                    "position": [
                        7.004834,
                        1.1,
                        -0.972091
                    ],
                    "rotation": [
                        0,
                        -0.7071067811865475,
                        0,
                        0.7071067811865476
                    ],
                    "entityId": "50178",
                    "categories": []
                },
                {
                    "id": "34ce344f-6c7c-4626-8941-6c26333e96c5",
                    "type": "electronics/TV - wall-attached",
                    "style": "Chinese Modern",
                    "size": [
                        180.829,
                        110.098,
                        1.30694
                    ],
                    "scale": [
                        0.846103,
                        0.846103,
                        0.846103
                    ],
                    "position": [
                        2.841167,
                        0.75,
                        0.330798
                    ],
                    "rotation": [
                        0,
                        0.7071067811865475,
                        0,
                        0.7071067811865476
                    ],
                    "entityId": "50294",
                    "categories": [],
                    "relate": "wall",
                    "relate_role": "wall"
                },
                {
                    "id": "9827200f-687c-4ef8-a16f-36d7da9386ce",
                    "type": "chair/chair",
                    "style": "Contemporary",
                    "size": [
                        44.0734,
                        46.6565,
                        35.1004
                    ],
                    "scale": [
                        1,
                        1,
                        1
                    ],
                    "position": [
                        3.407455,
                        0,
                        1.90272
                    ],
                    "rotation": [
                        0,
                        -0.0,
                        0,
                        1.0
                    ],
                    "entityId": "50299",
                    "categories": []
                },
                {
                    "id": "e7880d8e-0d1e-401a-a05e-1e756e9c0b4b",
                    "type": "rug/rug",
                    "style": "Victorian",
                    "size": [
                        345.661,
                        1.0,
                        239.925
                    ],
                    "scale": [
                        1,
                        1,
                        1
                    ],
                    "position": [
                        5.160229,
                        0,
                        0.4477
                    ],
                    "rotation": [
                        0,
                        0.7071067811865475,
                        0,
                        0.7071067811865476
                    ],
                    "entityId": "50300",
                    "categories": []
                },
                {
                    "id": "c2aed6f6-8773-4ae2-ad5d-dfabf28dd870",
                    "type": "curtain/curtain",
                    "style": "Victorian",
                    "size": [
                        214.247,
                        176.73,
                        9.10419
                    ],
                    "scale": [
                        2.100379,
                        1.697505,
                        1.417216
                    ],
                    "position": [
                        4.970854,
                        0,
                        2.946348
                    ],
                    "rotation": [
                        0,
                        1.0,
                        0,
                        6.123233995736766e-17
                    ],
                    "entityId": "50440",
                    "categories": []
                },
                {
                    "id": "57d6c041-6cde-4d00-960e-f8bf18eaa8b5",
                    "type": "accessory/accessory - on top of others",
                    "style": "Contemporary",
                    "size": [
                        30.205400466918945,
                        15.667400360107422,
                        18.78689956665039
                    ],
                    "scale": [
                        0.702095,
                        0.702095,
                        0.702095
                    ],
                    "position": [
                        2.987906,
                        0.321,
                        0.112814
                    ],
                    "rotation": [
                        0,
                        0.7071067811865475,
                        0,
                        0.7071067811865476
                    ],
                    "entityId": "50479",
                    "categories": []
                },
                {
                    "id": "d44e9710-ce30-4124-b584-d42623a1e64e",
                    "type": "accessory/accessory - on top of others",
                    "style": "Japanese",
                    "size": [
                        33.3519,
                        9.34044,
                        26.5126
                    ],
                    "scale": [
                        0.963552,
                        0.963552,
                        0.963552
                    ],
                    "position": [
                        2.957582,
                        0.201,
                        0.11473
                    ],
                    "rotation": [
                        0,
                        0.7071067811865475,
                        0,
                        0.7071067811865476
                    ],
                    "entityId": "50480",
                    "categories": []
                },
                {
                    "id": "8b6c7e4d-e5d8-43e6-81d9-5a0d0c94e538",
                    "type": "accessory/accessory - on top of others",
                    "style": "Contemporary",
                    "size": [
                        34.569,
                        8.3218,
                        25.5149
                    ],
                    "scale": [
                        1,
                        1,
                        1
                    ],
                    "position": [
                        2.987906,
                        0.321,
                        0.587388
                    ],
                    "rotation": [
                        0,
                        0.7071067811865475,
                        0,
                        0.7071067811865476
                    ],
                    "entityId": "50481",
                    "categories": []
                },
                {
                    "id": "eb113d9e-25f1-4d18-bbd0-4ff817b5b4f0",
                    "type": "300 - on top of others",
                    "style": "Asian",
                    "size": [
                        31.495800018310547,
                        17.449199676513672,
                        11.244799613952637
                    ],
                    "scale": [
                        0.515783,
                        0.515783,
                        0.515783
                    ],
                    "position": [
                        2.973523,
                        0.201,
                        0.58473
                    ],
                    "rotation": [
                        0,
                        0.7071067811865475,
                        0,
                        0.7071067811865476
                    ],
                    "entityId": "50482",
                    "categories": [],
                    "category": "49801d4a-6610-4b95-80ef-557869ace825",
                    "turn": 0,
                    "turn_fix": 1
                },
                {
                    "id": "eeffb348-5783-4702-a743-0b62787536e8",
                    "type": "accessory/accessory - on top of others",
                    "style": "Contemporary",
                    "size": [
                        28.0,
                        31.034700393676758,
                        22.0
                    ],
                    "scale": [
                        0.741106,
                        0.741106,
                        0.741106
                    ],
                    "position": [
                        2.973523,
                        0.201,
                        -0.29527
                    ],
                    "rotation": [
                        0,
                        0.7071067811865475,
                        0,
                        0.7071067811865476
                    ],
                    "entityId": "50483",
                    "categories": []
                },
                {
                    "id": "8a60f035-1737-47d2-ad1e-14fba0142000",
                    "type": "300 - on top of others",
                    "style": "Country",
                    "size": [
                        32.92060089111328,
                        10.74269962310791,
                        22.068899154663086
                    ],
                    "scale": [
                        0.850531,
                        0.850531,
                        0.850531
                    ],
                    "position": [
                        2.973523,
                        0.201,
                        0.98973
                    ],
                    "rotation": [
                        0,
                        0.7071067811865475,
                        0,
                        0.7071067811865476
                    ],
                    "entityId": "50484",
                    "categories": [],
                    "category": "49801d4a-6610-4b95-80ef-557869ace825",
                    "relate": "wall",
                    "relate_role": "wall"
                },
                {
                    "id": "3c54d624-ff0c-4b26-8101-da5a8c44ba88",
                    "type": "300 - on top of others",
                    "style": "欧式/古典",
                    "size": [
                        14.1533,
                        16.6135,
                        11.193200000000001
                    ],
                    "scale": [
                        1,
                        1,
                        1
                    ],
                    "position": [
                        3.040854,
                        0.496633,
                        -0.372139
                    ],
                    "rotation": [
                        0,
                        0.7071067811865475,
                        0,
                        0.7071067811865476
                    ],
                    "entityId": "50485",
                    "categories": [],
                    "turn": 0,
                    "turn_fix": 1
                },
                {
                    "id": "eeaeaceb-f608-49d5-9dd5-5595004a3243",
                    "type": "accessory/accessory - on top of others",
                    "style": "Contemporary",
                    "size": [
                        25.95800018310547,
                        27.098800659179688,
                        25.95800018310547
                    ],
                    "scale": [
                        0.886047,
                        0.886047,
                        0.886047
                    ],
                    "position": [
                        3.065643,
                        0.775095,
                        2.379783
                    ],
                    "rotation": [
                        0,
                        0.7071067811865475,
                        0,
                        0.7071067811865476
                    ],
                    "entityId": "50486",
                    "categories": []
                },
                {
                    "id": "8bd5de3b-24c7-4bbc-95a2-7c53dc2f0e02",
                    "type": "300 - on top of others",
                    "style": "Contemporary",
                    "size": [
                        10.700400352478027,
                        16.02869987487793,
                        11.481100082397461
                    ],
                    "scale": [
                        0.84109,
                        0.84109,
                        0.84109
                    ],
                    "position": [
                        3.093581,
                        0.77542,
                        1.719185
                    ],
                    "rotation": [
                        0,
                        0.7071067811865475,
                        0,
                        0.7071067811865476
                    ],
                    "entityId": "50487",
                    "categories": [],
                    "category": "bbbd6fb4-1ae5-484b-b22c-1e600eef954a",
                    "turn": 0,
                    "turn_fix": 1
                },
                {
                    "id": "229a93f4-48af-441f-b7ea-41d797856689",
                    "type": "300 - on top of others",
                    "style": "Contemporary",
                    "size": [
                        11.128100395202637,
                        3.3519399166107178,
                        6.151889801025391
                    ],
                    "scale": [
                        1,
                        1,
                        1
                    ],
                    "position": [
                        3.04968,
                        0.681,
                        2.625129
                    ],
                    "rotation": [
                        0,
                        -0.0,
                        0,
                        1.0
                    ],
                    "entityId": "50488",
                    "categories": [],
                    "category": "bbbd6fb4-1ae5-484b-b22c-1e600eef954a",
                    "turn": 0,
                    "turn_fix": 1
                },
                {
                    "id": "9e156d74-85b6-40d2-bd69-32996e04e0a6",
                    "type": "accessory/accessory - on top of others",
                    "style": "Contemporary",
                    "size": [
                        30.0,
                        28.216999053955078,
                        18.0
                    ],
                    "scale": [
                        1,
                        1,
                        1
                    ],
                    "position": [
                        3.04739,
                        0.181,
                        2.403168
                    ],
                    "rotation": [
                        0,
                        0.7071067811865475,
                        0,
                        0.7071067811865476
                    ],
                    "entityId": "50489",
                    "categories": []
                },
                {
                    "id": "d2b4d546-51dd-4106-9a3d-cadfe5d28a91",
                    "type": "300 - on top of others",
                    "style": "Contemporary",
                    "size": [
                        7.125840187072754,
                        18.54560089111328,
                        6.703959941864014
                    ],
                    "scale": [
                        0.98234,
                        0.98234,
                        0.98234
                    ],
                    "position": [
                        2.998518,
                        0.181,
                        2.607539
                    ],
                    "rotation": [
                        0,
                        0.7071067811865475,
                        0,
                        0.7071067811865476
                    ],
                    "entityId": "50490",
                    "categories": [],
                    "category": "bbbd6fb4-1ae5-484b-b22c-1e600eef954a",
                    "turn": 0,
                    "turn_fix": 1
                },
                {
                    "id": "fa86be0c-a31f-4ba0-ac10-b8fa5d7d5e53",
                    "type": "door/single swing door",
                    "style": "Victorian",
                    "size": [
                        82.0,
                        230.0,
                        13.25
                    ],
                    "scale": [
                        0.914634,
                        0.938809,
                        1
                    ],
                    "position": [
                        3.585506,
                        0,
                        -2.717954
                    ],
                    "rotation": [
                        0,
                        -0.0,
                        0,
                        1.0
                    ],
                    "entityId": "47423",
                    "categories": [],
                    "pocket": {
                        "jid": "",
                        "texture_url": "https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/fa86be0c-a31f-4ba0-ac10-b8fa5d7d5e53/pocket_tex.jpg",
                        "color": None,
                        "colorMode": "texture",
                        "size": [
                            0.001,
                            0.001
                        ],
                        "seam": False,
                        "material_id": "47487",
                        "area": -1
                    },
                    "unit_to_room": "Bathroom-11132",
                    "unit_to_type": "Bathroom"
                },
                {
                    "id": "ec9b9318-17d5-4af4-b306-81cc38c2fb59",
                    "type": "window/window",
                    "style": "Contemporary",
                    "size": [
                        134.9949951171875,
                        119.9520034790039,
                        10.026000022888184
                    ],
                    "scale": [
                        2.042655,
                        1.333867,
                        1
                    ],
                    "position": [
                        4.993745,
                        0.85,
                        3.192585
                    ],
                    "rotation": [
                        0,
                        -0.0,
                        0,
                        1.0
                    ],
                    "entityId": "47901",
                    "categories": [],
                    "unit_to_room": "",
                    "unit_to_type": ""
                }
            ],
            "decorate_info": [],
            "material_info": {
                "id": "Bedroom-4300",
                "type": "Bedroom",
                "floor": [
                    {
                        "jid": "23563d1a-a079-44e7-ab21-8eae20a93368",
                        "texture_url": "https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/23563d1a-a079-44e7-ab21-8eae20a93368/wallfloor_mini.jpg",
                        "color": [
                            255,
                            255,
                            255
                        ],
                        "colorMode": "texture",
                        "size": [
                            1.0799975233334098,
                            1.08
                        ],
                        "seam": [
                            "material",
                            "flooring - hardwood"
                        ],
                        "area": 24.989108472599998,
                        "lift": 0
                    }
                ],
                "wall": [
                    {
                        "jid": "3d2b3248-d675-40c1-8a65-10176d52379a",
                        "texture_url": "",
                        "color": [
                            250,
                            247,
                            237
                        ],
                        "colorMode": "color",
                        "size": [
                            1.0000000000000002,
                            1.0
                        ],
                        "seam": [
                            "material",
                            "paint"
                        ],
                        "wall": [
                            [
                                2.81669,
                                -1.1169
                            ],
                            [
                                2.81669,
                                2.63779
                            ]
                        ],
                        "height": 0.0,
                        "area": 10.513131999999999
                    },
                    {
                        "jid": "3d2b3248-d675-40c1-8a65-10176d52379a",
                        "texture_url": "",
                        "color": [
                            250,
                            247,
                            237
                        ],
                        "colorMode": "color",
                        "size": [
                            1.0000000000000002,
                            0.9999982549637556
                        ],
                        "seam": [
                            "material",
                            "paint"
                        ],
                        "wall": [
                            [
                                7.17738,
                                -2.65795
                            ],
                            [
                                7.17738,
                                3.07258
                            ]
                        ],
                        "height": 0.0,
                        "area": 16.045484
                    },
                    {
                        "jid": "3d2b3248-d675-40c1-8a65-10176d52379a",
                        "texture_url": "",
                        "color": [
                            250,
                            247,
                            237
                        ],
                        "colorMode": "color",
                        "size": [
                            1.0,
                            1.0
                        ],
                        "seam": [
                            "material",
                            "paint"
                        ],
                        "wall": [
                            [
                                2.81669,
                                2.63779
                            ],
                            [
                                2.81669,
                                3.07258
                            ]
                        ],
                        "height": 0.0,
                        "area": 1.217412
                    },
                    {
                        "jid": "3d2b3248-d675-40c1-8a65-10176d52379a",
                        "texture_url": "",
                        "color": [
                            250,
                            247,
                            237
                        ],
                        "colorMode": "color",
                        "size": [
                            1.0000000000000004,
                            1.0000000000000002
                        ],
                        "seam": [
                            "material",
                            "paint"
                        ],
                        "wall": [
                            [
                                2.81669,
                                -2.65795
                            ],
                            [
                                2.81669,
                                -1.1169
                            ]
                        ],
                        "height": 0.0,
                        "area": 2.63494
                    },
                    {
                        "jid": "3d2b3248-d675-40c1-8a65-10176d52379a",
                        "texture_url": "",
                        "color": [
                            250,
                            247,
                            237
                        ],
                        "colorMode": "color",
                        "size": [
                            1.0000000000000007,
                            1.0
                        ],
                        "seam": [
                            "material",
                            "paint"
                        ],
                        "wall": [
                            [
                                2.81669,
                                -2.65795
                            ],
                            [
                                7.17738,
                                -2.65795
                            ]
                        ],
                        "height": 0.0,
                        "area": 10.590487
                    },
                    {
                        "jid": "3d2b3248-d675-40c1-8a65-10176d52379a",
                        "texture_url": "",
                        "color": [
                            250,
                            247,
                            237
                        ],
                        "colorMode": "color",
                        "size": [
                            1.0000000000000018,
                            1.0000000000000002
                        ],
                        "seam": [
                            "material",
                            "paint"
                        ],
                        "wall": [
                            [
                                2.81669,
                                3.07258
                            ],
                            [
                                7.17738,
                                3.07258
                            ]
                        ],
                        "height": 0.0,
                        "area": 7.7978431518
                    }
                ],
                "ceiling": [
                    {
                        "jid": "c53afd8f-6b30-4d1b-8454-0138ff5d7147",
                        "texture_url": "",
                        "color": [
                            248,
                            249,
                            251
                        ],
                        "colorMode": "color",
                        "size": [
                            1.0000000000000004,
                            1.0
                        ],
                        "seam": [
                            "material",
                            "paint"
                        ],
                        "area": 24.989108472599998,
                        "lift": 2.8
                    }
                ],
                "win_pocket": [],
                "door_pocket": [
                    {
                        "jid": "local",
                        "texture_url": "https://jr-prod-pim-products.oss-cn-beijing.aliyuncs.com/i/fa86be0c-a31f-4ba0-ac10-b8fa5d7d5e53/pocket_tex.jpg",
                        "color": [
                            255,
                            255,
                            255
                        ],
                        "colorMode": "texture",
                        "size": [
                            0.001,
                            0.001000000000000001
                        ],
                        "seam": False,
                        "area": 0,
                        "lift": 0
                    }
                ],
                "baseboard": [],
                "customized_ceiling": [
                    {
                        "id": "a591c378-7df6-42ee-98e9-1b892fc05c5c_47992.json",
                        "type": "CustomizedCeiling",
                        "size": [
                            436.07000000000005,
                            29.999999999999982,
                            573.053
                        ],
                        "position": [
                            4.9970300000000005,
                            2.5,
                            0.20731499999999992
                        ],
                        "rotation": [
                            0,
                            0,
                            0,
                            1
                        ],
                        "scale": [
                            1,
                            1,
                            1
                        ],
                        "style": "",
                        "valid": True,
                        "bounds": [
                            [
                                -2.1803500000000002,
                                2.1803500000000002
                            ],
                            [
                                -2.865265,
                                2.865265
                            ],
                            [
                                0.0,
                                0.2999999999999998
                            ]
                        ],
                        "coords": [
                            [
                                [
                                    2.18035,
                                    2.6652750000000003
                                ],
                                [
                                    2.18035,
                                    -2.865265
                                ],
                                [
                                    -2.1803500000000007,
                                    -2.865265
                                ],
                                [
                                    -2.1803500000000007,
                                    2.6652750000000003
                                ],
                                [
                                    -2.1803500000000007,
                                    2.865265
                                ],
                                [
                                    2.18035,
                                    2.865265
                                ],
                                [
                                    2.18035,
                                    2.6652750000000003
                                ]
                            ]
                        ],
                        "construct_id": "a591c378-7df6-42ee-98e9-1b892fc05c5c_47992",
                        "obj": "a591c378-7df6-42ee-98e9-1b892fc05c5c_47992.json",
                        "grid": [],
                        "edge": [],
                        "form": [],
                        "material": [
                            {
                                "jid": "c53afd8f-6b30-4d1b-8454-0138ff5d7147",
                                "texture_url": "",
                                "color": [
                                    248,
                                    249,
                                    251
                                ],
                                "colorMode": "color",
                                "size": [
                                    0.9999999911391385,
                                    1.0000023043281208
                                ],
                                "seam": [
                                    "material",
                                    "paint"
                                ],
                                "area": 24.989161778
                            }
                        ],
                        "attachment": [],
                        "house_id": "a591c378-7df6-42ee-98e9-1b892fc05c5c",
                        "room_id": "Bedroom-4300",
                        "uid_list": [
                            "47992customizedfeaturemodel_1/48003/customized_feature_model_48003",
                            "47992/customizedfeaturemodel_1/48003/customized_feature_model_48003<bottomFace>/0"
                        ],
                        "entityId": ""
                    },
                    {
                        "id": "cb313cff-628c-48eb-a1c7-27b1aa2c749d",
                        "type": "build element/ceiling molding",
                        "style": "Victorian",
                        "size": [
                            403.0,
                            32.2,
                            396.0
                        ],
                        "scale": [
                            1.06249,
                            1,
                            1.00013
                        ],
                        "position": [
                            4.99703,
                            2.478,
                            0.53156
                        ],
                        "rotation": [
                            0,
                            0.70711,
                            0,
                            0.70711
                        ],
                        "entityId": "50159"
                    }
                ],
                "background": [
                    {
                        "id": "9104d64b-4cb8-48fe-a05e-e0653286e0ff",
                        "type": "build element/background wall",
                        "style": "Victorian",
                        "size": [
                            280.0,
                            240.0,
                            1.80004
                        ],
                        "scale": [
                            1.63645,
                            1.04167,
                            1
                        ],
                        "position": [
                            2.82569,
                            0,
                            0.78156
                        ],
                        "rotation": [
                            0,
                            0.70711,
                            0,
                            0.70711
                        ],
                        "entityId": "50242"
                    }
                ]
            },
            "alias": "Bedroom-4300",
            "link": [
                "LivingDiningRoom",
                "Bathroom"
            ],
            "region_info": [
                {
                    "type": "Bed",
                    "size": [
                        3.481924,
                        1.6149799999999999,
                        2.16344
                    ],
                    "scale": [
                        1.0,
                        1.0,
                        1.0
                    ],
                    "position": [
                        5.981264,
                        0,
                        0.4731085000000004
                    ],
                    "rotation": [
                        0,
                        -0.7071067811865475,
                        0,
                        0.7071067811865476
                    ],
                    "zone": "Bedroom"
                },
                {
                    "type": "Armoire",
                    "size": [
                        2.39999983462,
                        2.49999905077,
                        0.5999998045080001
                    ],
                    "scale": [
                        1.0,
                        1.0,
                        1.0
                    ],
                    "position": [
                        5.977382,
                        0,
                        -2.357954
                    ],
                    "rotation": [
                        0,
                        -0.0,
                        0,
                        1.0
                    ],
                    "zone": "CloakRoom"
                },
                {
                    "type": "Media",
                    "size": [
                        1.82588,
                        1.6815424809400001,
                        0.412979
                    ],
                    "scale": [
                        1.0,
                        1.0,
                        1.0
                    ],
                    "position": [
                        3.0421274707259,
                        0,
                        0.34973
                    ],
                    "rotation": [
                        0,
                        0.7071067811865475,
                        0,
                        0.7071067811865476
                    ],
                    "zone": "Bedroom"
                },
                {
                    "type": "Work",
                    "size": [
                        1.18591,
                        1.61317,
                        0.8111345
                    ],
                    "scale": [
                        1.0,
                        1.0,
                        1.0
                    ],
                    "position": [
                        3.2222547500000003,
                        0,
                        2.158228
                    ],
                    "rotation": [
                        0,
                        0.7071067811865475,
                        0,
                        0.7071067811865476
                    ],
                    "zone": "Library"
                }
            ]
        }
    floor_pts = [[input_room_case["floor"][2 * i], input_room_case["floor"][2 * i + 1]] for i in
                 range(len(input_room_case["floor"]) // 2 - 1)]
    # for region_data in input_room_case["region_info"]:
    #     refine_group_rotation(region_data, floor_pts)

    show_room_data(input_room_case)
