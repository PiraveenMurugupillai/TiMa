import datetime

from app import db, login
import base64
from datetime import timedelta
from flask_login import UserMixin
import os
from werkzeug.security import check_password_hash, generate_password_hash


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(128), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    company = db.Column(db.String(32))
    job = db.Column(db.String(32))
    target_time = db.Column(db.Float)
    token = db.Column(db.String(32), index=True, unique=True)
    token_expiration = db.Column(db.DateTime)
    working_hours = db.relationship('WorkingHours', backref='employee', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_token(self, expires_in=3600):
        now = datetime.datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token

    def revoke_token(self):
        self.token_expiration = datetime.datetime.utcnow() - timedelta(seconds=1)

    def check_token(token):
        user = User.query.filter_by(token=token).first()
        if user is None or user.token_expiration < datetime.datetime.utcnow():
            return None
        return user

    def __repr__(self):
        return f'<User {self.username}>'

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'company': self.company,
            'job': self.job,
            'target_time': self.target_time
        }


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class WorkingHours(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, index=True)
    working_hours = db.Column(db.Float)
    comment = db.Column(db.String(64))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<WorkingHours {self.user_id} {self.date}>'

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.strftime('%d.%m.%Y'),
            'working_hours': self.working_hours,
            'comment': self.comment or '',
            'user_id': self.user_id
        }
