# -*- coding: utf-8 -*-

"""
@Author:
@Date: 2018-11-02
@Description:

"""

import os
import math
import numpy as np
from Furniture.glm_model import *


def glm_read_obj(file_path):
    try:
        f = open(file_path, 'r', encoding='gbk')
    except Exception as e:
        print('read obj %s failure:' % os.path.basename(file_path), e)
        return 0
    model = GLMModel()
    model.obj_path = file_path
    model.vertices.append([0, 0, 0])  # vertices
    model.normals.append([0, 0, 0])  # normals
    model.coords.append([0, 0])  # texture coordinates
    group = glm_add_group(model, 'default')  # default group
    material = 0  # default material
    try:
        lines = f.readlines()
        count = 0
        group_name = ''
        for line in lines:
            count += 1
            content = line.split(' ', 1)
            if line[0] == '#':  # comment
                continue
            elif content[0] == 'v':  # vertex
                if len(content) > 1:
                    value_str = content[1].strip().split(' ')
                    value_float = list(map(float, value_str))
                    model.vertices.append(value_float)
                continue
            elif content[0] == 'vn':  # normal
                if len(content) > 1:
                    value_str = content[1].strip().split(' ')
                    value_float = list(map(float, value_str))
                    model.normals.append(value_float)
                continue
            elif content[0] == 'vt':  # texture coordinates
                if len(content) > 1:
                    value_str = content[1].strip().split(' ')
                    value_float = list(map(float, value_str))
                    value_float = value_float[0:2]
                    model.coords.append(value_float)
                continue
            elif content[0] == 'mtllib':  # m
                if len(content) > 1:
                    mtlib_name = content[1].strip()
                    model.mtl_path = mtlib_name
                    glm_read_mtl(model, file_path, mtlib_name)
                continue
            elif content[0] == 'g':  # group
                if len(content) > 1:
                    group_name = (content[1]).strip()
                    group = glm_add_group(model, group_name)
                    group.material = material
                continue
            elif content[0] in ('usemtl', 'usemat'):
                if len(content) > 1:
                    material_name = content[1].strip()
                    material = glm_get_mtl(model, material_name)
                    group.material = material
                continue
            elif content[0] == 'f':  # face
                if len(content) > 1:
                    triangle = GLMTriangle()
                    value_str = content[1].strip().split(' ')
                    # v//n
                    if '//' in value_str[0]:
                        for value_one in value_str:
                            w = value_one.split('//')
                            # v
                            v = int(w[0])
                            if v < 0:
                                v += len(model.vertices)
                            triangle.v_indices.append(v)
                            # n
                            if len(w) >= 2 and len(w[1]) > 0:
                                n = int(w[1])
                                if n < 0:
                                    n += len(model.normals)
                                triangle.n_indices.append(n)
                            else:
                                triangle.n_indices.append(0)
                    # v/t or v/t/n
                    elif '/' in value_str[0]:
                        for value_one in value_str:
                            w = value_one.split('/')
                            # v
                            v = int(w[0])
                            if v < 0:
                                v += len(model.vertices)
                            triangle.v_indices.append(v)
                            # t
                            if len(w) >= 2 and len(w[1]) > 0:
                                t = int(w[1])
                                if t < 0:
                                    t += len(model.coords)
                                triangle.t_indices.append(t)
                            else:
                                triangle.t_indices.append(0)
                            # n
                            if len(w) >= 3 and len(w[2]) > 0:
                                n = int(w[2])
                                if n < 0:
                                    n += len(model.normals)
                                triangle.n_indices.append(n)
                            else:
                                triangle.n_indices.append(0)
                    # v
                    else:
                        for value_one in value_str:
                            w = value_one
                            # v
                            v = int(w)
                            if v < 0:
                                v += len(model.vertices)
                            triangle.v_indices.append(v)
                    if len(triangle.v_indices) > 0:
                        model.faces.append(triangle)
                        group.faces.append(len(model.faces) - 1)
                        if group_name == 'shadow' or 'shadow' in group_name or 'Shadow' in group_name:
                            model.shadow_triangles.append(triangle)
                            for index in triangle.v_indices:
                                model.shadow_indices.append(index)
                continue
            else:
                continue
        glm_calc_box(model)
        glm_calc_face(model)
        glm_calc_vertex(model, 90)
    except Exception as e:
        print('read obj %s failure:' % os.path.basename(file_path), e)
        model = 0
        if f:
            f.close()
        return model
    if f:
        f.close()
    return model


def glm_write_obj(model, file_name, mode, mtlib='', usemtl=''):
    if not model:
        return 0
    if mode & glm_flat and len(model.faces_normals) < 2:
        print('flat normal output request with no facet normals defined.')
        mode &= ~glm_flat
    if mode & glm_smooth and len(model.normals) < 2:
        print('smooth normal output request with no normals defined.')
        mode &= ~glm_smooth
    if mode & glm_texture and len(model.coords) < 2:
        print('texture coordinate output request with no texture coordinates defined.')
        mode &= ~glm_texture
    if mode & glm_flat and mode & glm_smooth:
        print('flat normal and smooth normal output request with using smooth.')
        mode &= ~glm_flat
    if mode & glm_color and len(model.material) < 2:
        print('color output request with no materials defined.')
        mode &= ~glm_color
    if mode & glm_material and len(model.material) < 2:
        print('material output request with no materials defined.')
        mode &= ~glm_material
    if mode & glm_color and mode & glm_material:
        print('color and material output request with using materials.')
        mode &= ~glm_color
    try:
        f = open(file_name, 'w')
    except Exception as e:
        print('write_obj error', file_name)
        print(e)
        return 0
    result = 1
    try:
        f.write('#  \n')
        f.write('#  Wavefront OBJ generated by GLM library\n')
        f.write('#  \n')
        f.write('#  GLM library\n')
        f.write('#  Ben Lee\n')
        f.write('#  zuojun.lzj@alibaba-inc.com\n')
        f.write('#  lizuojun@gmail.com\n')
        f.write('#  \n')
        # spit out mtl
        if mtlib == '' and mode & glm_material:
            buf = '\nmtllib ' + model.mtl_path + '\n\n'
            f.write(buf)
            glm_write_mtl(model, file_name, model.mtl_path)
        else:
            buf = '\nmtllib ' + mtlib + '\n\n'
            f.write(buf)
            # glm_write_mtl(model, file_name, model.mtlib_name)
        # spit out vertices
        f.write('\n')
        buf = '# %d vertices\n' % (len(model.vertices) - 1)
        f.write(buf)
        for value in model.vertices[1:]:
            buf = 'v %.6f %.6f %.6f\n' % (value[0], value[1], value[2])
            f.write(buf)
        # spit out smooth/flat normals
        if mode & glm_smooth:
            f.write('\n')
            buf = '# %d normals\n' % (len(model.normals) - 1)
            f.write(buf)
            for value in model.normals[1:]:
                buf = 'vn %.6f %.6f %.6f\n' % (value[0], value[1], value[2])
                f.write(buf)
        elif mode & glm_flat:
            f.write('\n')
            buf = '# %d normals\n' % (len(model.faces_normals) - 1)
            f.write(buf)
            for value in model.faces_normals[1:]:
                buf = 'vn %.6f %.6f %.6f\n' % (value[0], value[1], value[2])
                f.write(buf)
        # spit out texture coordinates
        if mode & glm_texture:
            f.write('\n')
            buf = '# %d texcoords\n' % (len(model.coords) - 1)
            f.write(buf)
            for value in model.coords[1:]:
                buf = 'vt %.6f %.6f\n' % (value[0], value[1])
                f.write(buf)
        # spit out groups
        f.write('\n')
        buf = '# %d groups\n' % (len(model.groups))
        f.write(buf)
        buf = '# %d faces (triangles)\n' % (len(model.faces))
        f.write(buf)
        f.write('\n')
        for group in model.groups[::-1]:
            buf = 'g ' + group.name + '\n'
            f.write(buf)
            if usemtl == '':
                if not 0 > group.material and len(model.materials) > group.material:
                    buf = 'usemtl ' + model.materials[group.material].name + '\n'
                    f.write(buf)
                else:
                    pass
            else:
                buf = 'usemtl ' + usemtl + '\n'
                f.write(buf)
            for index in group.faces:
                triangle = model.faces[index]
                if mode & glm_smooth and mode & glm_texture:
                    buf = 'f '
                    for i in range(len(triangle.v_indices)):
                        v = triangle.v_indices[i]
                        if i < len(triangle.t_indices):
                            t = triangle.t_indices[i]
                        else:
                            t = 0
                        if i < len(triangle.n_indices):
                            n = triangle.n_indices[i]
                        else:
                            n = 0
                        buf += '%d/%d/%d' % (v, t, n)
                        buf += ' '
                    buf += '\n'
                    f.write(buf)
                elif mode & glm_flat and mode & glm_texture:
                    buf = 'f '
                    for i in range(len(triangle.v_indices)):
                        v = triangle.v_indices[i]
                        f = triangle.f_index
                        buf += '%d/%d' % (v, f)
                        buf += ' '
                    buf += '\n'
                    f.write(buf)
                elif mode & glm_texture:
                    buf = 'f '
                    for i in range(len(triangle.v_indices)):
                        v = triangle.v_indices[i]
                        if i < len(triangle.t_indices):
                            t = triangle.t_indices[i]
                        else:
                            t = 0
                        buf += '%d/%d' % (v, t)
                        buf += ' '
                    buf += '\n'
                    f.write(buf)
                elif mode & glm_smooth:
                    buf = 'f '
                    for i in range(len(triangle.v_indices)):
                        v = triangle.v_indices[i]
                        if i < len(triangle.t_indices):
                            t = triangle.t_indices[i]
                        else:
                            t = 0
                        buf += '%d//%d' % (v, t)
                        buf += ' '
                    buf += '\n'
                    f.write(buf)
                elif mode & glm_flat:
                    buf = 'f '
                    for i in range(len(triangle.v_indices)):
                        v = triangle.v_indices[i]
                        f = triangle.f_index
                        buf += '%d//%d' % (v, f)
                        buf += ' '
                    buf += '\n'
                    f.write(buf)
                else:
                    buf = 'f '
                    for i in range(len(triangle.v_indices)):
                        v = triangle.v_indices[i]
                        buf += '%d' % v
                        buf += ' '
                    buf += '\n'
                    f.write(buf)
            f.write('\n')
    except Exception as e:
        print('write_obj', file_name, 'error.')
        print(e)
        result = 0
    if f:
        f.close()
    return result


def glm_add_group(model, group_name):
    group_exist = False
    if len(model.groups) > 0:
        for group in model.groups:
            if group.name == group_name:
                return group
    if not group_exist:
        group = GLMGroup()
        group.name = group_name
        model.groups.append(group)
        return group


def glm_read_mtl(model, model_path, mtlib_name):
    """

    :param model:
    :param model_path:
    :param mtlib_name:
    :return:
    """
    try:
        file_path = os.path.join(os.path.dirname(model_path), mtlib_name)
        if not os.path.exists(file_path):
            return 0
        f = open(file_path, 'r')
        material = GLMMaterial()
        lines = f.readlines()
        for line in lines:
            content = line.split(' ', 1)
            if line[0] == '#':  # comment
                continue
            elif content[0] == 'newmtl':  # newmtl
                if len(content) > 1:
                    mtl_name = (content[1]).strip()
                    material = GLMMaterial()
                    material.name = mtl_name
                    material.diffuse = [0.8, 0.8, 0.8, 1.0]
                    material.ambient = [0.2, 0.2, 0.2, 1.0]
                    material.specular = [0.0, 0.0, 0.0, 1.0]
                    material.shininess = 65.0
                    model.materials.append(material)
                continue
            # 材质
            elif content[0] == 'Ka':
                if len(content) > 1:
                    value_str = content[1].strip().split(' ')
                    value_float = list(map(float, value_str))
                    material.ambient[0:3] = value_float[0:3]
                continue
            elif content[0] == 'Kd':
                if len(content) > 1:
                    value_str = content[1].strip().split(' ')
                    value_float = list(map(float, value_str))
                    material.diffuse[0:3] = value_float[0:3]
                continue
            elif content[0] == 'Ks':
                if len(content) > 1:
                    value_str = content[1].strip().split(' ')
                    value_float = list(map(float, value_str))
                    material.specular[0:3] = value_float[0:3]
                continue
            elif content[0] == 'Ns':
                if len(content) > 1:
                    # wavefront shininess is from [0, 1000]
                    value = float((content[1]).strip()) / 1000.0 * 128.0
                    material.ns_exponent = value
                continue
            elif content[0] == 'd':
                continue
            # 纹理
            elif content[0] == 'map_Ka':
                continue
            elif content[0] == 'map_Kd':
                continue
            elif content[0] == 'map_Ks':
                continue
            elif content[0] == 'map_Ns':
                continue
            elif content[0] == 'map_d':
                continue
            else:
                continue
    except Exception as e:
        print(e)
    if f:
        f.close()
    return 1


def glm_write_mtl(model, model_path, mtlib_name):
    """

    :param model:
    :param model_path:
    :param mtlib_name:
    :return:
    """
    if not model:
        return 0
    try:
        file_name = os.path.join(os.path.dirname(model_path), mtlib_name)
        f = open(file_name, 'w')
    except Exception as e:
        print('write mtl error')
        return 0
    try:
        f.write('#  Wavefront MTL generated by GLM library\n')
        f.write('#  \n')
        f.write('#  GLM library\n')
        f.write('#  Ben Lee\n')
        f.write('#  zuojun.lzj@alibaba-inc.com\n')
        f.write('#  lizuojun@gmail.com\n')
        f.write('#  \n')
        for material in model.materials:
            buf = 'newmtl ' + material.name + '\n'
            f.write(buf)
            # diffuse
            buf = 'Kd %f %f %f\n' % (material.diffuse[0],
                                     material.diffuse[1],
                                     material.diffuse[2])
            f.write(buf)
            # ambient
            buf = 'Ka %f %f %f\n' % (material.ambient[0],
                                     material.ambient[1],
                                     material.ambient[2])
            f.write(buf)
            # specular
            buf = 'Ks %f %f %f\n' % (material.specular[0],
                                     material.specular[1],
                                     material.specular[2])
            f.write(buf)
            # ns exponent
            buf = 'Ns %f\n\n' % material.ns_exponent / 128.0 * 1000.0
            f.write(buf)
            # 纹理
            continue
    except Exception as e:
        print('write_mtl', file_name, 'error.')
        print(e)
    if f:
        f.close()


def glm_get_mtl(model, name):
    for index, material in enumerate(model.materials):
        if material.name == name:
            return index
    return 0


def glm_calc_box(model):
    max_x = min_x = model.vertices[0][0]
    max_y = min_y = model.vertices[0][0]
    max_z = min_z = model.vertices[0][0]
    for index, vertex in enumerate(model.vertices):
        if index + 1 in model.shadow_indices:
            continue
        if max_x < vertex[0]:
            max_x = vertex[0]
        if min_x > vertex[0]:
            min_x = vertex[0]
        if max_y < vertex[1]:
            max_y = vertex[1]
        if min_y > vertex[1]:
            min_y = vertex[1]
        if max_z < vertex[2]:
            max_z = vertex[2]
        if min_z > vertex[2]:
            min_z = vertex[2]
    model.bbox.min = [min_x, min_y, min_z]
    model.bbox.max = [max_x, max_y, max_z]


def glm_calc_face(model, face_add=1):
    if len(model.faces_normals) == 0:
        model.faces_normals.append([0, 0, 0])
    for index, triangle in enumerate(model.faces):
        triangle.f_index = index + face_add
        n = [0, 0, 0]
        if len(triangle.v_indices) >= 3:
            v0_index, v1_index, v2_index = triangle.v_indices[0], triangle.v_indices[1], triangle.v_indices[2]
            v0, v1, v2 = model.vertices[v0_index], model.vertices[v1_index], model.vertices[v2_index]
            u = [v1[i] - v0[i] for i in range(min(len(v1), len(v0)))]
            v = [v2[i] - v0[i] for i in range(min(len(v2), len(v0)))]
            glm_cross(u, v, n)
            glm_normal_vector(n)
        if len(model.faces_normals) > index + 1:
            model.faces_normals[index + 1] = n
        else:
            model.faces_normals.append(n)


def glm_calc_vertex(model, angle):
    if len(model.normals) == 0:
        model.normals.append([0, 0, 0])
    cosine_angle = math.cos(angle * math.pi / 180)
    normal_faces_list = [[] for n in range(len(model.vertices))]
    normal_flags_list = [[] for n in range(len(model.vertices))]
    for triangle_index, triangle_info in enumerate(model.faces):
        for v_index in triangle_info.v_indices:
            if 0 <= v_index < len(model.vertices):
                normal_faces_list[v_index].append(triangle_index)
    for normal_index, normal_faces in enumerate(normal_faces_list):
        if len(normal_faces) <= 0:
            continue
        average_flag = False
        average_norm = [0, 0, 0]
        triangle_0 = model.faces[normal_faces[0]]
        facenorm_0 = model.faces_normals[triangle_0.f_index]
        for j in normal_faces:
            triangle_j = model.faces[j]
            facenorm_j = model.faces_normals[triangle_j.f_index]
            dot = glm_dot(facenorm_0, facenorm_j)
            if dot > cosine_angle:
                normal_flags_list[normal_index].append(1)
                average_norm[0] += facenorm_j[0]
                average_norm[1] += facenorm_j[1]
                average_norm[2] += facenorm_j[2]
                average_flag = True
            else:
                normal_flags_list[normal_index].append(0)
        if average_flag:
            glm_normal_vector(average_norm)
            model.normals.append(average_norm)
        average_index = len(model.normals) - 1
        for i, j in enumerate(normal_faces):
            triangle_j = model.faces[j]
            facenorm_j = model.faces_normals[triangle_j.f_index]
            if normal_flags_list[normal_index][i]:
                for v_i, v_j in enumerate(triangle_j.v_indices):
                    triangle_j.n_indices.append(0)
                    if v_j == normal_index:
                        triangle_j.n_indices[v_i] = average_index
            else:
                model.normals.append(facenorm_j)
                for v_i, v_j in enumerate(triangle_j.v_indices):
                    triangle_j.n_indices.append(0)
                    if v_j == normal_index:
                        triangle_j.n_indices[v_i] = len(model.normals) - 1


def glm_dot(u, v):
    return u[0] * v[0] + u[1] * v[1] + u[2] * v[2]


def glm_cross(u, v, n):
    n[0] = u[1] * v[2] - u[2] * v[1]
    n[1] = u[2] * v[0] - u[0] * v[2]
    n[2] = u[0] * v[1] - u[1] * v[0]


def glm_normal_vector(v):
    l2 = np.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])
    if l2 < 0.00000000001:
        v[0] = 0
        v[1] = 0
        v[2] = 0
    else:
        v[0] = v[0] / l2
        v[1] = v[1] / l2
        v[2] = v[2] / l2


def glm_normal_vertex(model_set, decor_bot={}, decor_bak={}, decor_frt={}, ratio=1.0):
    # 判断
    if len(model_set) <= 0:
        return
    model_one = model_set[0]
    if len(model_one.vertices) < 1:
        return
    if len(model_one.bbox.min) < 3 or len(model_one.bbox.min) < 3:
        glm_calc_box(model_one)
    # min
    min_x = model_one.bbox.min[0]
    min_y = model_one.bbox.min[1]
    min_z = model_one.bbox.min[2]
    # max
    max_x = model_one.bbox.max[0]
    max_y = model_one.bbox.max[1]
    max_z = model_one.bbox.max[2]
    # center
    center_x = (max_x + min_x) / 2
    center_y = (max_y + min_y) / 2
    center_z = (max_z + min_z) / 2
    for model_one in model_set:
        # scale
        scale = 1.6 / max([max_x - min_x, max_y - min_y, max_z - min_z])
        # vertex
        for vertex in model_one.vertices:
            vertex[0] = (vertex[0] - center_x) * scale
            vertex[1] = (vertex[1] - center_y) * scale
            vertex[2] = (vertex[2] - center_z) * scale
    # bottom
    if ratio <= 0.0000000001:
        ratio = 1
    for bot_key, bot_val in decor_bot.items():
        for bot_one in bot_val:
            bot_one[0] = (bot_one[0] / ratio - center_x) * scale
            bot_one[1] = (bot_one[1] / ratio - center_y) * scale
            bot_one[2] = (bot_one[2] / ratio - center_z) * scale
            bot_one[3] = (bot_one[3] / ratio - center_x) * scale
            bot_one[4] = (bot_one[4] / ratio - center_y) * scale
            bot_one[5] = (bot_one[5] / ratio - center_z) * scale
            bot_one[6] *= scale
    for bak_key, bak_val in decor_bak.items():
        for bak_one in bak_val:
            bak_one[0] = (bak_one[0] / ratio - center_x) * scale
            bak_one[1] = (bak_one[1] / ratio - center_y) * scale
            bak_one[2] = (bak_one[2] / ratio - center_z) * scale
            bak_one[3] = (bak_one[3] / ratio - center_x) * scale
            bak_one[4] = (bak_one[4] / ratio - center_y) * scale
            bak_one[5] = (bak_one[5] / ratio - center_z) * scale
            bak_one[6] *= scale
    for bak_key, bak_val in decor_frt.items():
        for bak_one in bak_val:
            bak_one[0] = (bak_one[0] / ratio - center_x) * scale
            bak_one[1] = (bak_one[1] / ratio - center_y) * scale
            bak_one[2] = (bak_one[2] / ratio - center_z) * scale
            bak_one[3] = (bak_one[3] / ratio - center_x) * scale
            bak_one[4] = (bak_one[4] / ratio - center_y) * scale
            bak_one[5] = (bak_one[5] / ratio - center_z) * scale
            bak_one[6] *= scale


def glm_read_mesh(mesh_json):
    # 声明
    model_set = []
    # 遍历
    for mesh_idx, mesh_val in enumerate(mesh_json):
        model = GLMModel()
        model.obj_path = ''
        group = glm_add_group(model, 'default')  # default group
        material = 0  # default material
        # 读取
        xyz, face, normal, uv = [], [], [], []
        if 'xyz' in mesh_val:
            xyz = mesh_val['xyz']
        if 'face' in mesh_val:
            face = mesh_val['face']
        if 'normal' in mesh_val:
            normal = mesh_val['normal']
        if 'uv' in mesh_val:
            uv = mesh_val['uv']
        # 顶点
        cnt = int(len(xyz) / 3)
        for idx in range(cnt):
            vec = [xyz[idx * 3 + 0], xyz[idx * 3 + 1], xyz[idx * 3 + 2]]
            model.vertices.append(vec)
        # 法线
        cnt = int(len(normal) / 3)
        for idx in range(cnt):
            vec = [normal[idx * 3 + 0], normal[idx * 3 + 1], normal[idx * 3 + 2]]
            model.normals.append(vec)
        # 纹理
        cnt = int(len(uv) / 2)
        for idx in range(cnt):
            vec = [uv[idx * 2 + 0], uv[idx * 2 + 1]]
            model.coords.append(vec)
        # 索引
        cnt = int(len(face) / 3)
        for idx in range(cnt):
            triangle = GLMTriangle()
            triangle.v_indices.append(face[idx * 3 + 0])
            triangle.v_indices.append(face[idx * 3 + 1])
            triangle.v_indices.append(face[idx * 3 + 2])
            if len(triangle.v_indices) > 0:
                model.faces.append(triangle)
                group.faces.append(len(model.faces) - 1)
        # 添加
        glm_calc_box(model)
        glm_calc_face(model)
        glm_calc_vertex(model, 90)
        model.custom_mesh = mesh_val
        model_set.append(model)
    # 返回
    return model_set


def glm_write_mesh(model_set, file_name):
    pass
