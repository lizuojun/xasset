# -*- coding: utf-8 -*-

"""
@Author: lizuojun
@Date: 2019-05-20
@Description: 获取家具特征，取OBJ模型多视图HOG特征融合，PSLF聚类迭代提取

"""

import cv2
from Furniture.furniture import *
from Furniture.glm_render import *


def project_hog(obj_list, des_dir, obj_dir='', view_num=12, seed_num=30):
    # 目录
    if not os.path.exists(des_dir):
        os.makedirs(des_dir)
    # 线框
    line_dir = os.path.join(des_dir, 'line')
    # 撒点
    seed_dir = os.path.join(des_dir, 'seed')
    # 区域
    patch_dir = os.path.join(des_dir, 'patch')
    if not os.path.exists(line_dir):
        os.makedirs(line_dir)
    if not os.path.exists(seed_dir):
        os.makedirs(seed_dir)
    if not os.path.exists(patch_dir):
        os.makedirs(patch_dir)
    for view_idx in range(view_num):
        patch_dir_sub = os.path.join(des_dir, 'patch/%d' % (view_idx + 1))
        if not os.path.exists(patch_dir_sub):
            os.makedirs(patch_dir_sub)

    # 特征记录
    hog_set_list = []
    for view_idx in range(view_num):
        hog_set_list.append([])

    # 尺寸
    image_width = 240
    image_height = 240
    viewport_size = (image_width, image_height)
    patch_width = 48
    patch_height = 48
    patch_size = (patch_width, patch_height)

    # 遍历
    success_count = 0
    failure_count = 0
    for obj_id in obj_list:
        # 本地目录
        if obj_dir == '':
            obj_dir = DATA_DIR_FURNITURE
            if not os.path.exists(obj_dir):
                obj_dir = os.path.dirname(__file__) + '/temp/'
        # 下载模型
        obj_path = os.path.join(obj_dir, obj_id + '.obj')
        download_furniture(obj_id, obj_dir, '.obj')
        if not os.path.exists(obj_path):
            continue
        # 模型撒点
        seed_path = os.path.join(seed_dir, obj_id + '.off')
        seed_exist = False
        if os.path.exists(seed_path):
            seed_exist = True

        # 解析数据
        try:
            # 读取模型
            obj = glm_read_obj(obj_path)
            # 规范模型
            if obj:
                glm_normal_vertex([obj])
            else:
                failure_count += 1
                continue
            # 模型撒点
            if seed_exist:
                glm_read_seeds(obj, seed_path)
            else:
                glm_set_seeds(obj, seed_num)

            # 图像生成
            glm_render_initial(size=viewport_size)
            image_path = os.path.join(line_dir, obj_id + '_1.jpg')
            if not os.path.exists(image_path):
                glm_render_reshape()
                glm_render_project([obj], line_dir, view_num)
            if not os.path.exists(image_path):
                continue
            image_list = []
            for view_idx in range(view_num):
                image_path = os.path.join(line_dir, obj_id + '_%d.jpg' % (view_idx + 1))
                image_view = cv2.imread(image_path)
                image_list.append(image_view)

            # 特征计算
            for seed_idx in range(seed_num):
                print('hog obj seed %d' % (seed_idx + 1))
                patch_key = obj_id + '_%d' % (seed_idx + 1)
                # 图像生成
                glm_render_reshape()
                glm_render_project([obj], line_dir, view_num, seed_dot=True)
                # 特征计算
                for view_idx in range(view_num):
                    # 图像存在
                    image_path_seed = os.path.join(line_dir, obj_id + '_%d_seed.jpg' % (view_idx + 1))
                    if not os.path.exists(image_path_seed):
                        continue
                    # 定位撒点
                    image_seed = cv2.imread(image_path_seed)
                    r1, c1, r2, c2 = image_height, image_width, 0, 0
                    for row in range(image_height):
                        for col in range(image_width):
                            (b, g, r) = image_seed[row, col]
                            # seed
                            if b > 100 and g == 0 and r == 0:
                                if row < r1:
                                    r1 = row
                                if row > r2:
                                    r2 = row
                                if col < c1:
                                    c1 = col
                                if col > c2:
                                    c2 = col
                    if r2 == 0 or c2 == 0:
                        continue

                    # 截取图像
                    image_view = image_list[view_idx]
                    if r1 + patch_height <= image_height:
                        r2 = r1 + patch_height - 1
                        if c1 + patch_width <= image_width:
                            c2 = c1 + patch_width - 1
                            image_patch = image_view[r1:r2, c1:c2]
                        elif c2 - patch_width + 1 >= 0:
                            c1 = c2 - patch_width + 1
                            image_patch = image_view[r1:r2, c1:c2]
                    elif r2 - patch_height + 1 >= 0:
                        r1 = r2 - patch_height + 1
                        if c1 + patch_width <= image_width:
                            c2 = c1 + patch_width - 1
                            image_patch = image_view[r1:r2, c1:c2]
                        elif c2 - patch_width + 1 >= 0:
                            c1 = c2 - patch_width + 1
                            image_patch = image_view[r1:r2, c1:c2]
                    else:
                        continue
                    # 计算特征
                    hog_descriptor = cv2.HOGDescriptor(patch_size, (16, 16), (8, 8), (8, 8), 9)
                    hog_matrix = hog_descriptor.compute(image_patch)
                    # 融合特征
                    hog_set_list[view_idx].append(hog_matrix[:, 0])

                    # 保存目录
                    patch_dir_sub = os.path.join(des_dir, 'patch/%d' % (view_idx + 1))
                    # 保存图像
                    # patch_file = obj_id + '_%d.jpg' % (seed_idx + 1)
                    # patch_path = os.path.join(patch_dir_sub, patch_file)
                    # cv2.imwrite(patch_path, image_patch)
                    # 保存特征
                    # patch_file = obj_id + "_%d.txt" % (seed_idx + 1)
                    # patch_path = os.path.join(patch_dir_sub, patch_file)
                    # w = open(patch_path, 'w')
                    # for j in hog_matrix[:, 0]:
                    #     w.write(str(j) + '\n')
                    # w.close()

                # 其他撒点
                obj.seed_now += 1

            # 保存撒点
            if not seed_exist:
                glm_write_seeds(obj, seed_path)

            success_count += 1
            print('hog obj %s %d success' % (obj_id, success_count))
            if success_count % 2 == 0:
                break
        except Exception as e:
            failure_count += 1
            print('hog obj %s %d failure:' % (obj_id, success_count))
            print(e)
            continue

    # 特征融合
    hog_map_list = []
    for view_idx in range(view_num):
        hog_map_one = np.array(hog_set_list[view_idx])
        hog_map_list.append(hog_map_one)

    print('hog obj success', success_count)
    print('hog obj failure', failure_count)
    return hog_map_list


def run_cluster(hog_map_list, n_clusters=50):
    print()


def run_cluster_idf():
    print()


def pre_cnn():
    print()


if __name__ == '__main__':
    # obj_list = list_furniture_oss(DATA_OSS_FURNITURE)
    obj_list = ['299257d6-43ac-479e-86ab-f51a93cc1b31', '695c49ae-db22-4cae-b55f-3e88ef7c2209']
    des_dir = os.path.dirname(__file__) + '/pslf/'
    project_hog(obj_list, des_dir)
