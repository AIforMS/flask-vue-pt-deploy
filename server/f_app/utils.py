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
	print(np_img[:,:,0].shape)
	save_img = Image.fromarray(np.uint8(np_img[:, :, 0]))
	save_img.save(dst)
    
	try:
		with open(dst, 'rb') as f:
			return u"data:image/png;base64," + base64.b64encode(f.read()).decode('ascii')
	except Exception as e:
		print(str(e))
		return "Encode to base64 failed"


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


if __name__ == '__main__':
	basedir = r'D:/code_sources/from_github/Flask-Vue-Deploy/server'
	src = os.path.join(basedir, 'seg_net/input/Pancreas_001_0000.nii.gz')
	dst = os.path.join(basedir, 'seg_net/upload/aa.png')
	# upload_path = os.path.join(basedir, 'seg_net/upload')
	# if os.path.exists(dst):
	# 	shutil.rmtree(dst)
	# os.mkdir(dst)
	# print(nii_to_png(src, dst))
