import math

from HouseSearch.design.math_utils import check_pt_in_poly
from HouseSearch.sample_layout.region_math import compute_line_line_cos_angle, compute_line_line_project_length_and_dis
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

    return min_dis, min_dis_project_length, min_dis_project_vec


def refine_group_rotation(group_data, floor_poly):
    # size 功能区按较长边方向为x, 垂直方向为方向y
    # base_rot = 0
    # if group_data["size"][0] < group_data["size"][2]:
    #     group_data["size"] = [group_data["size"][2], group_data["size"][1], group_data["size"][0]]
    #     base_rot = PI

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
        dis, project_length, vec = compute_line_project_poly_parallel_line_dis(rect_line, floor_poly)
        project_len_list.append({"dis": dis, "p_len": project_length, "vec": vec})

    # 四条边选一个作为主方向
    # 先判断是x方向 y方向 的可能结果
    x_line_info_idx = 0
    if project_len_list[0]["dis"] > project_len_list[2]["dis"]:
        x_line_info_idx = 2

    y_line_info_idx = 1
    if project_len_list[1]["dis"] > project_len_list[3]["dis"]:
        y_line_info_idx = 3

    wall_attach = project_len_list[x_line_info_idx]["dis"] < 0.1 or project_len_list[y_line_info_idx]["dis"] < 0.1
    # 配置靠墙(床、工作区、电视区)、靠墙为主方向、
    if wall_attach and group_data["type"] in ["Bed", "Work", "Media"]:
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
    if project_len_list[rot_line_idx]["dis"] < 0.3:
        group_data["position"][0] += project_len_list[rot_line_idx]["vec"][0]
        group_data["position"][2] += project_len_list[rot_line_idx]["vec"][1]

    elif project_len_list[rot_line_idx]["dis"] < 0.6 and group_data["type"] in ["Media", "Meeting", "Cabinet", "Bed"]:
        group_data["position"][0] += project_len_list[rot_line_idx]["vec"][0]
        group_data["position"][2] += project_len_list[rot_line_idx]["vec"][1]

    rot_ang_list = [0, PI / 2., PI, -PI / 2.]
    if rot_line_idx in [1, 3]:
        group_data["size"][2], group_data["size"][0] = group_data["size"][0], group_data["size"][2]

    rot_ang = rot_ang_list[rot_line_idx]
    group_data["rotation"] = [0, math.sin(rot_ang / 2.), 0, math.cos(rot_ang / 2.)]


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
        if sum(s) > 0.1:
            pass
        else:
            ang = - rot_to_ang(media["rotation"])
            bed["rotation"] = [0, math.sin(ang / 2.), 0, math.cos(ang / 2.)]

    # 处理沙发悬空的朝向
    if meeting and media:
        s = [abs(meeting["rotation"][i] - media["rotation"][i]) for i in range(4)]
        if sum(s) > 0.1:
            pass
        else:
            ang = - rot_to_ang(media["rotation"])
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

        print(group_data)
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
    plt.plot(x, y)
    plt.show()


if __name__ == '__main__':
    input_room_case = {'area': 41.76542700703701, 'window_info': [], 'mirror': 1, 'baywindow_info': [
        {'width': 0.24, 'link': '', 'wall_idx': 9, 'to': '',
         'main_pts': [[-5.781840547802496, -4.384301999979287], [-5.781827452197504, -2.314438000020713]],
         'pts': [-5.901827452195103, 2.3144372408053258, -5.661827452199906, 2.314438759236101, -5.661840547804897,
                 4.384302759194674, -5.901840547800094, 4.384301240763898], 'height': 0.6}], 'coordinate': 'xzy',
                       'link': ['', 'SecondBedroom', 'MasterBedroom', 'SecondBedroom', 'SecondBathroom', 'Kitchen'],
                       'type': 'LivingDiningRoom', 'furniture_info': [], 'decorate_info': [], 'unit': 'cm',
                       'door_info': [{'width': 0.126784, 'link': '', 'wall_idx': 0, 'to': '',
                                      'main_pts': [[-1.3772920000000002, -4.65731], [-0.252792, -4.65731]],
                                      'pts': [-1.3772920000000002, 4.7173099999999994, -0.252792, 4.7173099999999994,
                                              -0.252792, 4.59731, -1.3772920000000002, 4.59731], 'height': 0},
                                     {'width': 0.109321, 'link': 'SecondBedroom', 'wall_idx': 5,
                                      'to': 'SecondBedroom-10486',
                                      'main_pts': [[0.23167510800939914, -1.1234199999908514],
                                                   [0.23168089199060085, -0.20921600000914847]],
                                      'pts': [0.2916751080093991, 1.1234199999908514, 0.2916808919906009,
                                              0.20921600000914847, 0.17168089199060085, 0.20921600000914847,
                                              0.17167510800939914, 1.1234199999908514], 'height': 0},
                                     {'width': 0.109321, 'link': 'MasterBedroom', 'wall_idx': 5,
                                      'to': 'MasterBedroom-9654',
                                      'main_pts': [[0.23167510800939914, 1.9844380000091484],
                                                   [0.23168089199060085, 2.8986419999908515]],
                                      'pts': [0.2916751080093991, -1.9844380000091484, 0.2916808919906009,
                                              -2.8986419999908515, 0.17168089199060085, -2.8986419999908515,
                                              0.17167510800939914, -1.9844380000091484], 'height': 0},
                                     {'width': 0.109321, 'link': 'SecondBedroom', 'wall_idx': 7,
                                      'to': 'SecondBedroom-8444',
                                      'main_pts': [[-1.2049998919906009, 1.9844380000091484],
                                                   [-1.2049941080093993, 2.8986419999908515]],
                                      'pts': [-1.264999891990601, -1.9844380000091484, -1.2649941080093994,
                                              -2.8986419999908515, -1.1449941080093993, -2.8986419999908515,
                                              -1.1449998919906008, -1.9844380000091484], 'height': 0},
                                     {'width': 0.109321, 'link': 'SecondBathroom', 'wall_idx': 7,
                                      'to': 'SecondBathroom-5167',
                                      'main_pts': [[-1.2049998919906009, 0.13971500000914855],
                                                   [-1.2049941080093993, 1.0539189999908516]],
                                      'pts': [-1.264999891990601, -0.13971500000914855, -1.2649941080093994,
                                              -1.0539189999908516, -1.1449941080093993, -1.0539189999908516,
                                              -1.1449998919906008, -0.13971500000914855], 'height': 0},
                                     {'width': 0.09394, 'link': 'Kitchen', 'wall_idx': 8, 'to': 'Kitchen-4031',
                                      'main_pts': [[-3.735579, -2.05077], [-2.2455789999999998, -2.05077]],
                                      'pts': [-3.735579, 1.99077, -2.2455789999999998, 1.99077, -2.2455789999999998,
                                              2.11077, -3.735579, 2.11077], 'height': 0}],
                       'alias': 'LivingDiningRoom-2268', 'material_info': {}, 'id': 'LivingDiningRoom-2268',
                       'hole_info': [],
                       'floor': [-1.1449969999999998, -2.9586419999999993, -1.144997, 2.11077, -5.721833999999999,
                                 2.11077, -5.721834, 4.597310000000001, 0.2916780000000002, 4.59731, 0.2916780000000002,
                                 5.356695, 5.487377000000001, 5.356695, 5.487377, 1.4950520000000003,
                                 0.17167800000000003, 1.4950519999999998, 0.17167800000000003, -2.958642,
                                 -1.1449969999999998, -2.9586419999999993],
                       'wall_width': [0.24, 0.24, 0.24, 0.24, 0.24, 0.24, 0.24, 0.24, 0.24, 0.24], 'height': 2.8,
                       'zone_info': [{'draw_pts': [[-4.390445074935863, 2.6461317146197145],
                                                   [-2.670943584623025, 3.991088325854508]], 'input': 'draw',
                                      'type': 'Dining'}, {'draw_pts': [[-5.1906091347844105, 2.1524134649259294],
                                                                       [-4.015900195857819, 2.5610078784656136]],
                                                          'input': 'draw', 'type': 'Cabinet'}, {
                                         'draw_pts': [[-3.556231480625674, 4.110261696470249],
                                                      [-2.0239991836136264, 4.586943643203603]], 'input': 'draw',
                                         'type': 'DiningCabinet'}, {
                                         'draw_pts': [[-1.9559033609285779, 3.1909242660059602],
                                                      [-1.4962346456964333, 4.552905644471574]], 'input': 'draw',
                                         'type': 'Hallway'}, {'draw_pts': [[0.49566312030952664, 1.5905961463088638],
                                                                           [5.058300738169332, 2.2715868355416706]],
                                                              'input': 'draw', 'type': 'Media'}, {
                                         'draw_pts': [[0.4596449666086704, 2.892429256818999],
                                                      [5.204884546158969, 5.311568399304656]], 'input': 'draw',
                                         'type': 'Meeting'}], 'region_info': [
            {'size': [1.7195014903128376, 1.5, 1.3449566112347933],
             'position': [-3.5306943297794438, 0.0, 3.318610020237111], 'rotation': [0, 0.0, 0, 1.0],
             'scale': [1, 1, 1], 'zone': '', 'type': 'Dining'}, {'size': [1.1747089389265915, 1.5, 0.4085944135396842],
                                                                 'position': [-4.603254665321115, 0.0,
                                                                              2.315067206769842],
                                                                 'rotation': [0, 0.0, 0, 1.0], 'scale': [1, 1, 1],
                                                                 'zone': '', 'type': 'Cabinet'},
            {'size': [1.5322322970120474, 1.5, 0.47668194673335407],
             'position': [-2.79011533211965, 0.0, 4.358969026633323],
             'rotation': [0, 0.9999999999999997, 0, 2.6794896585028633e-08], 'scale': [1, 1, 1], 'zone': 'DiningRoom',
             'type': 'Cabinet'}, {'size': [0.4596687152321446, 1.5, 1.3619813784656136],
                                  'position': [-1.7260690033125057, 0.0, 3.9163193107671934],
                                  'rotation': [0, 0.9999999999999997, 0, 2.6794896585028633e-08], 'scale': [1, 1, 1],
                                  'zone': 'Hallway', 'type': 'Cabinet', 'back_on_wall': True},
            {'size': [4.562637617859806, 1.5, 0.6809906892328068],
             'position': [2.776981929239429, 0.0, 1.8355473446164035], 'rotation': [0, 0.0, 0, 1.0], 'scale': [1, 1, 1],
             'zone': '', 'type': 'Media'}, {'size': [4.745239579550298, 1.5, 2.4191391424856574],
                                            'position': [2.8322647563838195, 0.0, 4.147125428757171],
                                            'rotation': [0, 0.9999999999999997, 0, 2.6794896585028633e-08],
                                            'scale': [1, 1, 1], 'zone': '', 'type': 'Meeting'}]}

    # all_group_list = [{'type': 'Meeting', 'style': 'Swedish', 'code': 112111, 'size': [3.4218945587848784, 0.7962170000000001, 2.3587780906559255], 'offset': [0.3564422793924391, 0, -0.6944260453279627], 'position': [-2.146389045327963, 0, 2.719531698318989], 'rotation': [0, 0.7071067811865476, 0, -0.7071067811865475], 'size_min': [2.70901, 0.7962170000000001, 0.969926], 'size_rest': [0.0, 0.7128845587848782, 1.3888520906559254, 0.0], 'obj_main': 'ca393c50-6ac0-4a1d-9214-33e0074d061d', 'obj_type': 'sofa/ multi seat sofa', 'obj_list': [], 'relate': '', 'relate_role': '', 'relate_position': [], 'zone': 'LivingRoom', 'seed_list': [], 'keep_list': [], 'regulation': [0, 0, 0.6065071637376296, 0.5603609967157754], 'vertical': 0, 'window': 0, 'center': 0, 'region_direct': 0, 'region_middle': 0.48774690564694445, 'region_center': [-2.9045229999999993, 0, 2.719531698318989], 'region_extent': 3.8750459999999993}, {'type': 'Dining', 'style': 'Contemporary', 'code': 145, 'size': [1.5263499999999999, 0.7510429999999999, 1.762929406087663], 'offset': [-0.0, 0, 0.0137470325309611], 'position': [-2.702400339600935, 0, -1.005175123904541], 'rotation': [0, -0.7071067717131211, 0, 0.7071067906599738], 'size_min': [1.5263499999999999, 0.7510429999999999, 0.841747], 'size_rest': [0.5243382355747926, 0.0, 0.49684417051287044, 0.0], 'obj_main': '368040b0-a8bf-4eee-ba99-da0c5b0369b9', 'obj_type': 'table/dining table - square', 'obj_list': [], 'relate': '', 'relate_role': '', 'relate_position': [], 'zone': 'DiningRoom', 'seed_list': ['368040b0-a8bf-4eee-ba99-da0c5b0369b9'], 'keep_list': [], 'regulation': [0, 0.0, 0, 0.0], 'vertical': 0, 'window': 0, 'center': 1, 'region_direct': 0, 'region_middle': 0.5, 'region_center': [-2.702400339600935, 0, -1.005175123904541], 'region_extent': 1.762929406087663}, {'type': 'Media', 'style': 'Contemporary', 'code': 1100, 'size': [5.002712400000001, 2.6500000000000004, 0.353882], 'offset': [-0.0, 0, -0.0], 'position': [-4.308365687691249, 0, 2.6236437999999995], 'rotation': [0, 0.7071067811865475, 0, 0.7071067811865476], 'size_min': [5.002712400000001, 2.6500000000000004, 0.353882], 'size_rest': [0.0, 0.0, 0.0, 0.0], 'obj_main': 'b0e9e14a-9d21-4b88-8182-dd73bfcf90fa', 'obj_type': 'build element/background wall', 'obj_list': [], 'relate': '', 'relate_role': '', 'relate_position': [], 'zone': 'LivingRoom', 'seed_list': [], 'keep_list': [], 'regulation': [0.35669331230875057, 0, 0.35669331230875057, 0.8], 'vertical': 0, 'window': 0, 'center': 0, 'region_direct': 0, 'region_middle': 0.1377120805958066, 'region_center': [-4.308365687691248, 0, 1.125], 'region_extent': 8.0}, {'type': 'Cabinet', 'style': 'Contemporary', 'code': 10, 'size': [2.7613600000000003, 2.53174, 0.329701], 'scale': [1, 1, 1], 'offset': [-0.0, 0, -0.0], 'position': [-4.6771495, 0, -1.1293010421720284], 'rotation': [0, 0.7071067811865475, 0, 0.7071067811865476], 'size_min': [2.7613600000000003, 2.53174, 0.329701], 'size_rest': [0.0, 0.0, 0.0, 0.0], 'relate': '', 'relate_position': [], 'obj_main': '89c92e85-6453-48ba-9269-2e5007d74102', 'obj_type': 'cabinet/hutch&buffet', 'obj_list': [], 'zone': 'DiningRoom', 'seed_list': [], 'keep_list': [], 'regulation': [0, -0.02767228926873133, 0.8, -0.02767228926873133], 'vertical': 0, 'window': 0, 'center': 0, 'region_direct': 0, 'region_middle': 0.4864435800849629, 'region_center': [-0.8419999999999996, 0, -1.1293010421720282], 'region_extent': 8.0}, {'type': 'Cabinet', 'style': 'Contemporary', 'code': 10, 'size': [1.9624000000000001, 2.5364, 0.434818], 'scale': [1, 1, 1], 'offset': [-0.0, 0, -0.0], 'position': [-4.624838001418023, 0, -3.6334523207751244], 'rotation': [0, 0.707106771713121, 0, 0.707106790659974], 'size_min': [1.9624000000000001, 2.5364, 0.434818], 'size_rest': [0.0, 0.0, 0.0, 0.0], 'relate': '', 'relate_position': [], 'obj_main': '7b28703c-291e-4194-99dc-13bea96c260f', 'obj_type': 'cabinet/hutch&buffet', 'obj_list': [], 'zone': 'Hallway', 'seed_list': [], 'keep_list': [], 'regulation': [0, -0.0, 0.1705479999999998, -0.0], 'vertical': 0, 'window': 0, 'center': 0, 'region_direct': 0, 'region_middle': 0.5224390235112442, 'region_center': [-4.411653001418023, 0, -3.6334523150628546], 'region_extent': 0.8611879999999995}, {'type': 'Cabinet', 'style': 'Contemporary', 'code': 10, 'size': [0.73, 1.4458399963378907, 0.401239013671875], 'scale': [1, 1, 1], 'offset': [-0.0, 0, -0.0], 'position': [-1.1676195068359374, 0, -1.1044814449690084], 'rotation': [0, 0.7071067811865476, 0, -0.7071067811865475], 'size_min': [0.73, 1.4458399963378907, 0.401239013671875], 'size_rest': [0.0, 0.0, 0.0, 0.0], 'relate': '', 'relate_position': [], 'obj_main': 'ec1f0efc-06ac-481e-ac2e-5bd98242dbc9', 'obj_type': 'cabinet/floor-based cabinet', 'obj_list': [], 'seed_list': [], 'keep_list': [], 'regulation': [0, 0.5659729763057108, 0.8, 0.5659729763057108], 'vertical': 0, 'window': 0, 'center': 0, 'region_direct': 0, 'region_middle': 0.41235697126103593, 'region_center': [-4.967, 0, -1.1044814449690081], 'region_extent': 8.0}]

    draw_zone_list_process(input_room_case)
    show_room_data(input_room_case)
