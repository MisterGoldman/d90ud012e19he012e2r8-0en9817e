# models.py

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import URLSafeTimedSerializer
import os
from datetime import datetime

db = SQLAlchemy()

secret_key = os.urandom(24)
ts = URLSafeTimedSerializer(secret_key)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
	role = db.Column(db.String(100), default="user")
    active_until = db.Column(db.DateTime, default=datetime.utcnow)
    session_token = db.Column(db.String(100), unique=True)

    def get_id(self):
        return ts.dumps(self.id)

class UserSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    session_token = db.Column(db.String(255), unique=True, nullable=False)
    ip_address = db.Column(db.String(45), nullable=False)
    user_agent = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='user_sessions')



    
