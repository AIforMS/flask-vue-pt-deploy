from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

# coding=utf-8

import os
import glob
import shutil
import base64
import re
import numpy as np

import logging

from io import BytesIO
from PIL import Image

# Flask utils
from flask import request, jsonify, redirect, url_for, g
from werkzeug.utils import secure_filename
from gevent.pywsgi import WSGIServer
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from f_app import app, db
from f_app.user_model import Userr
from f_app.utils import get_score, nii_to_png, png_to_nii, clear_dir_async, png_to_gray, \
    upload_path, submit_path, result_path
from f_app.auth import basic_auth, token_auth

from seg_net.step2to4_train_validate_inference import step3_TestOrInference
get_seg = step3_TestOrInference.get_seg


# 由于这些文件夹必须要存在，所以不能异步创建
if not os.path.exists(upload_path):
    # shutil.rmtree(upload_path)  # upload
    os.mkdir(upload_path)

if not os.path.exists(submit_path):
    os.mkdir(submit_path)  # input

if not os.path.exists(result_path):
    os.mkdir(result_path)  # output


@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
# @login_required
def index():
    return 'seg server running'


@app.route('/tokens', methods=['POST'])
@basic_auth.login_required
def get_token():
    token = g.current_user.get_token()
    db.session.commit()
    return jsonify({'token': token})


@app.route('/tokens', methods=['DELETE'])
@token_auth.login_required
def revoke_token():
    g.current_user.revoke_token()
    db.session.commit()
    return '', 204


@app.route('/uploader', methods = ['GET', 'POST'])
def uploader():
    """
    用于前端上传二维nii图片的可视化
    save: nii
    return: img base64 encode
    """
    clear_dir_async()  # 异步清理相关文件夹

    if request.method == 'POST':
        f = request.files['file']
        sessionId = request.form['id']  # front-end session id
        fileType = request.form['fileType']  # img or nii
        fileName = secure_filename(f.filename)
        print(f"fileName: {fileName}")
        fileSuffix = fileName[fileName.find('.'):]
        print(f"fileType: {fileSuffix}")

        filePath = os.path.join(submit_path, f'{sessionId}{fileSuffix}')

        out_path = os.path.join(result_path, f'{sessionId}.png')
        print(f"out_path: {out_path}")

        f.save(filePath)

        print(f'{fileName} saved to {filePath}')

        if fileType in ['nii', 'nii.gz', 'gz']:
            nii_src = filePath
            dst = os.path.join(upload_path, f"{sessionId}.png")
            img_base64 = nii_to_png(filePath, dst)
            return img_base64  # 返回前端
        else:
            png_to_gray(filePath, filePath)  # png转成单通道灰度图, nii已经转了
        
    return ''


@app.route('/seg', methods=['GET', 'POST'])
# @login_required
def seg():

    resp = {}  # 返回前端的json数据

    if request.method == 'POST':
        sessionId = request.form['id']  # front-end session id
        userContent = request.form['userContent']  # bool
        contentData = request.form['contentData']  # img data base64 src, if nii, none
        fileType = request.form['fileType']  # img or nii or gz

        out_path = os.path.join(result_path, f'{sessionId}.png')
        filePath = os.path.join(submit_path, sessionId)
        filePath = glob.glob(f"{filePath}.*")[0]
        print(f"img file path: {filePath}")

        if not os.path.isfile(out_path):
            print("FALSE")
            if fileType in ['nii', 'nii.gz', 'gz']:
                get_seg(os.path.join(upload_path, f"{sessionId}.png"), out_path)
            else:
                get_seg(filePath, out_path)  # 分割结果保存在 out_path
        print("TRUE")
        labelArea, labelCoverage, fakeDice = get_score(out_path)

        with open(os.path.join(os.path.dirname(__file__), out_path), 'rb') as f:
            """data表示取得数据的协定名称,image/png是数据类型名称,base64 是数据的编码方法,
               逗号后面是image/png（.png图片）文件的base64编码.
               <img src="data:image/png;base64,iVBORw0KGgoAggg=="/>即可展示图片
            """
            img_data = u"data:image/png;base64," + base64.b64encode(f.read()).decode('ascii')
        
        resp['seg_out'] = img_data
        resp['labelArea'] = labelArea
        resp['labelCoverage'] = labelCoverage
        resp['fakeDice'] = fakeDice

        return jsonify(resp)
    return ''


if __name__ != '__main__':
    """使用gunicorn启动时将flask的日志整合到gunicorn的日志"""
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)


if __name__ == '__main__':
    # app.run(port=5002, debug=True)

    # Serve the app with gevent
    print('Start serving style transfer at port 5002...')
    http_server = WSGIServer(('', 5002), app)
    http_server.serve_forever()
