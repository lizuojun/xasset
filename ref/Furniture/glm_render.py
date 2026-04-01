# -*- coding: utf-8 -*-

"""
@Author:
@Date: 2018-11-26
@Description:

"""

import os
# 临时目录
DATA_DIR_FURNITURE = os.path.dirname(__file__) + '/temp/'
if not os.path.exists(DATA_DIR_FURNITURE):
    os.makedirs(DATA_DIR_FURNITURE)
DATA_DIR_FURNITURE_OBJ = os.path.dirname(__file__) + '/temp/obj/'
if not os.path.exists(DATA_DIR_FURNITURE_OBJ):
    os.makedirs(DATA_DIR_FURNITURE_OBJ)

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import pygame
from pygame.constants import *
from PIL import Image
from Furniture.glm_interface import *

# 视口大小
viewport = (227, 227)


def glm_create_list_by_model(model_set, decor_bot={}, decor_bak={}, decor_frt={}):
    # 开始
    gl_list = glGenLists(1)
    glNewList(gl_list, GL_COMPILE)
    glEnable(GL_TEXTURE_2D)
    glFrontFace(GL_CCW)
    for model_one in model_set:
        # 顶点
        for group in model_one.groups:
            if group.name == 'shadow':
                continue
            for i in group.faces:
                if i >= len(model_one.faces):
                    continue
                triangle = model_one.faces[i]
                # triangle
                if len(triangle.v_indices) == 3:
                    glBegin(GL_TRIANGLES)
                    glColor3f(0.71, 0.71, 0.71)
                    glNormal3f(0, 0, 0)
                    # face normal
                    f_index = triangle.f_index
                    if f_index < len(model_one.faces_normals):
                        # face normal
                        glNormal3f(model_one.faces_normals[f_index][0], model_one.faces_normals[f_index][1], model_one.faces_normals[f_index][2])
                    # vertex
                    for j in range(len(triangle.v_indices)):
                        # vertex normal
                        if j < len(triangle.n_indices):
                            n_index = triangle.n_indices[j]
                            glNormal3f(model_one.normals[n_index][0], model_one.normals[n_index][1], model_one.normals[n_index][2])
                        # vertex
                        v_index = triangle.v_indices[j]
                        glVertex3fv(model_one.vertices[v_index])
                    glEnd()
                # polygon
                elif len(triangle.v_indices) >= 4:
                    glBegin(GL_POLYGON)
                    glColor3f(0.71, 0.71, 0.71)
                    glNormal3f(0, 0, 0)
                    # face normal
                    f_index = triangle.f_index
                    if f_index < len(model_one.faces_normals):
                        # face normal
                        glNormal3f(model_one.faces_normals[f_index][0], model_one.faces_normals[f_index][1], model_one.faces_normals[f_index][2])
                    # vertex
                    for j in range(len(triangle.v_indices)):
                        # vertex normal
                        if j < len(triangle.n_indices):
                            n_index = triangle.n_indices[j]
                            glNormal3f(model_one.normals[n_index][0], model_one.normals[n_index][1], model_one.normals[n_index][2])
                        # vertex
                        v_index = triangle.v_indices[j]
                        glVertex3fv(model_one.vertices[v_index])
                    glEnd()
    # 承载面
    for bot_key, bot_set in decor_bot.items():
        for bot_one in bot_set:
            x1, y1, z1, x2, y2, z2 = bot_one[0], bot_one[1], bot_one[2], bot_one[3], bot_one[4], bot_one[5]
            y0 = (y1 + y2) / 2 + 0.01
            glBegin(GL_TRIANGLES)
            glColor3f(0.71, 0.21, 0.21)
            glNormal3f(0, 1, 0)
            glVertex3fv([x1, y0, z1])
            glVertex3fv([x1, y0, z2])
            glVertex3fv([x2, y0, z2])
            glVertex3fv([x2, y0, z2])
            glVertex3fv([x2, y0, z1])
            glVertex3fv([x1, y0, z1])
            glEnd()
            pass
    # 依附面
    for bak_key, bak_set in decor_bak.items():
        for bak_one in bak_set:
            x1, y1, z1, x2, y2, z2 = bak_one[0], bak_one[1], bak_one[2], bak_one[3], bak_one[4], bak_one[5]
            z0 = (z1 + z2) / 2 + 0.01
            glBegin(GL_TRIANGLES)
            glColor3f(0.21, 0.21, 0.71)
            glNormal3f(0, 1, 0)
            glVertex3fv([x1, y1, z0])
            glVertex3fv([x1, y2, z0])
            glVertex3fv([x2, y2, z0])
            glVertex3fv([x2, y2, z0])
            glVertex3fv([x2, y1, z0])
            glVertex3fv([x1, y1, z0])
            glEnd()
            pass
    # 覆盖面
    for bak_key, bak_set in decor_frt.items():
        for bak_one in bak_set:
            x1, y1, z1, x2, y2, z2 = bak_one[0], bak_one[1], bak_one[2], bak_one[3], bak_one[4], bak_one[5]
            z0 = (z1 + z2) / 2 + 0.01
            glBegin(GL_TRIANGLES)
            glColor3f(0.21, 0.21, 0.71)
            glNormal3f(0, 1, 0)
            glVertex3fv([x1, y1, z0])
            glVertex3fv([x1, y2, z0])
            glVertex3fv([x2, y2, z0])
            glVertex3fv([x2, y2, z0])
            glVertex3fv([x2, y1, z0])
            glVertex3fv([x1, y1, z0])
            glEnd()
            pass
    # 结束
    glDisable(GL_TEXTURE_2D)
    glEndList()
    return gl_list


def glm_create_list_by_scene():
    # TODO:
    pass


def glm_create_list_by_group():
    # TODO:
    pass


def glm_render_initial(size=(227, 227)):
    global viewport
    viewport = size
    pygame.init()
    pygame.display.set_mode(viewport, OPENGL | DOUBLEBUF)
    # glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH | GLUT_MULTISAMPLE)
    # 设置
    glClearColor(1.0, 1.0, 1.0, 0.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    # 法线向量标准化
    glEnable(GL_NORMALIZE)
    # 光照
    glLightfv(GL_LIGHT0, GL_AMBIENT, (32.0 / 255.0, 32.0 / 255.0, 32.0 / 255.0, 1.0))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (182.0 / 255.0, 182.0 / 255.0, 182.0 / 255.0, 1.0))
    glLightfv(GL_LIGHT0, GL_SPECULAR, (0.6, 0.6, 0.6, 1.0))
    # glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.3, 1.0))
    # glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.9, 0.9, 0.9, 1.0))
    # glLightfv(GL_LIGHT0, GL_SPECULAR, (1.0, 1.0, 1.0, 1.0))
    # glLightfv(GL_LIGHT0, GL_POSITION, (0, 0, 1.0, 1.0))
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    # 材质
    # glMaterialfv(GL_FRONT, GL_AMBIENT, (1.0, 1.0, 1.0, 1.0))
    # glMaterialfv(GL_FRONT, GL_DIFFUSE, (1.0, 1.0, 1.0, 1.0))
    # glMaterialfv(GL_FRONT, GL_SPECULAR, (1.0, 1.0, 1.0, 1.0))
    # glMaterialf(GL_FRONT, GL_SHININESS, 50.0)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    # 着色模式
    glShadeModel(GL_SMOOTH)  # most obj files expect to be smooth-shaded
    # 过滤绘制线
    glEnable(GL_LINE_SMOOTH)
    # 深度测试
    glEnable(GL_DEPTH_TEST)
    # 抗锯齿
    glEnable(GL_MULTISAMPLE)
    # 裁剪
    glDisable(GL_CULL_FACE)
    #
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(0, -1.732 * 2, 1 * 2,
              0, 0, 0,
              0, 1 * 2, 1.732 * 2)


def glm_render_reshape():
    #
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-1, 1, -1, 1, 1.0, 20.0)
    #
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(0, -1.732 * 2, 1 * 2,
              0, 0, 0,
              0, 1 * 2, 1.732 * 2)


def glm_render_display(model_set, decor_bot={}, decor_bak={}, decor_frt={}, rotate=True):
    # 判断
    if len(model_set) <= 0:
        return
    model_one = model_set[0]
    # 读取
    # glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    glRotatef(90, 1, 0, 0)
    gl_list = glm_create_list_by_model(model_set, decor_bot, decor_bak, decor_frt)
    # 渲染
    while 1:
        for e in pygame.event.get():
            if e.type == QUIT:
                sys.exit()
            elif e.type == KEYDOWN and e.key == K_ESCAPE:
                sys.exit()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        # seeds
        if len(model_one.seed_all) > 0 and 0 <= model_one.seed_now < len(model_one.seed_all):
            seed = model_one.seed_all[model_one.seed_now]
            glTranslatef(seed[0], seed[1], seed[2])
            glColor3f(0, 0, 0.8)
            glutSolidSphere(0.15, 16, 16)
            glTranslatef(-seed[0], -seed[1], -seed[2])
        # vertex
        glCallList(gl_list)
        pygame.display.flip()
        if rotate:
            glRotatef(0.2, 0, 1, 0)


def glm_render_project(model_set, des_dir='', view_num=1, seed_dot=False):
    if not os.path.exists(des_dir):
        os.makedirs(des_dir)
    # 判断
    if len(model_set) <= 0:
        return
    model_one = model_set[0]
    # 读取
    glRotatef(90, 1, 0, 0)
    gl_list = glm_create_list_by_model(model_set)
    # 渲染
    for i in range(view_num):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        # seeds
        if len(model_one.seed_all) > 0 and 0 <= model_one.seed_now < len(model_one.seed_all) and seed_dot:
            seed = model_one.seed_all[model_one.seed_now]
            glTranslatef(seed[0], seed[1], seed[2])
            glColor3f(0, 0, 0.8)
            glutSolidSphere(0.15, 16, 16)
            glTranslatef(-seed[0], -seed[1], -seed[2])
        # vertex
        glCallList(gl_list)
        # screen
        obj_name = os.path.basename(model_one.obj_path)[:-4]
        if seed_dot:
            des_path = os.path.join(des_dir, obj_name + '_%d_seed.jpg' % (i + 1))
        else:
            des_path = os.path.join(des_dir, obj_name + '_%d.jpg' % (i + 1))
        glm_render_shot(des_path)
        #
        pygame.display.flip()
        glRotatef(360.0 / view_num, 0, 1, 0)


def glm_render_shot(path):
    width, height = viewport
    buffer = glReadPixels(0, 0, width, height, GL_RGB, GL_UNSIGNED_BYTE)
    image = Image.frombytes(mode="RGB", size=(width, height), data=buffer)
    image = image.rotate(180)
    image = image.transpose(Image.FLIP_LEFT_RIGHT)
    image.save(path)


if __name__ == '__main__':
    # 显示数据
    obj_id = 'e99bb94a-8287-41a0-b9c7-4bd639816548'
    obj_path = os.path.join(DATA_DIR_FURNITURE_OBJ, obj_id + '.obj')
    # 读取模型
    model_one = glm_read_obj(obj_path)
    # 显示模型
    if model_one:
        model_set = [model_one]
        glm_normal_vertex(model_set)
        glm_render_initial()
        glm_render_reshape()
        glm_render_display(model_set, {}, {}, {}, True)
