# -*- coding: utf-8 -*-
import os
import sys
import requests
from io import BytesIO

import oss2
import json


# RAM信息
ACCESS_ID = ''
ACCESS_SECRET = ''
ACCESS_ENDPOINT = 'http://oss-cn-hangzhou.aliyuncs.com'


def oss_upload_json(object_name, json_object, bucket_name='', access_id='', access_secret='', access_endpoint=''):
    if access_id == '':
        access_id = ACCESS_ID
    if access_secret == '':
        access_secret = ACCESS_SECRET
    if access_endpoint == '':
        access_endpoint = ACCESS_ENDPOINT
    auth = oss2.Auth(access_id, access_secret)
    bucket = oss2.Bucket(auth, access_endpoint, bucket_name)
    bucket.put_object(object_name, json.dumps(json_object, indent='  '))


def oss_upload_byte(object_name, json_file_txt, bucket_name='', access_id='', access_secret='', access_endpoint=''):
    if access_id == '':
        access_id = ACCESS_ID
    if access_secret == '':
        access_secret = ACCESS_SECRET
    if access_endpoint == '':
        access_endpoint = ACCESS_ENDPOINT
    auth = oss2.Auth(access_id, access_secret)
    bucket = oss2.Bucket(auth, access_endpoint, bucket_name)
    bucket.put_object(object_name, json_file_txt)


def oss_copy_object(object_name, target_name, bucket_name='', access_id='', access_secret='', access_endpoint=''):
    if access_id == '':
        access_id = ACCESS_ID
    if access_secret == '':
        access_secret = ACCESS_SECRET
    if access_endpoint == '':
        access_endpoint = ACCESS_ENDPOINT
    auth = oss2.Auth(access_id, access_secret)
    bucket = oss2.Bucket(auth, access_endpoint, bucket_name)
    bucket.copy_object(bucket_name, object_name, target_name)


def oss_upload_url_image(object_name, img_url, bucket_name='', access_id='', access_secret='', access_endpoint=''):
    if access_id == '':
        access_id = ACCESS_ID
    if access_secret == '':
        access_secret = ACCESS_SECRET
    if access_endpoint == '':
        access_endpoint = ACCESS_ENDPOINT
    auth = oss2.Auth(access_id, access_secret)
    bucket = oss2.Bucket(auth, access_endpoint, bucket_name)
    response = requests.get(img_url)
    bucket.put_object(object_name, BytesIO(response.content))


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


def oss_list_file(bucket_name, object_ext='', object_idx=0, object_cnt=100000):
    auth = oss2.Auth(ACCESS_ID, ACCESS_SECRET)
    bucket = oss2.Bucket(auth, ACCESS_ENDPOINT, bucket_name)
    file_list = []
    all_cnt = 0
    out_cnt = 0
    for obj in oss2.ObjectIterator(bucket, delimiter='/'):
        # 目录
        if object_ext == '' or obj.key.endswith(object_ext):
            if all_cnt >= object_idx:
                file_list.append(obj.key)
                out_cnt += 1
            all_cnt += 1
        # 计数
        if out_cnt >= object_cnt:
            break
    return file_list


def oss_get_file_data(object_name, bucket_name, access_id='', access_secret='', access_endpoint=''):
    if access_id == '':
        access_id = ACCESS_ID
    if access_secret == '':
        access_secret = ACCESS_SECRET
    if access_endpoint == '':
        access_endpoint = ACCESS_ENDPOINT
    auth = oss2.Auth(access_id, access_secret)
    bucket = oss2.Bucket(auth, access_endpoint, bucket_name)
    data = bucket.get_object(object_name)
    return data.read()


def oss_exist_file(object_name, bucket_name):
    auth = oss2.Auth(ACCESS_ID, ACCESS_SECRET)
    bucket = oss2.Bucket(auth, ACCESS_ENDPOINT, bucket_name)
    exist = bucket.object_exists(object_name)
    return exist


def oss_delete_file(object_name, bucket_name):
    auth = oss2.Auth(ACCESS_ID, ACCESS_SECRET)
    bucket = oss2.Bucket(auth, ACCESS_ENDPOINT, bucket_name)
    ret = bucket.delete_object(object_name)
    return ret


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
