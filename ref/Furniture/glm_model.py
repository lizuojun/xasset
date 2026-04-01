# -*- coding: utf-8 -*-

"""
@Author:
@Date: 2018-11-02
@Description:

"""

glm_none = 0  # render with only vertices
glm_flat = 1 << 0  # render with facet normals
glm_smooth = 1 << 1  # render with vertex normals
glm_texture = 1 << 2  # render with texture coordinates
glm_color = 1 << 3  # render with colors
glm_material = 1 << 4  # render with materials


class GLMMaterial(object):
    def __init__(self):
        # 名称
        self.name = ''
        # 环境光
        self.ambient = [0, 0, 0, 0]
        # 散射光
        self.diffuse = [0, 0, 0, 0]
        # 镜面光
        self.specular = [0, 0, 0, 0]
        #
        self.emissive = [0, 0, 0, 0]
        # 镜面光 反射指数
        self.ns_exponent = 0
        # 环境光 颜色纹理
        self.map_ka = ''
        # 散射光 颜色纹理
        self.map_kd = ''
        # 镜面光 颜色纹理
        self.map_ks = ''
        # 镜面光 反射标量纹理
        self.map_ns = ''


class GLMTriangle(object):
    def __init__(self):
        self.v_indices = []
        self.n_indices = []
        self.t_indices = []
        self.f_index = 0


class GLMGroup(object):
    def __init__(self):
        self.name = ''  # group name
        self.faces = []  # triangle indices array
        self.material = 0  # material index


class GLMAABB(object):
    def __init__(self):
        self.vertex = [[0, 0, 0] for i in range(8)]
        self.center = [0, 0, 0]
        self.bottom = [[0, 0, 0] for i in range(8)]
        self.min = []
        self.max = []


class GLMModel(object):
    def __init__(self):
        #
        self.obj_path = ''
        self.mtl_path = ''
        #
        self.seed_all = []
        self.seed_now = 0
        #
        self.vertices = []
        self.normals = []
        self.coords = []
        self.faces = []
        self.faces_normals = []
        self.groups = []
        self.materials = []
        #
        self.bbox = GLMAABB()
        self.position = [0, 0, 0]
        #
        self.shadow_triangles = []
        self.shadow_indices = []
        #
        self.custom_mesh = {}
        self.custom_part = []
