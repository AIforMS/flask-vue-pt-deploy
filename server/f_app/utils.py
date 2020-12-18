import os
import shutil
import base64
import numpy as np
import nibabel as nib
from PIL import Image

# from config import basedir


def nii_to_png(src, dst):
    """
    将 nii 图片转成 png 并返回 base64 编码，以便前端展示源图
    src: 源图像完整路径
    dst: 目标 png 图像的存放的完整路径

    return:
      png 图像的 base64 编码
    """

    nib_img = nib.load(src)
    affine = nib_img.affine
    print(nib_img.shape)

    np_img = np.asarray(nib_img.dataobj)
    print(np_img[:,:,0].shape)  # np.ndarray 的二维图像矩阵为：[w, h, c]
    save_img = Image.fromarray(np.uint8(np_img[:, :, 0]))
    save_img.save(dst)

    try:
        with open(dst, 'rb') as f:
            return u"data:image/png;base64," + base64.b64encode(f.read()).decode('ascii')
    except Exception as e:
        print(str(e))
        return "Encode to base64 failed"


def png_to_nii(src, dst):
    """
    将 png 图片保存成 nii 格式，以便分割

    return:
      dst
    """
    np_img = np.asarray(Image.open(src))
    print(np_img.shape)
    # np_img = np.rot90(np_img, 2)  # 取值一般为1、2、3，分别表示旋转90度、180度、270度；k也可以取负数，-1、-2、-3。k取正数表示逆时针旋转，取负数表示顺时针旋转。
    np_img = np.mean(np_img, axis=2)  # 转为灰度图
    affine = affine = np.eye(4)  # 一般png转成nii的affine设成4×4的单位矩阵

    nib.save(nib.Nifti1Image(np_img, affine), dst)  # 保存的图像是顺时针旋转90°的
    print('Png saved to nii')
    # nib_img = nib.load(dst)
    # nib_img = np.asarray(nib_img.dataobj)
    # print(nib_img.shape)
    return dst


def get_seg(content_path, out_path, *args):
    """
    todo: 通过命令行指定原图和分割标签的输出路径
    return:
      直接保存分割标签到文件夹，读取后base64编码再发送到前端
    """
    return r'D:\code_sources\from_github\Flask-Vue-Deploy\server\seg_net\output\Pancreas_002_0000.nii.gz.png'


def get_score(out_path):
    """
    todo: 得到分割图片后计算指标
    return: 
      :labelArea: 分割面积
      :labelCoverage: 分割标签覆盖率
      :fakeDice: 银dice
    """
    return 1, 2, 3


if __name__ == '__main__':
    basedir = r'D:/code_sources/from_github/Flask-Vue-Deploy/server'
    src = os.path.join(basedir, 'seg_net/input/FraserRiver.jpg')
    dst = os.path.join(basedir, 'seg_net/upload/FraserRiver.nii')
    # png_to_nii(src, dst)
    # upload_path = os.path.join(basedir, 'seg_net/upload')
    # if os.path.exists(dst):
    # 	shutil.rmtree(dst)
    # os.mkdir(dst)
    # print(nii_to_png(src, dst))
