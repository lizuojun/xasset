import numpy as np
import os
from matplotlib import pyplot as plt
from matplotlib import patches
import copy
from LayoutDecoration.Base.math_util import compute_furniture_rely, is_coincident_line, compute_furniture_rect, extend_edge
from LayoutDecoration.Base.recon_params import ROOM_BUILD_TYPE, is_hallway, PRIME_GENERAL_WALL_ROOM_TYPES


class RoomAreaSegmentation:
    def __init__(self, house_info, house_layouts=[], height=2.8, thickness=0.15, build_mode={}, concession=True):
        self.default_ceiling_height = thickness
        self.room_height = height
        self.refined_floor_pts = {}
        draw = build_mode['debug'] if 'debug' in build_mode else False
        self.is_customized_ceiling = build_mode['customized_ceiling'] if 'customized_ceiling' in build_mode else True
        # draw = False
        if draw:
            plt.figure()
            plt.axis('equal')
        for room_id in house_info['rooms'].keys():
            room_info = house_info['rooms'][room_id]
            if room_id in house_layouts:
                layouts = house_layouts[room_id]
            else:
                layouts = []
            # customized_ceiling
            room_type = ROOM_BUILD_TYPE[room_info['type']]
            if room_type in ['LivingDiningRoom'] + PRIME_GENERAL_WALL_ROOM_TYPES:
                living_required_points = []
                dining_required_points = []
                hallway_required_points = []
                for layout in layouts:
                    if 'LivingDiningRoom' == room_type and layout['type'] in ['Meeting', 'Media']:
                        living_required_points.append([layout['position'][0], layout['position'][2]])
                    if 'LivingDiningRoom' == room_type and layout['type'] in ['Dining']:
                        dining_required_points.append([layout['position'][0], layout['position'][2]])
                    if room_type in ['MasterBedroom', 'Library', 'KidsRoom'] and layout['type'] in ['Bed']:
                        living_required_points.append([layout['position'][0], layout['position'][2]])
                for door in room_info['Door']:
                    door_target_type = ROOM_BUILD_TYPE[door['target_room_type']]
                    if door_target_type in ['Other', '', 'LivingDiningRoom'] + PRIME_GENERAL_WALL_ROOM_TYPES:
                        face_offset = np.array(door['normal'])
                        pos = np.mean(door['layout_pts'], axis=0) + face_offset / np.linalg.norm(face_offset) * 0.3
                        hallway_required_points.append(pos)
                self.seg_main_wall(room_info, layouts)
                refined_floor_pts, cabinet_extra_area = self.refine_points(copy.deepcopy(room_info['floor_pts']),
                                                                           room_info,
                                                                           layouts,
                                                                           concession)
                self.refined_floor_pts[room_id] = refined_floor_pts
                living_rect, dining_rect, hallway_rect, remained_area = self.split_floor_into_rect(refined_floor_pts,
                                                                                                   living_required_points,
                                                                                                   dining_required_points,
                                                                                                   hallway_required_points,
                                                                                                   room_info['type']
                                                                                                   )

                self.config_area(room_info, living_rect, dining_rect, hallway_rect, remained_area, cabinet_extra_area,
                                 layouts, refined_floor_pts)
                self.seg_wall_with_room_area(room_info)

            else:
                living_rect, dining_rect, hallway_rect, remained_area = None, None, None, []
            if draw:
                self.plot_split_regions(room_info, layouts)
        if len(house_info['rooms']) > 0 and draw:
            # plt.show()
            folder = os.path.join(os.path.dirname(__file__), '../temp/%s/' % house_info['id'])
            if not os.path.exists(folder):
                os.makedirs(folder)
            save_path = os.path.join(os.path.dirname(__file__), '../temp/%s/region_segmentation.png' % house_info['id'])
            plt.savefig(save_path, dpi=300)
            plt.close()

    def refine_floor_pts_for_layout(self, floor_pts, room_info, layouts=[]):
        avoid_depth = 0.15
        for layout in layouts:
            if layout['type'] in ['Door', 'Window']:
                for fur_obj in layout['obj_list']:
                    if ('type' in fur_obj and 'curtain' in fur_obj['type']) or fur_obj['role'] == 'curtain':
                        depth = fur_obj['size'][-1] * fur_obj['scale'][-1] / 100.
                        if depth * 1.2 > avoid_depth:
                            avoid_depth = depth * 1.2
        each_wall_win_occupy = {}
        for win in room_info['Window']:
            if win['target_room_id'] == '':
                wall_length = np.linalg.norm(np.array(room_info['Wall'][win['related']['Wall']]['layout_pts'][0]) -
                                             np.array(room_info['Wall'][win['related']['Wall']]['layout_pts'][1]))
                if win['related']['Wall'] not in each_wall_win_occupy:
                    each_wall_win_occupy[win['related']['Wall']] = win['length'] / wall_length
                else:
                    each_wall_win_occupy[win['related']['Wall']] += win['length'] / wall_length
        for door in room_info['Door']:
            if 'Balcony' == ROOM_BUILD_TYPE[door['target_room_type']] and door['length'] > 1.:
                wall_length = np.linalg.norm(np.array(room_info['Wall'][door['related']['Wall']]['layout_pts'][0]) -
                                             np.array(room_info['Wall'][door['related']['Wall']]['layout_pts'][1]))
                if door['related']['Wall'] not in each_wall_win_occupy:
                    each_wall_win_occupy[door['related']['Wall']] = door['length'] / wall_length
                else:
                    each_wall_win_occupy[door['related']['Wall']] += door['length'] / wall_length
        refined_floor_pts = copy.deepcopy(floor_pts)
        for wall, win_ratio in each_wall_win_occupy.items():
            wall_length = np.linalg.norm(np.array(room_info['Wall'][wall]['layout_pts'][0]) -
                                         np.array(room_info['Wall'][wall]['layout_pts'][1]))
            if win_ratio >= 0.5 and wall_length > 1.5:
                if (abs(refined_floor_pts[wall][0] - refined_floor_pts[(wall + 1) % len(refined_floor_pts)][
                    0]) < 1e-4 and
                    abs(refined_floor_pts[wall][0] - refined_floor_pts[(wall - 1) % len(refined_floor_pts)][0]) < 1e-4) \
                        or \
                        (abs(refined_floor_pts[wall][1] - refined_floor_pts[(wall + 1) % len(refined_floor_pts)][
                            1]) < 1e-4 and
                         abs(refined_floor_pts[wall][1] - refined_floor_pts[(wall - 1) % len(refined_floor_pts)][
                             1]) < 1e-4):
                    refined_floor_pts[(wall - 1) % len(refined_floor_pts)] = (
                                np.array(room_info['Wall'][wall]['normal'])
                                * avoid_depth + np.array(
                            refined_floor_pts[(wall - 1) % len(refined_floor_pts)])).tolist()
                if (abs(refined_floor_pts[wall][0] - refined_floor_pts[(wall + 1) % len(refined_floor_pts)][
                    0]) < 1e-4 and
                    abs(refined_floor_pts[(wall + 1) % len(refined_floor_pts)][0] -
                        refined_floor_pts[(wall + 2) % len(refined_floor_pts)][0]) < 1e-4) \
                        or \
                        (abs(refined_floor_pts[wall][1] - refined_floor_pts[(wall + 1) % len(refined_floor_pts)][
                            1]) < 1e-4 and
                         abs(refined_floor_pts[(wall + 1) % len(refined_floor_pts)][1] -
                             refined_floor_pts[(wall + 2) % len(refined_floor_pts)][1]) < 1e-4):
                    refined_floor_pts[(wall + 2) % len(refined_floor_pts)] = (
                                np.array(room_info['Wall'][wall]['normal'])
                                * avoid_depth + np.array(
                            refined_floor_pts[(wall + 2) % len(refined_floor_pts)])).tolist()
                refined_floor_pts[wall] = (np.array(room_info['Wall'][wall]['normal']) * avoid_depth + np.array(
                    refined_floor_pts[wall])).tolist()
                refined_floor_pts[(wall + 1) % len(refined_floor_pts)] = (np.array(
                    room_info['Wall'][wall]['normal']) * avoid_depth + np.array(
                    refined_floor_pts[(wall + 1) % len(refined_floor_pts)])).tolist()

        cabinet_extra_area = []
        if ROOM_BUILD_TYPE[room_info['type']] in PRIME_GENERAL_WALL_ROOM_TYPES:
            cabinet_wall_depth = {}
            for layout in layouts:
                if layout['type'] in ['Cabinet', 'Armoire'] and layout['size'][1] > 1.7:
                    depth = layout['size'][2]

                    object_one = {
                        'size': layout['size'],
                        'position': layout['position'],
                        'rotation': layout['rotation'],
                        'type': layout['type'],
                        'scale': [1, 1, 1.]
                    }
                    edge_idx, _ = compute_furniture_rely(object_one, floor_pts, rely_dlt=1.)
                    if 'back_p1' not in layout or 'back_p2' not in layout or len(layout['back_p1']) == 0 or len(layout['back_p2']) == 0:
                        if edge_idx == -1:
                            continue
                        bed_back_pts = [floor_pts[edge_idx], floor_pts[(edge_idx + 1) % len(floor_pts)]]
                    else:
                        bed_back_pts = [layout['back_p1'], layout['back_p2']]
                        if edge_idx != -1:
                            bed_back_len = np.linalg.norm(np.array(bed_back_pts[0]) - bed_back_pts[1])
                            wall_edge = [floor_pts[edge_idx], floor_pts[(edge_idx + 1) % len(floor_pts)]]
                            flag, remained, removed = is_coincident_line(wall_edge, bed_back_pts)
                            if flag:
                                for remained_edge in remained:
                                    if np.linalg.norm(
                                            np.array(remained_edge[0]) - remained_edge[1]) > bed_back_len * 0.4:
                                        scale = bed_back_len * 0.3
                                    else:
                                        scale = None
                                    is_valid = True
                                    for opening in room_info['Window'] + room_info['Hole'] + room_info['Door']:
                                        if opening['related']['Wall'] == edge_idx:
                                            flag_open, remained_open, removed_open = is_coincident_line(
                                                opening['layout_pts'], remained_edge)
                                            if flag_open:
                                                is_valid = False
                                                break
                                    if is_valid:
                                        _, bed_back_pts = extend_edge(bed_back_pts, remained_edge, max_len=scale)
                    bed_back_pts_center = np.mean(bed_back_pts, axis=0)
                    if len(bed_back_pts_center) == 0:
                        continue
                    shrinked_bed_back_pts = (np.array(bed_back_pts) - bed_back_pts_center) * 0.5 + bed_back_pts_center
                    for i in range(len(floor_pts)):
                        wall = [floor_pts[i], floor_pts[(i + 1) % len(floor_pts)]]
                        if np.linalg.norm(np.array(floor_pts[i]) - np.array(floor_pts[(i + 1) % len(floor_pts)])) < 0.1:
                            continue

                        v1 = (shrinked_bed_back_pts[1] - wall[0]) / np.linalg.norm((shrinked_bed_back_pts[1] - wall[0]))
                        v2 = (shrinked_bed_back_pts[1] - wall[1]) / np.linalg.norm((shrinked_bed_back_pts[1] - wall[1]))
                        cond1 = abs(v1[0] * v2[1] - v1[1] * v2[0]) < 1e-3
                        v1 = (shrinked_bed_back_pts[0] - wall[0]) / np.linalg.norm((shrinked_bed_back_pts[0] - wall[0]))
                        v2 = (shrinked_bed_back_pts[0] - wall[1]) / np.linalg.norm((shrinked_bed_back_pts[0] - wall[1]))
                        cond2 = abs(v1[0] * v2[1] - v1[1] * v2[0]) < 1e-3

                        if cond1 and cond2:
                            if i in cabinet_wall_depth:
                                if depth > cabinet_wall_depth[i]:
                                    cabinet_wall_depth[i] = depth
                            else:
                                cabinet_wall_depth[i] = depth
                            break

            for wall, depth in cabinet_wall_depth.items():
                cabinet_avoid_area = [copy.deepcopy(refined_floor_pts[wall]),
                                      copy.deepcopy(refined_floor_pts[(wall + 1) % len(refined_floor_pts)]),
                                      ]
                refined_floor_pts[wall] = (np.array(room_info['Wall'][wall]['normal']) * depth + np.array(
                    refined_floor_pts[wall])).tolist()
                refined_floor_pts[(wall + 1) % len(refined_floor_pts)] = (np.array(
                    room_info['Wall'][wall]['normal']) * depth + np.array(
                    refined_floor_pts[(wall + 1) % len(refined_floor_pts)])).tolist()
                cabinet_avoid_area.append(refined_floor_pts[(wall + 1) % len(refined_floor_pts)])
                cabinet_avoid_area.append(refined_floor_pts[wall])
                cabinet_extra_area.append(copy.deepcopy(cabinet_avoid_area))
        return refined_floor_pts, cabinet_extra_area

    def config_area(self, room_info, living_rect, dining_rect, hallway_rect, remained_area,
                    avoid_cabinet_area=[],
                    layout_info=[],
                    refined_floor_pts=None):
        wall_attrs = ['Meeting', 'Media', 'Hallway', 'Bed', 'Balcony', 'Open']
        floor_pts = room_info['floor_pts']
        living_dining_min_dis_pair = [-1, -1]

        if living_rect is not None:
            if is_hallway(room_info['type']):
                ceiling_type = 'hallway'
                l = np.linalg.norm(np.array(living_rect[0]) - np.array(living_rect[1]))
                w = np.linalg.norm(np.array(living_rect[1]) - np.array(living_rect[2]))
                if l > w:
                    wall_attr = ['Hallway', '', 'Hallway', '']
                else:
                    wall_attr = ['', 'Hallway', '', 'Hallway']

            elif ROOM_BUILD_TYPE[room_info['type']] == 'Library':
                ceiling_type = 'work'
                wall_attr = ['', '', '', '']
            elif ROOM_BUILD_TYPE[room_info['type']] in PRIME_GENERAL_WALL_ROOM_TYPES:
                ceiling_type = 'bed'
                wall_attr = ['', '', '', '']
                for layout in layout_info:
                    if layout['type'] in ['Bed', 'Media'] and room_info['type'] in PRIME_GENERAL_WALL_ROOM_TYPES:
                        object_one = {
                            'size': layout['size'],
                            'position': layout['position'],
                            'rotation': layout['rotation'],
                            'type': layout['type'],
                            'scale': [1, 1, 1.]
                        }
                        edge_idx, _ = compute_furniture_rely(object_one, floor_pts, rely_dlt=1.)
                        if 'back_p1' not in layout or 'back_p2' not in layout or len(layout['back_p1']) == 0 or len(layout['back_p2']) == 0:
                            if edge_idx == -1:
                                continue
                            bed_back_pts = [floor_pts[edge_idx], floor_pts[(edge_idx + 1) % len(floor_pts)]]
                        else:
                            bed_back_pts = [layout['back_p1'], layout['back_p2']]
                            if edge_idx != -1:
                                bed_back_len = np.linalg.norm(np.array(bed_back_pts[0]) - bed_back_pts[1])
                                wall_edge = [floor_pts[edge_idx], floor_pts[(edge_idx + 1) % len(floor_pts)]]
                                flag, remained, removed = is_coincident_line(wall_edge, bed_back_pts)
                                if flag:
                                    for remained_edge in remained:
                                        if np.linalg.norm(
                                                np.array(remained_edge[0]) - remained_edge[1]) > bed_back_len * 0.4:
                                            scale = bed_back_len * 0.3
                                        else:
                                            scale = None
                                        is_valid = True
                                        for opening in room_info['Window'] + room_info['Hole'] + room_info['Door']:
                                            if opening['related']['Wall'] == edge_idx:
                                                flag_open, remained_open, removed_open = is_coincident_line(
                                                    opening['layout_pts'], remained_edge)
                                                if flag_open:
                                                    is_valid = False
                                        if is_valid:
                                            _, bed_back_pts = extend_edge(bed_back_pts, remained_edge, max_len=scale)
                        bed_back_pts_center = np.mean(bed_back_pts, axis=0)
                        if len(bed_back_pts_center) == 0:
                            continue
                        min_dis = 1e8
                        min_edge = 0
                        for i in range(4):
                            line = np.array([living_rect[i], living_rect[(i + 1) % 4]])
                            vect1 = line[1] - line[0]
                            vect2 = bed_back_pts_center - line[0]
                            if 0. < np.dot(vect1, vect2) / np.linalg.norm(vect1) / np.linalg.norm(vect1) < 1.:
                                dis = abs(np.cross(vect1, vect2) / np.linalg.norm(vect1))
                                if dis < min_dis:
                                    min_dis = dis
                                    min_edge = i
                        wall_attr[min_edge] = layout['type']
                if 'Media' in wall_attr and 'Bed' not in wall_attr:
                    for a_ind, attr in enumerate(wall_attr):
                        if attr == 'Media':
                            wall_attr[(a_ind + 2) % len(wall_attr)] = 'Bed'
                            break
            else:
                ceiling_type = 'living'
                wall_attr = ['', '', '', '']
                for layout in layout_info:
                    if layout['type'] in ['Meeting', 'Media'] and ROOM_BUILD_TYPE[room_info['type']] == 'LivingDiningRoom':
                        object_one = {
                            'size': layout['size'],
                            'position': layout['position'],
                            'rotation': layout['rotation'],
                            'type': layout['type'],
                            'scale': [1, 1, 1.]
                        }
                        edge_idx, _ = compute_furniture_rely(object_one, floor_pts, rely_dlt=1.)
                        if 'back_p1' not in layout or 'back_p2' not in layout or len(layout['back_p1']) == 0 or len(
                                layout['back_p2']) == 0:
                            if edge_idx == -1:
                                continue
                            back_pts = [floor_pts[edge_idx], floor_pts[(edge_idx + 1) % len(floor_pts)]]
                        else:
                            back_pts = [layout['back_p1'], layout['back_p2']]
                            if edge_idx != -1:
                                bed_back_len = np.linalg.norm(np.array(back_pts[0]) - back_pts[1])
                                wall_edge = [floor_pts[edge_idx], floor_pts[(edge_idx + 1) % len(floor_pts)]]
                                flag, remained, removed = is_coincident_line(wall_edge, back_pts)
                                if flag:
                                    for remained_edge in remained:
                                        if np.linalg.norm(
                                                np.array(remained_edge[0]) - remained_edge[1]) > bed_back_len * 0.4:
                                            scale = bed_back_len * 0.3
                                        else:
                                            scale = None
                                        is_valid = True
                                        for opening in room_info['Window'] + room_info['Hole'] + room_info['Door']:
                                            if opening['related']['Wall'] == edge_idx:
                                                flag_open, remained_open, removed_open = is_coincident_line(
                                                    opening['layout_pts'], remained_edge)
                                                if flag_open:
                                                    is_valid = False
                                                    break
                                        if is_valid:
                                            _, back_pts = extend_edge(back_pts, remained_edge, max_len=scale)
                        back_pts_center = np.mean(back_pts, axis=0)
                        if len(back_pts_center) == 0:
                            continue
                        min_dis = 1e8
                        min_edge = 0
                        for i in range(4):
                            line = np.array([living_rect[i], living_rect[(i + 1) % 4]])
                            vect1 = line[1] - line[0]
                            vect2 = back_pts_center - line[0]
                            if 0. < np.dot(vect1, vect2) / np.linalg.norm(vect1) / np.linalg.norm(vect1) < 1.:
                                dis = abs(np.cross(vect1, vect2) / np.linalg.norm(vect1))
                                if dis < min_dis:
                                    min_dis = dis
                                    min_edge = i
                        wall_attr[min_edge] = layout['type']

                for door in room_info['Door']:
                    door_target_type = ROOM_BUILD_TYPE[door['target_room_type']]
                    if door_target_type == 'Balcony':
                        pos = np.mean(door['layout_pts'], axis=0)
                        for i in range(4):
                            line = np.array(living_rect[(i + 1) % 4]) - np.array(living_rect[i])
                            door_line = pos - np.array(living_rect[i])
                            proj = np.dot(door_line, line) / np.linalg.norm(line) / np.linalg.norm(line)
                            if 0. < proj < 1.:
                                dis = np.cross(line, door_line) / np.linalg.norm(line)
                                if abs(dis) < 0.5:
                                    wall_attr[i] = 'Balcony'
                for win in room_info['Window']:
                    win_length = win['length']
                    wall_pts = np.array(room_info['Wall'][win['related']['Wall']]['layout_pts'])
                    wall_length = np.linalg.norm(wall_pts[1] - wall_pts[0])
                    if win_length / (wall_length + 1e-3) > 0.5:
                        pos = np.mean(win['layout_pts'], axis=0)
                        for i in range(4):
                            line = np.array(living_rect[(i + 1) % 4]) - np.array(living_rect[i])
                            win_line = pos - np.array(living_rect[i])
                            proj = np.dot(win_line, line) / np.linalg.norm(line) / np.linalg.norm(line)
                            if 0. < proj < 1.:
                                dis = np.cross(line, win_line) / np.linalg.norm(line)
                                if abs(dis) < 0.5:
                                    wall_attr[i] = 'Balcony'

                if dining_rect is not None:
                    min_dis = 1e8
                    for i in range(4):
                        living_edge = np.array([living_rect[i], living_rect[(i + 1) % 4]])
                        for j in range(4):
                            dining_edge = np.array([dining_rect[j], dining_rect[(j + 1) % 4]])
                            if abs(np.cross(dining_edge[1] - dining_edge[0], living_edge[1] - living_edge[0])) > 1e-3:
                                continue

                            vect1 = living_edge[0] - dining_edge[0]
                            vect2 = living_edge[1] - dining_edge[0]

                            line_vect = dining_edge[1] - dining_edge[0]

                            proj1 = np.dot(vect1, line_vect) / np.linalg.norm(line_vect) / np.linalg.norm(line_vect)
                            proj2 = np.dot(vect2, line_vect) / np.linalg.norm(line_vect) / np.linalg.norm(line_vect)
                            if (proj1 < 1e-3 and proj2 < 1e-3) or (proj1 > 1 - 1e-3 and proj2 > 1 - 1e-3):
                                continue
                            dis = abs(np.cross(vect1, line_vect) / np.linalg.norm(line_vect))
                            if dis < min_dis:
                                living_dining_min_dis_pair = [i, j]
                                min_dis = dis
                    if -1 not in living_dining_min_dis_pair and wall_attr[living_dining_min_dis_pair[0]] == '':
                        wall_attr[living_dining_min_dis_pair[0]] = 'Open'
                    # open_edge_ind = -1
                    # for edge_ind in range(4):
                    #     if wall_attr[edge_ind] == 'Open':
                    #         if open_edge_ind == -1:
                    #             open_edge_ind = edge_ind
                    #         else:
                    #             open_edge_ind = -1
                    #             break
                    # if open_edge_ind >= 0:
                    #     wall_attr[(open_edge_ind - 1) % 4] = 'Dining'
                    #     wall_attr[(open_edge_ind + 1) % 4] = 'Dining'
                else:
                    if room_info['type'] == 'DiningRoom' and 'Meeting' not in wall_attr and 'Media' not in wall_attr:
                        ceiling_type = 'dining'
                # for i in range(4):
                #     has_coincident_floor = False
                #     rect_line = np.array([living_rect[i], living_rect[(i + 1) % 4]])
                #     for floor_ind in range(len(refined_floor_pts)):
                #         line = np.array([refined_floor_pts[floor_ind], refined_floor_pts[(floor_ind + 1) % len(refined_floor_pts)]])
                #         if abs(np.cross(rect_line[1] - rect_line[0], line[1] - line[0])) > 1e-3:
                #             continue
                #         rect_cross_line = rect_line[1] - line[0]
                #         line_vect = line[1] - line[0]
                #         if np.cross(rect_cross_line, line_vect) / np.linalg.norm(line_vect) < 1e-3:
                #
                #             has_coincident_floor = True
                #             break
                #     if not has_coincident_floor and wall_attr[i] == '':
                #         wall_attr[i] = 'Dangling'

            room_info['CustomizedCeiling'].append({'name': room_info['id'] + '_%s_customizedCeiling' % ceiling_type,
                                                   'type': ceiling_type,
                                                   'layout_pts': living_rect,
                                                   'edge_attr': wall_attr,
                                                   'room_height': self.room_height,
                                                   'ceiling_height': self.default_ceiling_height,
                                                   'related': {},
                                                   'mesh': self.is_customized_ceiling,
                                                   'obj_info': {
                                                       # 'name': '',
                                                       # 'pos': [0, 0, 0],
                                                       # 'rot': [0, 0, 0, 1],
                                                       # 'jid': '',
                                                       'ceiling': [],
                                                       'SpotLight': [],
                                                       'MeshLight': []
                                                   },
                                                   'material': {}
                                                   }
                                                  )
        if dining_rect is not None:
            wall_attr = ['', '', '', '']
            for door in room_info['Door']:
                door_target_type = ROOM_BUILD_TYPE[door['target_room_type']]
                if door_target_type == 'Balcony':
                    pos = np.mean(door['layout_pts'], axis=0)
                    for i in range(4):
                        line = np.array(dining_rect[(i + 1) % 4]) - np.array(dining_rect[i])
                        door_line = pos - np.array(dining_rect[i])
                        proj = np.dot(door_line, line) / np.linalg.norm(line) / np.linalg.norm(line)
                        if 0. < proj < 1.:
                            dis = np.cross(line, door_line) / np.linalg.norm(line)
                            if abs(dis) < 0.5:
                                wall_attr[i] = 'Balcony'
            if -1 not in living_dining_min_dis_pair and wall_attr[living_dining_min_dis_pair[1]] == '':
                wall_attr[living_dining_min_dis_pair[1]] = 'Open'
            open_edge_ind = -1
            for edge_ind in range(4):
                if wall_attr[edge_ind] == 'Open':
                    if open_edge_ind == -1:
                        open_edge_ind = edge_ind
                    else:
                        open_edge_ind = -1
                        break
            if open_edge_ind >= 0:
                wall_attr[(open_edge_ind - 1) % 4] = 'Dining'
                wall_attr[(open_edge_ind + 1) % 4] = 'Dining'
            # for i in range(4):
            #     has_coincident_floor = False
            #     rect_line = np.array([dining_rect[i], dining_rect[(i + 1) % 4]])
            #     for floor_ind in range(len(refined_floor_pts)):
            #         line = np.array(
            #             [refined_floor_pts[floor_ind], refined_floor_pts[(floor_ind + 1) % len(refined_floor_pts)]])
            #         if abs(np.cross(rect_line[1] - rect_line[0], line[1] - line[0])) > 1e-3:
            #             continue
            #         rect_cross_line = rect_line[1] - line[0]
            #         line_vect = line[1] - line[0]
            #         if np.cross(rect_cross_line, line_vect) / np.linalg.norm(line_vect) < 1e-3:
            #             has_coincident_floor = True
            #             break
            #     if not has_coincident_floor and wall_attr[i] == '':
            #         wall_attr[i] = 'Dangling'

            room_info['CustomizedCeiling'].append({'name': room_info['id'] + '_dining_customizedCeiling',
                                                   'type': 'dining',
                                                   'layout_pts': dining_rect,
                                                   'edge_attr': wall_attr,
                                                   'room_height': self.room_height,
                                                   'ceiling_height': self.default_ceiling_height,
                                                   'related': {},
                                                   'mesh': self.is_customized_ceiling,
                                                   'obj_info': {
                                                       # 'name': '',
                                                       # 'pos': [0, 0, 0],
                                                       # 'rot': [0, 0, 0, 1],
                                                       # 'jid': '',

                                                       'ceiling': [],
                                                       'SpotLight': [],
                                                       'MeshLight': []
                                                   },
                                                   'material': {}
                                                   }
                                                  )
        if hallway_rect is not None:
            l = np.linalg.norm(np.array(hallway_rect[0]) - np.array(hallway_rect[1]))
            w = np.linalg.norm(np.array(hallway_rect[1]) - np.array(hallway_rect[2]))
            if l > w:
                wall_attr = ['Hallway', '', 'Hallway', '']
            else:
                wall_attr = ['', 'Hallway', '', 'Hallway']
            room_info['CustomizedCeiling'].append({'name': room_info['id'] + '_hallway_customizedCeiling',
                                                   'type': 'hallway',
                                                   'layout_pts': hallway_rect,
                                                   'edge_attr': wall_attr,
                                                   'room_height': self.room_height,
                                                   'ceiling_height': self.default_ceiling_height,
                                                   'related': {},
                                                   'mesh': self.is_customized_ceiling,
                                                   'obj_info': {
                                                       # 'name': '',
                                                       # 'pos': [0, 0, 0],
                                                       # 'rot': [0, 0, 0, 1],
                                                       # 'jid': '',
                                                       'ceiling': [],
                                                       'SpotLight': [],
                                                       'MeshLight': []
                                                   },
                                                   'material': {}
                                                   }
                                                  )
        for i, extra in enumerate(remained_area):
            if len(extra) < 3:
                continue
            room_info['CustomizedCeiling'].append({'name': room_info['id'] + '_extra_customizedCeiling' + '_%d' % i,
                                                   'type': 'extra',
                                                   'layout_pts': extra,
                                                   'room_height': self.room_height,
                                                   'ceiling_height': self.default_ceiling_height,
                                                   'related': {},
                                                   'mesh': self.is_customized_ceiling,
                                                   'obj_info': {
                                                       # 'name': '',
                                                       # 'pos': [0, 0, 0],
                                                       # 'rot': [0, 0, 0, 1],
                                                       # 'jid': '',
                                                       'ceiling': [],
                                                       'SpotLight': [],
                                                       'MeshLight': []
                                                   },
                                                   'material': {}
                                                   }
                                                  )
        for i, extra in enumerate(avoid_cabinet_area):
            if len(extra) < 3:
                continue
            room_info['CustomizedCeiling'].append({'name': room_info['id'] + '_cabinet_customizedCeiling' + '_%d' % i,
                                                   'type': 'cabinet',
                                                   'layout_pts': extra,
                                                   'room_height': self.room_height,
                                                   'ceiling_height': self.default_ceiling_height,
                                                   'related': {},
                                                   'mesh': self.is_customized_ceiling,
                                                   'obj_info': {
                                                       # 'name': '',
                                                       # 'pos': [0, 0, 0],
                                                       # 'rot': [0, 0, 0, 1],
                                                       # 'jid': '',
                                                       'ceiling': [],
                                                       'SpotLight': [],
                                                       'MeshLight': []
                                                   },
                                                   'material': {}
                                                   }
                                                  )

    def seg_main_wall(self, room_info, layout_info):
        floor_pts = room_info['floor_pts']
        for layout in layout_info:
            if layout['type'] in ['Bed', 'Media'] and room_info['type'] in PRIME_GENERAL_WALL_ROOM_TYPES:
                object_one = {
                    'size': layout['size'],
                    'position': layout['position'],
                    'rotation': layout['rotation'],
                    'type': layout['type'],
                    'scale': [1, 1, 1.]
                }
                edge_idx, _ = compute_furniture_rely(object_one, floor_pts, rely_dlt=1.)
                if 'back_p1' not in layout or 'back_p2' not in layout or len(layout['back_p1']) == 0 or len(layout['back_p2']) == 0:
                    if edge_idx == -1:
                        continue
                    bed_back_pts = [floor_pts[edge_idx], floor_pts[(edge_idx + 1) % len(floor_pts)]]
                else:
                    bed_back_pts = [layout['back_p1'], layout['back_p2']]
                    if edge_idx != -1:
                        bed_back_len = np.linalg.norm(np.array(bed_back_pts[0]) - bed_back_pts[1])
                        wall_edge = [floor_pts[edge_idx], floor_pts[(edge_idx + 1) % len(floor_pts)]]
                        flag, remained, removed = is_coincident_line(wall_edge, bed_back_pts)
                        if flag:
                            for remained_edge in remained:
                                if np.linalg.norm(
                                        np.array(remained_edge[0]) - remained_edge[1]) > bed_back_len * 0.4:
                                    scale = bed_back_len * 0.3
                                else:
                                    scale = None
                                is_valid = True
                                for opening in room_info['Window'] + room_info['Hole'] + room_info['Door']:
                                    if opening['related']['Wall'] == edge_idx:
                                        flag_open, remained_open, removed_open = is_coincident_line(
                                            opening['layout_pts'], remained_edge)
                                        if flag_open:
                                            is_valid = False
                                            break
                                if is_valid:
                                    _, bed_back_pts = extend_edge(bed_back_pts, remained_edge, max_len=scale)
                bed_back_pts_center = np.mean(bed_back_pts, axis=0)
                if len(bed_back_pts_center) == 0:
                    continue
                shrinked_bed_back_pts = (np.array(bed_back_pts) - bed_back_pts_center) * 0.5 + bed_back_pts_center
                for wallInner in room_info['Wall']:
                    wall = wallInner['layout_pts']
                    if np.linalg.norm(np.array(wall[0]) - wall[1]) < 1e-1:
                        continue
                    v1 = (shrinked_bed_back_pts[1] - wall[0]) / np.linalg.norm((shrinked_bed_back_pts[1] - wall[0]))
                    v2 = (shrinked_bed_back_pts[1] - wall[1]) / np.linalg.norm((shrinked_bed_back_pts[1] - wall[1]))
                    cond1 = abs(v1[0] * v2[1] - v1[1] * v2[0]) < 1e-3
                    v1 = (shrinked_bed_back_pts[0] - wall[0]) / np.linalg.norm((shrinked_bed_back_pts[0] - wall[0]))
                    v2 = (shrinked_bed_back_pts[0] - wall[1]) / np.linalg.norm((shrinked_bed_back_pts[0] - wall[1]))
                    cond2 = abs(v1[0] * v2[1] - v1[1] * v2[0]) < 1e-3

                    if np.linalg.norm((shrinked_bed_back_pts[0] - wall[0])) < np.linalg.norm((shrinked_bed_back_pts[1] - wall[0])):
                        v1 = shrinked_bed_back_pts[0] - wall[0]
                        v2 = shrinked_bed_back_pts[1] - wall[1]
                        v_wall = np.array(wall[0]) - wall[1]
                        v_bed_bp = np.array(shrinked_bed_back_pts[0]) - shrinked_bed_back_pts[1]
                    else:
                        v1 = shrinked_bed_back_pts[0] - wall[1]
                        v2 = shrinked_bed_back_pts[1] - wall[0]
                        v_wall = np.array(wall[0]) - wall[1]
                        v_bed_bp = np.array(shrinked_bed_back_pts[0]) - shrinked_bed_back_pts[1]
                    cond3 = abs(np.linalg.norm(v1) + np.linalg.norm(v2) + np.linalg.norm(v_bed_bp) - np.linalg.norm(v_wall)) < 0.1 * np.linalg.norm(v_wall)

                    if (cond1 and cond2) or cond3:
                        if layout['type'] == 'Bed':
                            bed_wall_ind = wallInner['name']
                            bed_wall_expand_ind = (bed_wall_ind - 1) % len(room_info['floor_pts'])
                            if not len([i for i in room_info['Window'] if
                                        i['related']['Wall'] == bed_wall_expand_ind]) > 0:
                                bed_wall_expand_ind = (bed_wall_ind + 1) % len(room_info['floor_pts'])
                                if not len([i for i in room_info['Window'] if
                                            i['related']['Wall'] == bed_wall_expand_ind]) > 0:
                                    bed_wall_expand_ind = (bed_wall_ind - 1) % len(room_info['floor_pts'])
                                    if not len([i for i in room_info['Window'] if
                                                i['related']['Wall'] == bed_wall_expand_ind]) > 0:
                                        bed_wall_expand_ind = (bed_wall_ind + 1) % len(room_info['floor_pts'])

                            flag, remained, removed = is_coincident_line(wall, bed_back_pts)
                            wall_length = np.linalg.norm(np.array(wall[0]) - np.array(wall[1]))
                            bed_back_wall_length = np.linalg.norm(np.array(bed_back_pts[0]) - np.array(bed_back_pts[1]))
                            for remained_wall in remained:
                                length = np.linalg.norm(np.array(remained_wall[0]) - np.array(remained_wall[1]))
                                if length / wall_length < 0.33:
                                    valid_flag = True
                                    for door in room_info['Door'] + room_info['Window'] + room_info['Hole']:
                                        door_wall = door['layout_pts']
                                        flag, _, _ = is_coincident_line(remained_wall, door_wall)
                                        if flag:
                                            valid_flag = False
                                            break
                                    if valid_flag:
                                        start = remained_wall[0]
                                        end = remained_wall[1]
                                        if np.linalg.norm(np.array(start) - np.array(bed_back_pts[0])) < \
                                                np.linalg.norm(np.array(end) - np.array(bed_back_pts[0])):
                                            start = remained_wall[1]
                                            end = remained_wall[0]
                                        bed_back_pts = [start, ((np.array(end) - np.array(start)) * (
                                                    length + bed_back_wall_length) / length + np.array(start)).tolist()]
                                        bed_back_wall_length = np.linalg.norm(
                                            np.array(bed_back_pts[0]) - np.array(bed_back_pts[1]))
                            bed_back_pts = np.array(bed_back_pts).tolist()
                            wallInner['functional']['PrimeBed'] = bed_back_pts
                            room_info['Wall'][bed_wall_expand_ind]['functional']['SubPrimeBed'] = wallInner['name']
                            for s in wallInner['segments']:
                                s['Functional'] = {
                                    'PrimeBed': bed_back_pts,
                                    'SubPrimeBed': wallInner['name']
                                }
                        elif layout['type'] == 'Media':
                            wallInner['functional']['Media'] = bed_back_pts
                            for s in wallInner['segments']:
                                s['Functional'] = {
                                    'Media': bed_back_pts
                                }

            if layout['type'] in ['Meeting', 'Media'] and ROOM_BUILD_TYPE[room_info['type']] == 'LivingDiningRoom':
                object_one = {
                    'size': layout['size'],
                    'position': layout['position'],
                    'rotation': layout['rotation'],
                    'type': layout['type'],
                    'scale': [1, 1, 1.]
                }
                edge_idx, _ = compute_furniture_rely(object_one, floor_pts, rely_dlt=1.)
                if 'back_p1' not in layout or 'back_p2' not in layout or len(layout['back_p1']) == 0 or len(layout['back_p2']) == 0:
                    if edge_idx == -1:
                        continue
                    back_pts = [floor_pts[edge_idx], floor_pts[(edge_idx + 1) % len(floor_pts)]]
                else:
                    back_pts = [layout['back_p1'], layout['back_p2']]
                    if edge_idx != -1:
                        bed_back_len = np.linalg.norm(np.array(back_pts[0]) - back_pts[1])
                        wall_edge = [floor_pts[edge_idx], floor_pts[(edge_idx + 1) % len(floor_pts)]]
                        flag, remained, removed = is_coincident_line(wall_edge, back_pts)
                        if flag:
                            for remained_edge in remained:
                                if np.linalg.norm(
                                        np.array(remained_edge[0]) - remained_edge[1]) > bed_back_len * 0.4:
                                    scale = bed_back_len * 0.3
                                else:
                                    scale = None
                                is_valid = True
                                for opening in room_info['Window'] + room_info['Hole'] + room_info['Door']:
                                    if opening['related']['Wall'] == edge_idx:
                                        flag_open, remained_open, removed_open = is_coincident_line(
                                            opening['layout_pts'], remained_edge)
                                        if flag_open:
                                            is_valid = False
                                if is_valid:
                                    _, back_pts = extend_edge(back_pts, remained_edge, max_len=scale)
                back_pts_center = np.mean(back_pts, axis=0)
                if len(back_pts_center) == 0:
                    continue
                shrinked_bed_back_pts = (np.array(back_pts) - back_pts_center) * 0.5 + back_pts_center
                for wallInner in room_info['Wall']:
                    wall = wallInner['layout_pts']
                    if np.linalg.norm(np.array(wall[0]) - wall[1]) < 1e-1:
                        continue
                    v1 = (shrinked_bed_back_pts[1] - wall[0]) / np.linalg.norm((shrinked_bed_back_pts[1] - wall[0]))
                    v2 = (shrinked_bed_back_pts[1] - wall[1]) / np.linalg.norm((shrinked_bed_back_pts[1] - wall[1]))
                    cond1 = abs(v1[0] * v2[1] - v1[1] * v2[0]) < 1e-3
                    v1 = (shrinked_bed_back_pts[0] - wall[0]) / np.linalg.norm((shrinked_bed_back_pts[0] - wall[0]))
                    v2 = (shrinked_bed_back_pts[0] - wall[1]) / np.linalg.norm((shrinked_bed_back_pts[0] - wall[1]))
                    cond2 = abs(v1[0] * v2[1] - v1[1] * v2[0]) < 1e-3

                    if np.linalg.norm((shrinked_bed_back_pts[0] - wall[0])) < np.linalg.norm((shrinked_bed_back_pts[1] - wall[0])):
                        v1 = shrinked_bed_back_pts[0] - wall[0]
                        v2 = shrinked_bed_back_pts[1] - wall[1]
                        v_wall = np.array(wall[0]) - wall[1]
                        v_bed_bp = np.array(shrinked_bed_back_pts[0]) - shrinked_bed_back_pts[1]
                    else:
                        v1 = shrinked_bed_back_pts[0] - wall[1]
                        v2 = shrinked_bed_back_pts[1] - wall[0]
                        v_wall = np.array(wall[0]) - wall[1]
                        v_bed_bp = np.array(shrinked_bed_back_pts[0]) - shrinked_bed_back_pts[1]
                    cond3 = abs(np.linalg.norm(v1) + np.linalg.norm(v2) + np.linalg.norm(v_bed_bp) - np.linalg.norm(v_wall)) < 0.1 * np.linalg.norm(v_wall)

                    if (cond1 and cond2) or cond3:
                        flag, remained, removed = is_coincident_line(wall, back_pts)
                        wall_length = np.linalg.norm(np.array(wall[0]) - np.array(wall[1]))
                        back_wall_length = np.linalg.norm(np.array(back_pts[0]) - np.array(back_pts[1]))
                        for remained_wall in remained:
                            length = np.linalg.norm(np.array(remained_wall[0]) - np.array(remained_wall[1]))
                            if length / wall_length < 0.33:
                                valid_flag = True
                                for door in room_info['Door'] + room_info['Window'] + room_info['Hole']:
                                    door_wall = door['layout_pts']
                                    flag, _, _ = is_coincident_line(remained_wall, door_wall)
                                    if flag:
                                        valid_flag = False
                                        break
                                if valid_flag:
                                    start = remained_wall[0]
                                    end = remained_wall[1]
                                    if np.linalg.norm(np.array(start) - np.array(back_pts[0])) < \
                                            np.linalg.norm(np.array(end) - np.array(back_pts[0])):
                                        start = remained_wall[1]
                                        end = remained_wall[0]
                                    back_pts = [start, ((np.array(end) - np.array(start)) * (
                                            length + back_wall_length) / length + np.array(start)).tolist()]
                                    back_wall_length = np.linalg.norm(
                                        np.array(back_pts[0]) - np.array(back_pts[1]))

                        flag, remained, removed = is_coincident_line(wall, back_pts)
                        removed = np.array(removed).tolist()
                        back_pts = np.array(back_pts).tolist()
                        if flag:
                            wallInner['functional'][layout['type']] = removed
                        else:
                            wallInner['functional'][layout['type']] = back_pts
                        break

    @staticmethod
    def seg_wall_with_room_area(room_info):
        # plot_split_regions(room_info)
        for cus in room_info['CustomizedCeiling']:
            if cus['type'] in ['living', 'dining', 'hallway']:
                for i, edge_attr in enumerate(cus['edge_attr']):
                    if edge_attr in ['Meeting', 'Media', 'Dining', 'Hallway']:
                        func_area_edge = [cus['layout_pts'][i], cus['layout_pts'][(i + 1) % 4]]
                        for wall in room_info['Wall']:
                            wall_edge = wall['layout_pts']
                            wall_name = wall['name']
                            # 墙线交叉
                            flag, remained, removed = is_coincident_line(wall_edge, func_area_edge)
                            if flag:
                                # wall['functional'][edge_attr] = removed
                                split_seg = {}
                                new_seg_name = {}
                                split_seg_list = []
                                segments = wall['segments']
                                for sid, s in enumerate(segments):
                                    seg_wall = [s['line_pts_list'][0], s['line_pts_list'][-1]]
                                    # 墙段交叉
                                    flag_seg, remained_seg, removed_seg = is_coincident_line(seg_wall, func_area_edge)
                                    if flag_seg:
                                        # 该段完全被包含，直接置为功能墙
                                        if len(remained_seg) == 0:
                                            s['Functional'] = edge_attr
                                        else:
                                            # print('拆墙')
                                            # 该段需要拆解为功能墙和非功能墙
                                            new_line_split_inds = [0]
                                            new_line_split_func_flag = []
                                            line_pts_list_new = copy.deepcopy(s['line_pts_list'])
                                            # line_pts_type_new = copy.deepcopy(s['line_pts_type'])
                                            win_door_info = [{'type': 0, 'bottom': 0, 'top': 0}]
                                            for ti in range(1, len(s['line_pts_list']) - 1, 2):
                                                win_door_info.append(s['line_pts_type'][ti])
                                                if win_door_info[-1]['type'] > 0:
                                                    win_door_info.append({'type': 0, 'bottom': 0, 'top': 0})
                                            win_door_info_new = copy.deepcopy(win_door_info)
                                            add_pt_num = 0
                                            for line_idx, line in enumerate(range(len(s['line_pts_list']) - 1)):
                                                line_type = win_door_info[line_idx]['type']
                                                line_pts = [s['line_pts_list'][line_idx],
                                                            s['line_pts_list'][line_idx + 1]]
                                                flag_line, remained_line, removed_line = is_coincident_line(line_pts,
                                                                                                            func_area_edge)
                                                # 门窗切割点做调整
                                                if flag_line:
                                                    # 起始点
                                                    start_flag, end_flag = False, False

                                                    if np.linalg.norm(
                                                            np.array(removed_seg[0]) - removed_line[0]) < 1e-3:
                                                        start_flag = True
                                                    if np.linalg.norm(
                                                            np.array(removed_seg[1]) - removed_line[1]) < 1e-3:
                                                        end_flag = True
                                                    # 同时满足起点终点的，如果该段不是门窗端，则可以使用起始点进行截取
                                                    # 只满足起点的，如果该段不是门窗，则使用该点做起点，否则，使用该段的终点做起点
                                                    # 只满足终点的，如果该段不是门窗，则使用该点做起点，否则，使用该段的起点做起点
                                                    # 都不满足 表示该段处于功能线段中间，不需要处理
                                                    if start_flag or end_flag:
                                                        if start_flag and end_flag:
                                                            if line_type > 0:
                                                                # 整个功能区线段落在了一个门窗区段内，这种功能区不接受
                                                                pass
                                                            else:
                                                                start_break_pts = removed_seg[0]
                                                                end_break_pts = removed_seg[1]

                                                                if np.linalg.norm(
                                                                        np.array(line_pts[0]) - start_break_pts) > 1e-3:
                                                                    line_pts_list_new.insert(line_idx + 1,
                                                                                             start_break_pts)
                                                                    # line_pts_type_new.insert(line_idx + 1,
                                                                    #                          line_pts_type_new[line_idx])
                                                                    win_door_info_new.insert(line_idx + 1,
                                                                                             {'type': 0, 'bottom': 0,
                                                                                              'top': 0})

                                                                    new_line_split_inds.append(1 + line_idx)
                                                                    add_pt_num += 1
                                                                else:
                                                                    new_line_split_inds.append(line_idx)
                                                                new_line_split_func_flag.append(False)

                                                                if np.linalg.norm(
                                                                        np.array(line_pts[1]) - end_break_pts) > 1e-3:
                                                                    line_pts_list_new.insert(line_idx + 1 + add_pt_num,
                                                                                             end_break_pts)
                                                                    # line_pts_type_new.insert(line_idx + 1 + add_pt_num,
                                                                    #                          line_pts_type_new[line_idx + add_pt_num])
                                                                    win_door_info_new.insert(line_idx + 1 + add_pt_num,
                                                                                             {'type': 0, 'bottom': 0,
                                                                                              'top': 0})
                                                                    new_line_split_inds.append(
                                                                        line_idx + 1 + add_pt_num)
                                                                else:
                                                                    new_line_split_inds.append(
                                                                        line_idx + 1 + add_pt_num)
                                                                new_line_split_func_flag.append(True)
                                                        elif start_flag:
                                                            if line_type > 0:
                                                                # 舍弃这一段包含门窗的功能墙
                                                                start_break_pts = line_pts[1]
                                                                new_line_split_inds.append(line_idx + 1)
                                                            else:
                                                                start_break_pts = removed_seg[0]
                                                                if np.linalg.norm(
                                                                        np.array(line_pts[0]) - start_break_pts) > 1e-3:
                                                                    line_pts_list_new.insert(line_idx + 1,
                                                                                             start_break_pts)
                                                                    # line_pts_type_new.insert(line_idx + 1,
                                                                    #                          line_pts_type_new[line_idx])
                                                                    win_door_info_new.insert(line_idx + 1,
                                                                                             {'type': 0, 'bottom': 0,
                                                                                              'top': 0})
                                                                    new_line_split_inds.append(line_idx + 1)
                                                                    add_pt_num += 1
                                                                else:
                                                                    new_line_split_inds.append(line_idx)

                                                            new_line_split_func_flag.append(False)
                                                        elif end_flag:
                                                            if line_type > 0:
                                                                # 舍弃这一段包含门窗的功能墙
                                                                end_break_pts = line_pts[0]
                                                                new_line_split_inds.append(line_idx + add_pt_num)
                                                            else:
                                                                end_break_pts = removed_seg[1]
                                                                if np.linalg.norm(
                                                                        np.array(line_pts[1]) - end_break_pts) > 1e-3:
                                                                    line_pts_list_new.insert(line_idx + 1 + add_pt_num,
                                                                                             end_break_pts)
                                                                    # line_pts_type_new.insert(line_idx + 1 + add_pt_num,
                                                                    #                          line_pts_type_new[line_idx + add_pt_num])
                                                                    win_door_info_new.insert(line_idx + 1 + add_pt_num,
                                                                                             {'type': 0, 'bottom': 0,
                                                                                              'top': 0})
                                                                    new_line_split_inds.append(
                                                                        line_idx + 1 + add_pt_num)
                                                                    add_pt_num += 1
                                                                else:
                                                                    new_line_split_inds.append(
                                                                        line_idx + 1 + add_pt_num)
                                                            new_line_split_func_flag.append(True)
                                            # print('增加切断点数量: %d' % add_pt_num)
                                            # 添加额外数据
                                            if len(new_line_split_inds) > 1 and new_line_split_inds[1] == 0:
                                                new_line_split_inds.pop(0)
                                                new_line_split_func_flag.pop(0)
                                            if len(new_line_split_inds) > 1 and new_line_split_inds[-1] != len(
                                                    line_pts_list_new) - 1:
                                                new_line_split_inds.append(len(line_pts_list_new) - 1)
                                                new_line_split_func_flag.append(False)

                                            # 创建新segment
                                            for ind in range(len(new_line_split_inds) - 1):
                                                split_ind = new_line_split_inds[ind]
                                                split_ind_end = new_line_split_inds[ind + 1]
                                                split_func_flag = new_line_split_func_flag[ind]
                                                new_seg = copy.deepcopy(s)
                                                new_seg['line_pts_list'] = line_pts_list_new[
                                                                           split_ind: split_ind_end + 1]

                                                pts_type = win_door_info_new[split_ind:split_ind_end]
                                                line_pts_type_new = [{'type': 0, 'bottom': 0, 'top': 0}]
                                                for pt_type in pts_type:
                                                    if pt_type['type'] > 0:
                                                        line_pts_type_new.append(pt_type)
                                                        line_pts_type_new.append(pt_type)
                                                line_pts_type_new.append({'type': 0, 'bottom': 0, 'top': 0})
                                                if pts_type[0]['type'] > 0:
                                                    vec = np.array(new_seg['line_pts_list'][0]) - np.array(
                                                        new_seg['line_pts_list'][1])
                                                    add_p = (vec / np.linalg.norm(vec) * 2e-3 + np.array(
                                                        new_seg['line_pts_list'][0])).tolist()
                                                    new_seg['line_pts_list'].insert(0, add_p)
                                                if pts_type[-1]['type'] > 0:
                                                    vec = np.array(new_seg['line_pts_list'][-1]) - np.array(
                                                        new_seg['line_pts_list'][-2])
                                                    add_p = (vec / np.linalg.norm(vec) * 2e-3 + np.array(
                                                        new_seg['line_pts_list'][-1])).tolist()
                                                    new_seg['line_pts_list'].append(add_p)
                                                new_seg['line_pts_type'] = line_pts_type_new
                                                new_seg['line_pts_list'] = np.array(new_seg['line_pts_list']).tolist()
                                                new_seg['inner_pts'] = [new_seg['line_pts_list'][0],
                                                                        new_seg['line_pts_list'][-1]]
                                                if np.linalg.norm(
                                                        np.array(new_seg['inner_pts'][0]) - new_seg['inner_pts'][
                                                            1]) < 1e-3:
                                                    continue
                                                if len(new_seg['mid_pts']) > 0:
                                                    if split_ind != 0:
                                                        mid_start = (line_pts_list_new[split_ind] - np.array(
                                                            wall['normal']) * s['depth'] / 2.).tolist()
                                                    else:
                                                        mid_start = new_seg['mid_pts'][0]
                                                    if split_ind_end != len(line_pts_list_new):
                                                        mid_end = (line_pts_list_new[split_ind_end] - np.array(
                                                            wall['normal']) * s['depth'] / 2.).tolist()
                                                    else:
                                                        mid_end = new_seg['mid_pts'][1]
                                                    new_seg['mid_pts'] = np.array([mid_start, mid_end]).tolist()

                                                if split_func_flag:
                                                    new_seg['Functional'] = edge_attr
                                                if sid not in split_seg:
                                                    split_seg[sid] = [new_seg]
                                                else:
                                                    split_seg[sid].append(new_seg)

                                    pass

                                name = 0
                                for sid, s in enumerate(segments):
                                    if sid not in split_seg:
                                        split_seg_list.append(s)
                                        new_seg_name[sid] = [name]
                                        name += 1
                                    else:
                                        split_seg_list += split_seg[sid]
                                        seg_name = []
                                        for _ in range(len(split_seg[sid])):
                                            seg_name.append(name)
                                            name += 1
                                        new_seg_name[sid] = seg_name
                                wall['segments'] = split_seg_list

                                # 修复门窗依赖关系
                                for door in room_info['Door']:
                                    if 'Wall' in door['related'] and 'Segment' in door['related']:
                                        if door['related']['Wall'] == wall_name and door['related'][
                                            'Segment'] in split_seg:
                                            for sid, seg in enumerate(split_seg[door['related']['Segment']]):
                                                seg_edge = [seg['line_pts_list'][0], seg['line_pts_list'][-1]]
                                                door_edge = door['layout_pts']
                                                flag = is_coincident_line(door_edge, seg_edge)
                                                if flag:
                                                    door['related']['Segment'] = \
                                                        new_seg_name[door['related']['Segment']][sid]
                                                    break
                                for win in room_info['Window']:
                                    if 'Wall' in win['related'] and 'Segment' in win['related']:
                                        if win['related']['Wall'] == wall_name and win['related'][
                                            'Segment'] in split_seg:
                                            for sid, seg in enumerate(split_seg[win['related']['Segment']]):
                                                seg_edge = [seg['line_pts_list'][0], seg['line_pts_list'][-1]]
                                                door_edge = win['layout_pts']
                                                flag = is_coincident_line(door_edge, seg_edge)
                                                if flag:
                                                    win['related']['Segment'] = new_seg_name[win['related']['Segment']][
                                                        sid]
                                                    break
        # plot_split_regions(room_info)
        # plt.show()

    @staticmethod
    def plot_split_regions(room_info, layout_info):
        floor_pts = room_info['floor_pts']
        room_type = room_info['type']
        # if room_type not in ['LivingDiningRoom', 'LivingRoom', 'DiningRoom']:
        #     return
        if len(floor_pts) == 0:
            return
        # plt_floor_pts = floor_pts + [floor_pts[0]]
        # plt.plot(np.array(plt_floor_pts)[:, 0], np.array(plt_floor_pts)[:, 1], color='black', linewidth=2)
        draw_params = {
            'dining': {
                'line_color': (1, 0, 1, 0.5),
                'line_style': '-',
                'line_width': 1,
                'fill': True,
                'face_color': None
            },
            'living': {
                'line_color': (0, 0, 1, 0.5),
                'line_style': '-',
                'line_width': 1,
                'fill': True,
                'face_color': None
            },
            'hallway': {
                'line_color': (0, 1, 1, 0.5),
                'line_style': '-',
                'line_width': 1,
                'fill': True,
                'face_color': None
            },
            'bed': {
                'line_color': (0, 0, 1, 0.5),
                'line_style': '-',
                'line_width': 1,
                'fill': True,
                'face_color': None
            },
            'extra': {
                'line_color': (0.2, 0.2, 0.2, 0.5),
                'line_style': '-',
                'line_width': 1,
                'fill': True,
                'face_color': None
            },
            'text': {
                'color': 'green',
                'size': 5
            }
        }
        for region in room_info['CustomizedCeiling']:
            rect = region['layout_pts']
            rect_type = region['type']
            if rect_type not in draw_params:
                continue
            plt_rect = rect.copy()
            # plt_rect.append(plt_rect[0])
            plt_rect = np.array(plt_rect)
            # plt.plot(plt_rect[:, 0], plt_rect[:, 1], color=draw_params[rect_type]['color'])
            draw_param = draw_params[rect_type]
            # 绝对坐标
            line_color, line_fill, line_style = draw_param['line_color'], draw_param['fill'], draw_param[
                'line_style']
            unit_poly = patches.Polygon(plt_rect, color=line_color, fill=line_fill)
            plt.gca().add_patch(unit_poly)
            plt.text(np.mean(plt_rect[:4, 0]), np.mean(plt_rect[:4, 1]), rect_type,
                     color=draw_params['text']['color'], size=draw_params['text']['size'])
        center = (np.max(floor_pts, axis=0) + np.min(floor_pts, axis=0)) * 0.5
        plt.text(center[0], center[1], room_info['id'], color='black', size=5)
        for wall in room_info['Wall']:
            for seg in wall['segments']:
                plt.plot(np.array(seg['inner_pts'])[:, 0], np.array(seg['inner_pts'])[:, 1], color='black', linewidth=1,
                         # marker='o'
                         )

        for win in room_info['Window']:
            plt.plot(np.array(win['layout_pts'])[:, 0], np.array(win['layout_pts'])[:, 1], color='blue', linewidth=3)

        for door in room_info['Door']:
            plt.plot(np.array(door['layout_pts'])[:, 0], np.array(door['layout_pts'])[:, 1], color='red', linewidth=3)

        for region in room_info['CustomizedCeiling']:
            if 'edge_attr' in region:
                edge_attr = region['edge_attr']
                layout_pts = region['layout_pts']
                for i in range(4):
                    if edge_attr[i] != '':
                        pos = np.mean([layout_pts[i], layout_pts[(i + 1) % 4]], axis=0)
                        plt.text(pos[0], pos[1], edge_attr[i], color='black', size=5)

        DRAW_GROUP_PARAM = {
            'Dining': {
                'line_color': (1, 0, 1, 0.2),
                'line_style': '-',
                'line_width': 1,
                'fill': True,
                'face_color': None
            },
            'Meeting': {
                'line_color': (0, 0, 1, 0.2),
                'line_style': '-',
                'line_width': 1,
                'fill': True,
                'face_color': None
            },
            'Media': {
                'line_color': (0, 1, 1, 0.2),
                'line_style': '-',
                'line_width': 1,
                'fill': True,
                'face_color': None
            },
            'Bed': {
                'line_color': (0, 0, 1, 0.2),
                'line_style': '-',
                'line_width': 1,
                'fill': True,
                'face_color': None
            }
        }
        for layout in layout_info:
            if layout['type'] in ['Bed', 'Meeting', 'Media', 'Dining']:
                object_one = {
                    'size': layout['size'],
                    'position': layout['position'],
                    'rotation': layout['rotation'],
                    'type': layout['type'],
                    'scale': [1, 1, 1.]
                }
                object_pos, object_rot = object_one['position'], object_one['rotation']
                object_size = [abs(object_one['size'][i] * object_one['scale'][i]) for i in range(3)]
                unit_array = compute_furniture_rect(object_size, object_pos, object_rot)
                draw_param = DRAW_GROUP_PARAM[layout['type']]
                # 绝对坐标
                line_color, line_fill, line_style = draw_param['line_color'], draw_param['fill'], draw_param[
                    'line_style']
                unit_poly = patches.Polygon(unit_array, color=line_color, fill=line_fill, linestyle=line_style)
                plt.gca().add_patch(unit_poly)
                center = np.mean(unit_array, axis=0)
                plt.text(center[0], center[1], layout['type'], size=5)

    @staticmethod
    def split_floor_into_rect(points, living_required_points, kitchen_required_points, hallway_required_points,
                              room_type):
        point_floor = copy.deepcopy(points)
        remained_edges = []
        org_edges = []
        grouped_edge_points = [copy.deepcopy(points)]
        for i in range(len(point_floor)):
            remained_edges.append([point_floor[i], point_floor[(i - 1) % len(point_floor)]])
            org_edges.append([point_floor[i], point_floor[(i - 1) % len(point_floor)]])
        # get all rects
        rects = RoomAreaSegmentation.split_all_rects(remained_edges)
        all_rects = copy.deepcopy(rects)
        # try get hallway rect
        grouped_edges, grouped_edge_points = RoomAreaSegmentation.separate_edge_group(remained_edges)
        if len(hallway_required_points) != 0 and room_type == 'LivingDiningRoom':
            hallway_rect = RoomAreaSegmentation.get_hallway_rect(rects, hallway_required_points)
            if hallway_rect is not None:
                remained_edges = RoomAreaSegmentation.get_remained_edges(remained_edges, list(hallway_rect))
                grouped_edges, grouped_edge_points = RoomAreaSegmentation.separate_edge_group(remained_edges)

                rects = []
                for grouped_edge in grouped_edges:
                    rects += RoomAreaSegmentation.split_all_rects(grouped_edge)
        else:
            hallway_rect = None

        # get living rects
        living_rect, status = RoomAreaSegmentation.get_main_rect(rects, living_required_points)
        if living_rect is not None and (status or is_hallway(room_type)):
            remained_edges = RoomAreaSegmentation.get_remained_edges(remained_edges, list(living_rect))
            grouped_edges, grouped_edge_points = RoomAreaSegmentation.separate_edge_group(remained_edges)
            rects = []
            for grouped_edge in grouped_edges:
                rects += RoomAreaSegmentation.split_all_rects(grouped_edge)
            if is_hallway(room_type):
                hallway_rect = living_rect
                living_rect = None
                dining_rect = None
                return living_rect, dining_rect, hallway_rect, grouped_edge_points
        else:
            living_rect = None
        # 由于切走道导致不存在客厅时，优先切客厅，再切走道
        if hallway_rect is not None and living_rect is None:
            living_rect, status = RoomAreaSegmentation.get_main_rect(all_rects, living_required_points)
            if living_rect is not None and (status or is_hallway(room_type)):
                remained_edges = RoomAreaSegmentation.get_remained_edges(org_edges, list(living_rect))
                grouped_edges, grouped_edge_points = RoomAreaSegmentation.separate_edge_group(remained_edges)
                rects = []
                for grouped_edge in grouped_edges:
                    rects += RoomAreaSegmentation.split_all_rects(grouped_edge)

                hallway_rect = RoomAreaSegmentation.get_hallway_rect(rects, hallway_required_points)
                if hallway_rect is not None:
                    remained_edges = RoomAreaSegmentation.get_remained_edges(remained_edges, list(hallway_rect))
                    grouped_edges, grouped_edge_points = RoomAreaSegmentation.separate_edge_group(remained_edges)

                    rects = []
                    for grouped_edge in grouped_edges:
                        rects += RoomAreaSegmentation.split_all_rects(grouped_edge)
            else:
                return None, None, None, [points]

        # get dining rects
        dining_rect = None
        if room_type == 'LivingDiningRoom':
            dining_rect, status = RoomAreaSegmentation.get_main_rect(rects, kitchen_required_points)
            if dining_rect is not None:
                size = np.max(dining_rect, axis=0) - np.min(dining_rect, axis=0)
                if min(size) / max(size) < 0.4:
                    dining_rect = None
            if dining_rect is not None and (status or is_hallway(room_type)):
                remained_edges = RoomAreaSegmentation.get_remained_edges(remained_edges, list(dining_rect))
                grouped_edges, grouped_edge_points = RoomAreaSegmentation.separate_edge_group(remained_edges)
            else:
                dining_rect = None

        # 当存在走道，不存在餐厅空间时，重新生成客餐厅
        if hallway_rect is not None and dining_rect is None and living_rect is not None and room_type == 'LivingDiningRoom':
            remained_edges_backup = RoomAreaSegmentation.get_remained_edges(org_edges, list(living_rect))
            grouped_edges_backup, grouped_edge_points_backup = RoomAreaSegmentation.separate_edge_group(
                remained_edges_backup)
            rects_backup = []
            for grouped_edge_backup in grouped_edges_backup:
                rects_backup += RoomAreaSegmentation.split_all_rects(grouped_edge_backup)
            dining_rect_backup, status = RoomAreaSegmentation.get_main_rect(rects_backup, kitchen_required_points)
            if dining_rect_backup is not None:
                size = np.max(dining_rect_backup, axis=0) - np.min(dining_rect_backup, axis=0)
                if min(size) / max(size) < 0.6:
                    dining_rect_backup = None
            if dining_rect_backup is not None and (status or is_hallway(room_type)):
                remained_edges_backup = RoomAreaSegmentation.get_remained_edges(remained_edges_backup,
                                                                                list(dining_rect_backup))
                grouped_edges, grouped_edge_points = RoomAreaSegmentation.separate_edge_group(remained_edges_backup)
                remained_edges = remained_edges_backup
                hallway_rect = None
                dining_rect = dining_rect_backup
            else:
                # 不再以hallway为主体，优先切割living再尝试切出hallway
                living_rect_backup, status = RoomAreaSegmentation.get_main_rect(all_rects, living_required_points)
                if living_rect_backup is not None and (status or is_hallway(room_type)):
                    living_rect = living_rect_backup
                    remained_edges = RoomAreaSegmentation.get_remained_edges(org_edges, list(living_rect))
                    grouped_edges, grouped_edge_points = RoomAreaSegmentation.separate_edge_group(remained_edges)
                    rects = []
                    for grouped_edge in grouped_edges:
                        rects += RoomAreaSegmentation.split_all_rects(grouped_edge)

                    hallway_rect = RoomAreaSegmentation.get_hallway_rect(rects, hallway_required_points)
                    if hallway_rect is not None:
                        remained_edges = RoomAreaSegmentation.get_remained_edges(remained_edges, list(hallway_rect))
                        grouped_edges, grouped_edge_points = RoomAreaSegmentation.separate_edge_group(remained_edges)

                        rects = []
                        for grouped_edge in grouped_edges:
                            rects += RoomAreaSegmentation.split_all_rects(grouped_edge)
        # 最终对比一下没有走道时，是否客餐厅面积都会变大
        if hallway_rect is not None and dining_rect is not None and living_rect is not None and room_type == 'LivingDiningRoom':
            living_rect_backup, status = RoomAreaSegmentation.get_main_rect(all_rects, living_required_points)
            if living_rect_backup is not None and (status or is_hallway(room_type)):
                remained_edges_backup = RoomAreaSegmentation.get_remained_edges(org_edges, list(living_rect_backup))
                grouped_edges_backup, grouped_edge_points_backup = RoomAreaSegmentation.separate_edge_group(
                    remained_edges_backup)
                rects_backup = []
                for grouped_edge_backup in grouped_edges_backup:
                    rects_backup += RoomAreaSegmentation.split_all_rects(grouped_edge_backup)
                dining_rect_backup, status = RoomAreaSegmentation.get_main_rect(rects_backup, kitchen_required_points)
                if dining_rect_backup is not None:
                    size = np.max(dining_rect_backup, axis=0) - np.min(dining_rect_backup, axis=0)
                    if min(size) / max(size) < 0.6:
                        dining_rect_backup = None
                if dining_rect_backup is not None and (status or is_hallway(room_type)):
                    remained_edges_backup = RoomAreaSegmentation.get_remained_edges(remained_edges_backup,
                                                                                    list(dining_rect_backup))
                    grouped_edges_backup, grouped_edge_points_backup = RoomAreaSegmentation.separate_edge_group(
                        remained_edges_backup)
                    living_new_l = np.linalg.norm(np.array(living_rect_backup[0]) - np.array(living_rect_backup[1]))
                    living_new_w = np.linalg.norm(np.array(living_rect_backup[1]) - np.array(living_rect_backup[2]))
                    living_area_new = living_new_l * living_new_w
                    dining_new_l = np.linalg.norm(np.array(dining_rect_backup[0]) - np.array(dining_rect_backup[1]))
                    dining_new_w = np.linalg.norm(np.array(dining_rect_backup[1]) - np.array(dining_rect_backup[2]))
                    dining_area_new = dining_new_l * dining_new_w

                    living_l = np.linalg.norm(np.array(living_rect[0]) - np.array(living_rect[1]))
                    living_w = np.linalg.norm(np.array(living_rect[1]) - np.array(living_rect[2]))
                    living_area = living_l * living_w
                    dining_l = np.linalg.norm(np.array(dining_rect[0]) - np.array(dining_rect[1]))
                    dining_w = np.linalg.norm(np.array(dining_rect[1]) - np.array(dining_rect[2]))
                    dining_area = dining_l * dining_w
                    if living_area_new > living_area + 0.1 and dining_area_new > dining_area + 0.1:
                        dining_rect = dining_rect_backup
                        living_rect = living_rect_backup
                        grouped_edge_points = grouped_edge_points_backup
                        grouped_edges = grouped_edges_backup
                        remained_edges = remained_edges_backup
                        hallway_rect = None

        # 将剩余区域切分为多个矩形
        flag = True
        remained_edges_tmp = remained_edges.copy()
        remained_edges = []
        for edge in remained_edges_tmp:
            if np.linalg.norm(np.array(edge[0]) - edge[1]) > 5e-4:
                remained_edges.append(edge)
        for i in range(len(remained_edges)):
            cur = remained_edges[i]
            if abs(cur[0][0] - cur[1][0]) > 1e-3 and abs(cur[0][1] - cur[1][1]) > 1e-3:
                flag = False
                break
        if flag:
            remained_rects = []
            max_iter = 10
            while max_iter > 0:
                max_iter -= 1
                remained_edges_tmp = remained_edges.copy()
                remained_edges = []
                for edge in remained_edges_tmp:
                    if np.linalg.norm(np.array(edge[0]) - edge[1]) > 5e-4:
                        remained_edges.append(edge)
                if len(remained_edges) < 4:
                    break
                grouped_edges, grouped_edge_points = RoomAreaSegmentation.separate_edge_group(remained_edges)
                if len(grouped_edge_points) == 1 and len(grouped_edge_points[0]) == 4:
                    remained_rects.append(grouped_edge_points[0].copy())
                    break
                rects = []

                remained_edges_tmp = []
                for i, grouped_edge in enumerate(grouped_edges):
                    if len(grouped_edge) < 4:
                        continue
                    if len(grouped_edge) == 4:
                        remained_rects.append(grouped_edge_points[i])
                        continue
                    remained_edges_tmp += grouped_edge
                    rects += RoomAreaSegmentation.split_all_rects(grouped_edge)
                rects = [i for i in rects if i[1] > 1e-8]
                if len(rects) == 0:
                    break
                rects.sort(key=lambda x: -x[1])
                remained_rects.append(rects[0][0].copy())
                remained_edges = RoomAreaSegmentation.get_remained_edges(remained_edges_tmp, list(rects[0][0]))
            remained_rects = np.array(remained_rects).tolist()
            if len(remained_edges) > 0:
                grouped_edges, grouped_edge_points = RoomAreaSegmentation.separate_edge_group(remained_edges)
                remained_rects += np.array(grouped_edge_points).tolist()
        else:
            grouped_edges, grouped_edge_points = RoomAreaSegmentation.separate_edge_group(remained_edges)
            remained_rects = np.array(grouped_edge_points).tolist()
        return living_rect, dining_rect, hallway_rect, remained_rects

    @staticmethod
    def get_rects_one_direct(edges, perpendicular_edge, flag='vertical'):
        assert flag in ['vertical', 'horizontal']
        rects = []
        for i in range(len(edges)):
            edge = edges[i]
            cur = edge[0]
            last = edge[1]
            ind = 0 if flag == 'vertical' else 1
            start_x = cur[ind]
            min_len = 1e7
            min_edge = None

            start_y = min(cur[1 - ind], last[1 - ind])
            end_y = max(cur[1 - ind], last[1 - ind])
            length = end_y - start_y
            for j in range(len(edges)):
                if i == j:
                    continue
                candidate = edges[j]
                start_y_candidate = min(candidate[0][1 - ind], candidate[1][1 - ind])
                end_y_candidate = max(candidate[0][1 - ind], candidate[1][1 - ind])
                inter_min = max(start_y_candidate, start_y)
                inter_max = min(end_y_candidate, end_y)
                if (inter_max - inter_min) > 1e-3 and abs(candidate[0][ind] - start_x) < min_len:
                    # center_point = [(candidate[0][ind] + start_x) / 2., (start_y + end_y) / 2.]
                    # if flag == 'horizontal':
                    #     center_point = [center_point[1], center_point[0]]
                    min_len = abs(candidate[0][ind] - start_x)
                    min_edge = candidate
            if min_edge is not None:
                # check if rect edge could be expanded
                if min_edge[0][ind] > start_x:
                    lower_edge = [[start_x, start_y], [start_x + min_len, start_y]]
                    upper_edge = [[start_x, end_y], [start_x + min_len, end_y]]
                else:
                    lower_edge = [[start_x - min_len, start_y], [start_x, start_y]]
                    upper_edge = [[start_x - min_len, end_y], [start_x, end_y]]
                if flag == 'horizontal':
                    lower_edge = np.array(lower_edge)[:, ::-1].tolist()
                    upper_edge = np.array(upper_edge)[:, ::-1].tolist()

                lower_expand_len = 1e7
                upper_expand_len = 1e7
                for j in range(len(perpendicular_edge)):

                    candidate = perpendicular_edge[j]

                    if candidate[0][1 - ind] <= lower_edge[0][1 - ind]:
                        start_y_candidate = min(candidate[0][ind], candidate[1][ind])
                        end_y_candidate = max(candidate[0][ind], candidate[1][ind])
                        inter_min = max(start_y_candidate, lower_edge[0][ind])
                        inter_max = min(end_y_candidate, lower_edge[1][ind])
                        if inter_max > inter_min and lower_edge[0][1 - ind] - candidate[0][1 - ind] < lower_expand_len:
                            lower_expand_len = lower_edge[0][1 - ind] - candidate[0][1 - ind]

                    if candidate[0][1 - ind] >= upper_edge[0][1 - ind]:
                        start_y_candidate = min(candidate[0][ind], candidate[1][ind])
                        end_y_candidate = max(candidate[0][ind], candidate[1][ind])
                        inter_min = max(start_y_candidate, upper_edge[0][ind])
                        inter_max = min(end_y_candidate, upper_edge[1][ind])
                        if inter_max > inter_min and -upper_edge[0][1 - ind] + candidate[0][1 - ind] < upper_expand_len:
                            upper_expand_len = -upper_edge[0][1 - ind] + candidate[0][1 - ind]

                if lower_expand_len != 1e7:
                    start_y -= lower_expand_len
                    length += lower_expand_len
                if upper_expand_len != 1e7:
                    end_y += upper_expand_len
                    length += upper_expand_len
                area = length * min_len

                if min_edge[0][ind] > start_x:
                    cur_rect = np.array([[start_x, start_y], [start_x + min_len, start_y], [start_x + min_len, end_y],
                                         [start_x, end_y]])
                else:
                    cur_rect = np.array([[start_x - min_len, start_y], [start_x, start_y], [start_x, end_y],
                                         [start_x - min_len, end_y]])
                if flag == 'horizontal':
                    cur_rect = np.array(cur_rect)[:, ::-1]
                rects.append([cur_rect, area, min(min_len, length), max(min_len, length)])

        return rects

    @staticmethod
    def split_all_rects(edges):
        horizon_edges = []
        vertical_edges = []
        for i in range(len(edges)):
            cur = edges[i][0]
            last = edges[i][1]
            if abs(cur[0] - last[0]) < 1e-3:
                vertical_edges.append([cur, last])

            else:
                horizon_edges.append([cur, last])

        # rect start with a vertical edge
        rects_vertical = RoomAreaSegmentation.get_rects_one_direct(vertical_edges, horizon_edges, flag='vertical')
        # rect start with a horizontal edge
        rects_horizontal = RoomAreaSegmentation.get_rects_one_direct(horizon_edges, vertical_edges, flag='horizontal')
        rects = rects_vertical + rects_horizontal
        for rect in rects:
            rect[0] = np.round(rect[0], 3)
        return rects

    @staticmethod
    def get_main_rect(rects, required_points):
        if len(rects) == 0:  # or len(required_points) == 0:
            return None, False
        all_rects = rects.copy()
        all_rects.sort(key=lambda x: -x[1])
        valid_rect = []
        max_area = all_rects[0][1]
        for i, rect in enumerate(all_rects):

            if rect[2] < 1.5 or rect[3] < 2.:
                continue
            area_grades = rect[1] / max_area

            ratio = rect[2] / rect[3]
            if ratio > 1:
                ratio = 1. / ratio
            ratio_grade = 2 * ratio - 1.

            contained_pt_num = 0
            for pt in required_points:
                contained_pt_num += (np.min(rect[0][:, 0]) <= pt[0] <= np.max(rect[0][:, 0]) and
                                     np.min(rect[0][:, 1]) <= pt[1] <= np.max(rect[0][:, 1]))
            required_pts_grades = (1e-3 + contained_pt_num) / (1e-3 + len(required_points))
            if required_pts_grades <= 0.5:
                continue
            grade = 0.8 * area_grades + required_pts_grades + 0.5 * ratio_grade
            valid_rect.append(all_rects[i] + [grade])
        if len(valid_rect) == 0:
            return all_rects[0][0].tolist(), False
        valid_rect.sort(key=lambda x: -x[-1])
        max_rect = valid_rect[0][0]
        return max_rect.tolist(), True

    @staticmethod
    def get_hallway_rect(rects, required_points):
        hallway_rect = None
        max_contained_pt_num = 0
        max_area = 0
        for i, rect in enumerate(rects):
            if rect[2] > 1.5 or rect[2] < 0.3:
                continue

            ratio = rect[2] / rect[3]
            if ratio > 1:
                ratio = 1. / ratio
            if ratio > 0.66667:
                continue

            contained_pt_num = 0
            for pt in required_points:
                contained_pt_num += int(np.min(rect[0][:, 0]) <= pt[0] <= np.max(rect[0][:, 0]) and
                                     np.min(rect[0][:, 1]) <= pt[1] <= np.max(rect[0][:, 1]))
            if contained_pt_num < 4 and (contained_pt_num < len(required_points) - 2 or (contained_pt_num + 1e-3) / (
                    len(required_points) + 1e-3) < 0.5):
                continue
            if contained_pt_num > max_contained_pt_num:
                max_contained_pt_num = contained_pt_num
                hallway_rect = rect[0].tolist()
                max_area = rect[1]
            elif contained_pt_num == max_contained_pt_num:
                if rect[1] > max_area:
                    max_area = rect[1]
                    hallway_rect = rect[0].tolist()
        return hallway_rect

    def refine_points(self, org_points, room_info, layouts, concession=True):
        points = copy.deepcopy(org_points)
        # point_floor = []
        wall_dict = {}
        for i in range(len(points)):
            wall_dict[i] = i
        for i in range(len(points)):
            points[i] = [round(points[i][0], 3), round(points[i][1], 3)]

        # 拉直
        for i in range(len(points)):
            cur = points[i % len(points)]
            nxt = points[(i + 1) % len(points)]

            if abs(cur[0] - nxt[0]) > 1e-4 and abs(cur[1] - nxt[1]) > 1e-4:
                if abs(cur[0] - nxt[0]) > abs(cur[1] - nxt[1]):
                    nxt[1] = cur[1]
                else:
                    nxt[0] = cur[0]
        # 去除短墙
        minimal_wall_len = 0.1
        i = 0
        while True:
            if i >= len(points):
                break
            cur = points[i]
            last = points[(i - 1) % len(points)]
            ind = 1 if abs(cur[0] - last[0]) < abs(cur[1] - last[1]) else 0

            length = abs(cur[ind] - last[ind])
            if length < minimal_wall_len:
                points[i] = last  # 保留一个与前一点相同的点，保证总的墙数是不变的，后续优化窗帘避让时，墙的信息还能从house_info中读取
            i += 1
        if concession:
            points, cabinet_extra_area = self.refine_floor_pts_for_layout(points, room_info, layouts)
        else:
            cabinet_extra_area = []
        # 拉直
        for i in range(len(points)):
            cur = points[i % len(points)]
            nxt = points[(i + 1) % len(points)]

            if abs(cur[0] - nxt[0]) > 1e-4 and abs(cur[1] - nxt[1]) > 1e-4:
                if abs(cur[0] - nxt[0]) > abs(cur[1] - nxt[1]):
                    nxt[1] = cur[1]
                else:
                    nxt[0] = cur[0]
        # 去除共线
        i = 0
        while True:
            if i >= len(points):
                break
            cur = points[i]
            last = points[(i - 1) % len(points)]
            next = points[(i + 1) % len(points)]
            if (abs(cur[0] - last[0]) < 1e-4 and abs(cur[0] - next[0]) < 1e-4) or \
                    (abs(cur[1] - last[1]) < 1e-4 and abs(cur[1] - next[1]) < 1e-4):
                points.pop(i)
            else:
                i += 1
        # plt.figure()
        # plt.plot(np.array(org_points)[:, 0], np.array(org_points)[:, 1], color='black', linewidth='3')
        # plt.plot(np.array(points)[:, 0], np.array(points)[:, 1], color='red')
        # plt.show()
        return points, cabinet_extra_area

    @staticmethod
    def separate_edge_group(edges):
        ALPHA = 2e-3
        grouped_edges = []
        grouped_edge_points = []
        edge_flag = [True for _ in range(len(edges))]
        for i in range(len(edges)):
            if edge_flag[i]:
                start = edges[i][1]

                group = [edges[i]]
                group_points = [start]
                edge_flag[i] = False
                while True:
                    find_valid = False
                    ALPHA = 5e-5
                    for j in range(len(edges)):
                        if edge_flag[j]:
                            next = edges[j]
                            if abs(next[0][0] - start[0]) < ALPHA and abs(next[0][1] - start[1]) < ALPHA:
                                start = next[1]
                                edge_flag[j] = False
                                group.append(next)
                                group_points.append(start)
                                find_valid = True
                                break
                            elif abs(next[1][0] - start[0]) < ALPHA and abs(next[1][1] - start[1]) < ALPHA:
                                start = next[0]
                                edge_flag[j] = False
                                group.append(next)
                                group_points.append(start)
                                find_valid = True
                                break
                    if not find_valid:
                        ALPHA = 2e-3
                        for j in range(len(edges)):
                            if edge_flag[j]:
                                next = edges[j]

                                if abs(next[0][0] - start[0]) < ALPHA and abs(next[0][1] - start[1]) < ALPHA:
                                    start = next[1]
                                    edge_flag[j] = False
                                    group.append(next)
                                    group_points.append(start)
                                    find_valid = True
                                    break
                                elif abs(next[1][0] - start[0]) < ALPHA and abs(next[1][1] - start[1]) < ALPHA:
                                    start = next[0]
                                    edge_flag[j] = False
                                    group.append(next)
                                    group_points.append(start)
                                    find_valid = True
                                    break

                    if not find_valid:
                        break
                grouped_edges.append(group.copy())
                grouped_edge_points.append(group_points.copy())
        return grouped_edges, grouped_edge_points

    @staticmethod
    def get_remained_edges(edges, rect):
        remained_edges = []
        # remove edges that are coincided with rect edge
        # add edges that are not coincided by existing edge on rect edge
        edge_status = [0 for _ in edges]
        for i in range(4):
            rect_edges = [rect[i], rect[(i + 1) % 4]]
            rect_min_y = min(rect_edges[0][1], rect_edges[1][1])
            rect_max_y = max(rect_edges[0][1], rect_edges[1][1])

            rect_min_x = min(rect_edges[0][0], rect_edges[1][0])
            rect_max_x = max(rect_edges[0][0], rect_edges[1][0])
            coincided_edges = []
            for j in range(len(edges)):
                edge = edges[j]
                if abs(rect_edges[0][0] - rect_edges[1][0]) < 1e-4 and abs(edge[0][0] - edge[1][0]) < 1e-4 and abs(
                        edge[0][0] - rect_edges[0][0]) < 1e-4:
                    edge_min_y = min(edge[0][1], edge[1][1])
                    edge_max_y = max(edge[0][1], edge[1][1])
                    interaction = min(edge_max_y, rect_max_y) - max(edge_min_y, rect_min_y)
                    if interaction > 0:
                        coincided_edges.append([edge, edge_min_y, edge_max_y])
                        edge_status[j] += 1

                if abs(rect_edges[0][1] - rect_edges[1][1]) < 1e-4 and abs(edge[0][1] - edge[1][1]) < 1e-4 and abs(
                        edge[0][1] - rect_edges[0][1]) < 1e-4:
                    edge_min_x = min(edge[0][0], edge[1][0])
                    edge_max_x = max(edge[0][0], edge[1][0])
                    interaction = min(edge_max_x, rect_max_x) - max(edge_min_x, rect_min_x)
                    if interaction > 0:
                        coincided_edges.append([edge, edge_min_x, edge_max_x])
                        edge_status[j] += 1

            coincided_edges.sort(key=lambda x: x[1])
            for coincided_edge, edge_min, edge_max in coincided_edges:
                if abs(rect_edges[0][1] - rect_edges[1][1]) < 1e-4:
                    if abs(rect_min_x - edge_min) > 1e-4:
                        remained_edges.append([[min(rect_min_x, edge_min), rect_min_y],
                                               [max(rect_min_x, edge_min), rect_min_y]])  # rect_min_y == rect_max_y
                    rect_min_x = edge_max
                else:
                    if abs(rect_min_y - edge_min) > 1e-4:
                        remained_edges.append([[rect_min_x, min(rect_min_y, edge_min)],
                                               [rect_min_x, max(rect_min_y, edge_min)]])  # rect_min_y == rect_max_y
                    rect_min_y = edge_max
            if abs(rect_edges[0][1] - rect_edges[1][1]) < 1e-4 and abs(rect_min_x - rect_max_x) > 1e-4:
                remained_edges.append(
                    [[min(rect_min_x, rect_max_x), rect_min_y], [max(rect_min_x, rect_max_x), rect_min_y]])
            if abs(rect_edges[0][0] - rect_edges[1][0]) < 1e-4 and abs(rect_min_y - rect_max_y) > 1e-4:
                remained_edges.append(
                    [[rect_min_x, min(rect_min_y, rect_max_y)], [rect_min_x, max(rect_min_y, rect_max_y)]])

        for j in range(len(edges)):
            edge = edges[j]
            if edge_status[j] != 1:
                remained_edges.append(edge)
        for i, edge in enumerate(remained_edges):
            remained_edges[i] = np.round(edge, 3).tolist()
        return remained_edges
