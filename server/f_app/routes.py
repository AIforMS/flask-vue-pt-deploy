from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

# coding=utf-8

import os
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
from f_app.utils import get_seg, get_score, nii_to_png, png_to_nii
from f_app.auth import basic_auth, token_auth

from seg_net.step2to4_train_validate_inference import step3_TestOrInference
get_seg = step3_TestOrInference.get_seg
from config import basedir

upload_path = app.config['UPLOAD_FOLDER']
submit_path = app.config['SUBMIT_FOLDER']
result_path = app.config['RESULT_FOLDER']


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

    if os.path.exists(upload_path):
        shutil.rmtree(upload_path)  # upload
    os.mkdir(upload_path)

    if os.path.exists(submit_path):
        shutil.rmtree(submit_path)  # input
    os.mkdir(submit_path)

    if os.path.exists(result_path):
        shutil.rmtree(result_path)  # output
    os.mkdir(result_path)

    if request.method == 'POST':
        f = request.files['file']
        sessionId = request.form['id']  # front-end session id
        fileType = request.form['fileType']  # img or nii
        # print(f)
        fileName = secure_filename(f.filename)
        global filePath
        filePath = os.path.join(submit_path, fileName)

        global out_path
        out_path = os.path.join(result_path, f'{sessionId}.png')

        f.save(filePath)

        print(f'{fileName} saved to {submit_path}')

        if fileType == 'nii':
            nii_src = filePath
            global dst
            dst = os.path.join(upload_path, f"{fileName}.png")
            img_base64 = nii_to_png(filePath, dst)
            # get_seg(dst, out_path)
            return img_base64  # 返回前端
        else:
            # contentPath = os.path.join(upload_path, f'{sessionId}.png')
            # print(contentPath)
            # imgData = re.sub('^data:image/.+;base64,', '', contentData)
            imgContent = Image.open(filePath)  # 420 x 420 ?!
            imgContent = np.asarray(imgContent)
            print(imgContent.shape)
            # imgContent.save(contentPath)
            # nii_src = png_to_nii(contentPath, os.path.join(submit_path, fileName))
        
    return ''


@app.route('/seg', methods=['GET', 'POST'])
# @login_required
def seg():

    resp = {}  # 返回前端的json数据

    if request.method == 'POST':
        sessionId = request.form['id']  # front-end session id
        userContent = request.form['userContent']  # bool
        contentData = request.form['contentData']  # img data base64 src, if nii, none
        fileType = request.form['fileType']  # img or nii
        fileName = request.form['fileName']

        # get_seg(dst, out_path)  # 分割结果保存在 out_path
        if fileType == 'nii':
            get_seg(dst, out_path)
        else:
            get_seg(filePath, out_path)  # 分割结果保存在 out_path

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
