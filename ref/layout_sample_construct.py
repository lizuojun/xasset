# -*- coding: utf-8 -*-

"""
@Author: liqing.zhc
@Date: 2021-08-31
@Description: 场景重建接口

"""
from LayoutDecoration.house_recon import construct_house


# 机位函数入口
def layout_sample_construct(house_data_info):
    return construct_house(house_data_info)


# 功能测试
if __name__ == '__main__':
    pass
