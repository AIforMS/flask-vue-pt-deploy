import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'ssssbbbb'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(basedir, 'seg_net/upload/')  # 保存用于前端可视化nii的png图片
    SUBMIT_FOLDER = os.path.join(basedir, 'seg_net/input/')  # 保存用于输入神经网络的nii图片
    RESULT_FOLDER = os.path.join(basedir, 'seg_net/output/')
