from flask import jsonify, g
from werkzeug.http import HTTP_STATUS_CODES
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from f_app.user_model import Userr

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()

def error_response(status_code, message=None):
    payload = {'error': HTTP_STATUS_CODES.get(status_code, 'Unknown error')}
    if message:
        payload['message'] = message
    response = jsonify(payload)
    response.status_code = status_code
    return response


@basic_auth.verify_password
def verify_password(username, password):
    '''用于检查用户提供的用户名和密码'''
    user = Userr.query.filter_by(username=username).first()
    if user is None:
        return False
    g.current_user = user
    return user.check_psw(password)


@basic_auth.error_handler
def basic_auth_error():
    '''用于在认证失败的情况下返回错误响应'''
    return error_response(401)


@token_auth.verify_token
def verify_token(token):
    '''用于检查用户请求是否有token，并且token真实存在，还在有效期内'''
    g.current_user = Userr.check_token(token) if token else None
    return g.current_user is not None


@token_auth.error_handler
def token_auth_error():
    '''用于在 Token Auth 认证失败的情况下返回错误响应'''
    return error_response(401)

