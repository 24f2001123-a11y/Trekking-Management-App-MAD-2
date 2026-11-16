#this is booking model

from datetime import datetime
from extensions import db


class Booking(db.Model):
    __tablename__ = "bookings"

    id = db.Column(db.Integer,
        primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False)

    trek_id = db.Column(
        db.Integer,
        db.ForeignKey("treks.id"),
        nullable=False)

    booking_date = db.Column(db.DateTime, 
        default=datetime.utcnow)

    status = db.Column(db.String(20), 
        default="Booked")

    payment_status = db.Column(db.String(20),
        default="Not Required")



    user = db.relationship("User", 
        back_populates="bookings")

    
    trek = db.relationship("Trek", 
        back_populates="bookings")
