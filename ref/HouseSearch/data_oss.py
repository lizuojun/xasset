# -*- coding: utf-8 -*-

"""
@Author: lizuojun
@Date: 2019-04-22
@Description: OSS数据的增删改查

"""
import json
import os
import sys
import oss2

# RAM信息
ACCESS_ID = ''
ACCESS_SECRET = ''
ACCESS_ENDPOINT = 'http://oss-cn-hangzhou.aliyuncs.com'


# 更改账号密码
def oss_change_ram(new_id, new_secret):
    global ACCESS_ID
    global ACCESS_SECRET
    AccessKeyID = new_id
    AccessKeySecret = new_secret


# 创建Bucket
def oss_create_bucket(bucket_name):
    auth = oss2.Auth(ACCESS_ID, ACCESS_SECRET)
    bucket = oss2.Bucket(auth, ACCESS_ENDPOINT, bucket_name)
    bucket.create_bucket(oss2.models.BUCKET_ACL_PRIVATE)


# 删除Bucket
def oss_delete_bucket(bucket_name):
    auth = oss2.Auth(ACCESS_ID, ACCESS_SECRET)
    bucket = oss2.Bucket(auth, ACCESS_ENDPOINT, bucket_name)
    bucket.delete_bucket()


# 打印Bucket
def oss_print_bucket():
    auth = oss2.Auth(ACCESS_ID, ACCESS_SECRET)
    service = oss2.Service(auth, ACCESS_ENDPOINT)
    print([b.name for b in oss2.BucketIterator(service)])


# 上传文件
def oss_upload_file(object_name, file_path, bucket_name, access_id='', access_secret='', access_endpoint=''):
    if not os.path.exists(file_path):
        return
    if access_id == '':
        access_id = ACCESS_ID
    if access_secret == '':
        access_secret = ACCESS_SECRET
    if access_endpoint == '':
        access_endpoint = ACCESS_ENDPOINT
    auth = oss2.Auth(access_id, access_secret)
    bucket = oss2.Bucket(auth, access_endpoint, bucket_name)
    bucket.put_object_from_file(object_name, file_path)


# 下载文件
def oss_download_file(object_name, file_path, bucket_name, access_id='', access_secret='', access_endpoint=''):
    if access_id == '':
        access_id = ACCESS_ID
    if access_secret == '':
        access_secret = ACCESS_SECRET
    if access_endpoint == '':
        access_endpoint = ACCESS_ENDPOINT
    auth = oss2.Auth(access_id, access_secret)
    bucket = oss2.Bucket(auth, access_endpoint, bucket_name)
    bucket.get_object_to_file(object_name, file_path)


def oss_get_json(object_name, bucket_name, access_id='', access_secret='', access_endpoint=''):
    if access_id == '':
        access_id = ACCESS_ID
    if access_secret == '':
        access_secret = ACCESS_SECRET
    if access_endpoint == '':
        access_endpoint = ACCESS_ENDPOINT
    auth = oss2.Auth(access_id, access_secret)
    bucket = oss2.Bucket(auth, access_endpoint, bucket_name)
    return json.loads(bucket.get_object(object_name).read())


# 删除文件
def oss_delete_file(object_name, bucket_name):
    auth = oss2.Auth(ACCESS_ID, ACCESS_SECRET)
    bucket = oss2.Bucket(auth, ACCESS_ENDPOINT, bucket_name)
    bucket.delete_object(object_name)


# 检查文件
def oss_exist_file(object_name, bucket_name):
    auth = oss2.Auth(ACCESS_ID, ACCESS_SECRET)
    bucket = oss2.Bucket(auth, ACCESS_ENDPOINT, bucket_name)
    exist = bucket.object_exists(object_name)
    return exist


# 列举文件
def oss_list_file(bucket_name, object_ext='', object_idx=0, object_cnt=10000):
    auth = oss2.Auth(ACCESS_ID, ACCESS_SECRET)
    bucket = oss2.Bucket(auth, ACCESS_ENDPOINT, bucket_name)
    file_list = []
    all_cnt = 0
    out_cnt = 0
    for obj in oss2.ObjectIterator(bucket, delimiter='/'):
        # 目录
        if obj.is_prefix():
            continue
        else:
            if object_ext == '' or obj.key.endswith(object_ext):
                if all_cnt >= object_idx:
                    file_list.append(obj.key)
                    out_cnt += 1
                all_cnt += 1
            # 计数
            if out_cnt >= object_cnt:
                break
    return file_list


# 测试功能
if __name__ == '__main__':
    # 版本信息
    print(oss2.__version__)
    # Bucket信息
    oss_print_bucket()

