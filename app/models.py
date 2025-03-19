from app import db
from datetime import datetime
from flask_login import UserMixin

# User Table
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    searches = db.relationship('SearchHistory', backref='user', lazy=True)
    allergies = db.relationship('Allergy', backref='user', lazy=True)

# Search History Table
class SearchHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    query = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Allergy Table
class Allergy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    drug_name = db.Column(db.String(100), nullable=False)
    reaction = db.Column(db.String(200))