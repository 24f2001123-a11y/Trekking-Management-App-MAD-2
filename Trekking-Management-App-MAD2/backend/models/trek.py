#this is trek model 


from extensions import db


class Trek(db.Model):
    __tablename__ = "treks"

    id = db.Column(
        db.Integer,
        primary_key=True)

    trek_name = db.Column(
        db.String(100),
        nullable=False)

    location = db.Column(
        db.String(100),
        nullable=False)

    difficulty = db.Column(
        db.String(50),
        nullable=False)

    duration = db.Column(
        db.Integer,
        nullable=False)

    available_slots = db.Column(
        db.Integer,
        default=0)

    status = db.Column(
        db.String(30),
        default="Pending")

    assigned_staff_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"))

    start_date = db.Column(
        db.Date,
        nullable=False)

    end_date = db.Column(
        db.Date,
        nullable=False)

    # relationship with staf
    assigned_staff = db.relationship("User",
        foreign_keys=[assigned_staff_id],
        backref="assigned_treks")


    # relationship with bookings
    bookings = db.relationship("Booking",
        back_populates="trek")
