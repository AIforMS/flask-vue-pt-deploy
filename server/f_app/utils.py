import os
import base64
import nibabel as nib
import numpy as np


def get_seg(content_path, out_path, *args):
    """
    todo: 通过命令行指定原图和分割标签的输出路径
    return:
      直接保存分割标签到文件夹，读取后base64编码再发送到前端
    """
    return ''


def get_score(out_path):
    """
    todo: 得到分割图片后计算指标
    return: 
      :labelArea: 分割面积
      :labelCoverage: 分割标签覆盖率
      :fakeDice: 银dice
    """
    return 1, 2, 3
