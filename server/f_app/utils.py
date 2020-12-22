import os
import time
import shutil
from threading import Thread
import base64
import hashlib

import numpy as np
import nibabel as nib
from PIL import Image

if not __name__ == '__main__':
    from config import Config

    upload_path = Config.UPLOAD_FOLDER
    submit_path = Config.SUBMIT_FOLDER
    result_path = Config.RESULT_FOLDER

    dir_list = [upload_path, submit_path, result_path]
# dir_list = (r'D:\code_sources\from_github\lese\test', r'D:\code_sources\from_github\lese\components')

def clear_dir(dir_list, time_step=3600):
    """
    异步清理文件夹，将一小时前新增的文件清理掉，同时，新增的文件名使用session id命名。
    这个函数通过时间戳判断，异步清理旧文件
    """
    for dir in dir_list:
        for file in os.listdir(dir):
            file_path = os.path.join(dir, file)
            f_mtime = os.path.getmtime(file_path)
            time_now = time.time()
            last = time_now - f_mtime
            msg = "dleted! " if last > time_step else "retain. "
            if msg == "dleted! ":
                print(f"File '{file_path}' {msg} last for {last // 3600} hours")
            if last > time_step:
                os.remove(file_path)

def clear_dir_async():
    Thread(target=clear_dir, kwargs={'dir_list': dir_list}).start()

def test_async():
    clear_dir_async()


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


def get_score(out_path):
    """
    todo: 得到分割图片后计算指标
    return: 
      :labelArea: 分割面积
      :labelCoverage: 分割标签覆盖率
      :fakeDice: 银dice
    """
    img = np.asarray(Image.open(out_path))
    seg_area = np.sum(img > 0)
    labelCoverage = round(seg_area / img.size * 100, 1)
    labelCoverage = f"{labelCoverage}%"
    print(labelCoverage)
    return 1, labelCoverage, 3

 
def get_md5(url):
    """
    由于hash不处理unicode编码的字符串（python3默认字符串是unicode）
        所以这里判断是否字符串，如果是则进行转码
        初始化md5、将url进行加密、然后返回加密字串
    """
    if isinstance(url, str):
        url = url.encode("utf-8")
    md = hashlib.md5()
    md.update(url)
    return md.hexdigest()


if __name__ == '__main__':
    basedir = r'D:/code_sources/from_github/Flask-Vue-Deploy/server'
    src = os.path.join(basedir, 'seg_net/input/FraserRiver.jpg')
    dst = os.path.join(basedir, 'seg_net/upload/FraserRiver.nii')
    print(get_md5("_vx1wbg3qj"))
    # test_async()
    # png_to_nii(src, dst)
    # upload_path = os.path.join(basedir, 'seg_net/upload')
    # if os.path.exists(dst):
    # 	shutil.rmtree(dst)
    # os.mkdir(dst)
    # print(nii_to_png(src, dst))
