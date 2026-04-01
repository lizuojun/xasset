# -*- coding: utf-8 -*-

"""
@Author: lizuojun
@Date: 2020-05-09
@Description: 布局日志入口

"""

import shutil
import datetime
from House.data_oss import *

# 临时目录
DATA_DIR_SERVER_LOG = os.path.dirname(__file__) + '/temp/log/'
if not os.path.exists(DATA_DIR_SERVER_LOG):
    os.makedirs(DATA_DIR_SERVER_LOG)


# 布局日志参数
LAYOUT_LOGGING_OLD = datetime.datetime.now()
LAYOUT_LOGGING_STR = ''
# 布局日志参数
LAYOUT_LOGGING_MAX = 10
LAYOUT_LOGGING_OSS = 'ihome-alg-log'


# 创建日志
def layout_log_create(log_max=10):
    global LAYOUT_LOGGING_OLD
    global LAYOUT_LOGGING_STR
    global LAYOUT_LOGGING_MAX
    LAYOUT_LOGGING_OLD = datetime.datetime.now()
    LAYOUT_LOGGING_STR = ''
    LAYOUT_LOGGING_STR += '0000 '
    LAYOUT_LOGGING_STR += datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
    LAYOUT_LOGGING_STR += '\n'
    if log_max > 0:
        LAYOUT_LOGGING_MAX = log_max
    print()


# 更新日志
def layout_log_update(log_add):
    global LAYOUT_LOGGING_OLD
    global LAYOUT_LOGGING_STR
    time_old = LAYOUT_LOGGING_OLD
    time_now = datetime.datetime.now()
    time_dlt = (time_now - time_old).total_seconds()
    LAYOUT_LOGGING_STR += '%04d ' % int(time_dlt)
    LAYOUT_LOGGING_STR += log_add
    LAYOUT_LOGGING_STR += '\n'
    print(log_add, flush=True)


# 上传日志
def layout_log_upload(log_dir, log_key, log_mod=1):
    global LAYOUT_LOGGING_OLD
    global LAYOUT_LOGGING_STR
    global LAYOUT_LOGGING_MAX
    global LAYOUT_LOGGING_OSS
    # 日期
    time_now = datetime.datetime.now()
    time_dir = time_now.strftime('%Y-%m-%d')
    time_key = time_now.strftime('%H-%M-%S')
    # 间隔
    time_old = LAYOUT_LOGGING_OLD
    time_max = LAYOUT_LOGGING_MAX
    time_dlt = (time_now - time_old).total_seconds()
    # 条件
    if log_mod <= 0 or (log_mod >= 1 and time_dlt >= time_max):
        # 内容
        log_str = LAYOUT_LOGGING_STR
        # 下载
        log_path = os.path.join(DATA_DIR_SERVER_LOG, log_key + '_' + time_key + '.log')
        fp = open(log_path, 'a')
        fp.write(log_str)
        fp.close()
        # 上传
        log_des = log_dir + '/' + time_dir + '/' + log_key + '_' + time_key + '.log'
        log_src = log_path
        log_oss = LAYOUT_LOGGING_OSS
        if os.path.exists(log_src):
            oss_upload_file(log_des, log_src, log_oss)


# 清空日志
def layout_log_clear():
    # 清空
    if os.path.exists(DATA_DIR_SERVER_LOG):
        shutil.rmtree(DATA_DIR_SERVER_LOG)
    # 重建
    if not os.path.exists(DATA_DIR_SERVER_LOG):
        os.makedirs(DATA_DIR_SERVER_LOG)