#this is my user model

from flask_login import UserMixin
from extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, 
        primary_key=True)
    
    name = db.Column(db.String(100),
        nullable=False)
    
    email = db.Column(db.String(120),
        unique=True, 
        nullable=False)
    
    password_hash = db.Column(db.String(255),
        nullable=False)


    
    role = db.Column(db.String(20),
        nullable=False)
    
    contact = db.Column(db.String(15))

    status = db.Column(db.String(20), 
        default="Active")

    is_approved = db.Column(db.Boolean,
        default=False)

    is_blacklisted = db.Column(db.Boolean, 
        default=False)


    bookings = db.relationship("Booking", 
        back_populates="user")
