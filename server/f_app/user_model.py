import os
import base64
from datetime import datetime, timedelta

from f_app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class Userr(UserMixin, db.Model):
    """
    User 数据库表类
    """

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    psw_hash = db.Column(db.String(128))
    token = db.Column(db.String(32), index=True, unique=True)
    token_expiration = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<User {self.username}>'

    def set_psw(self, psw):
        self.psw_hash = generate_password_hash(psw)

    def check_psw(self, psw):
        return check_password_hash(self.psw_hash, psw)

    def get_token(self, expires_in=3600):
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token

    def revoke_token(self):
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)

    @staticmethod
    def check_token(token):
        user = Userr.query.filter_by(token=token).first()
        if user is None or user.token_expiration < datetime.utcnow():
            return None
        return user


@login.user_loader 
def load_user(id):
    return User.query.get(int(id))
