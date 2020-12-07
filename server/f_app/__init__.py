from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

# coding=utf-8
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from config import Config


app = Flask(__name__)
CORS(app)  # 前后端跨域

app.config.from_object(Config)

# 插件初始化
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'  # 指定登录界面的URL

from f_app import routes, user_model, utils, auth
