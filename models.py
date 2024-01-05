from .extensions import db
from flask_login import UserMixin

def get_main_storage_data():
    # Hypothetical function to retrieve data from the database
    data = Storage.query.all()  # This is just an example query
    return data

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

class Storage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    integers = db.Column(db.PickleType, nullable=False, default=list)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
