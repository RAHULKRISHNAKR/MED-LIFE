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
    medications = db.relationship('UserMedication', backref='user', lazy=True)
    diseases = db.relationship('UserDisease', backref='user', lazy=True)

# Search History Table
class SearchHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    search_query = db.Column(db.String(200), nullable=False)  # Renamed from "query"
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Allergy Table
class Allergy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    drug_name = db.Column(db.String(100), nullable=False)
    reaction = db.Column(db.String(200))

# User Medication Table
class UserMedication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    medication_name = db.Column(db.String(100), nullable=False)
    dosage = db.Column(db.String(50))
    frequency = db.Column(db.String(50))
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)
    active = db.Column(db.Boolean, default=True)

# User Disease Table
class UserDisease(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    disease_name = db.Column(db.String(100), nullable=False)
    diagnosed_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default="Active")  # Active, In Remission, Resolved
    notes = db.Column(db.Text)