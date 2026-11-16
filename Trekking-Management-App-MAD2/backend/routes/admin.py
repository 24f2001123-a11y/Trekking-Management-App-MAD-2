#this is admin dashboard fiel



from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from datetime import datetime

from extensions import db, clear_trek_cache
from routes.auth import role_required
from models.user import User
from models.trek import Trek
from models.booking import Booking

from werkzeug.security import generate_password_hash

# Create admin blueprint
admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


# Admin dashboard API
@admin_bp.route("/dashboard", methods=["GET"])
@login_required
@role_required("admin")
def admin_dashboard():

    total_users = User.query.filter_by(role="user").count()
    total_staff = User.query.filter_by(role="staff").count()
    total_treks = Trek.query.count()
    total_bookings = Booking.query.count()

    return jsonify({
        "message": "Admin dashboard data",
        "total_users": total_users,
        "total_staff": total_staff,
        "total_treks": total_treks,
        "total_bookings": total_bookings})


# create a new TREK
@admin_bp.route("/treks", methods=["POST"])
@login_required
@role_required("admin")
def create_trek():

    data = request.get_json()

    trek_name = data.get("trek_name")
    location = data.get("location")
    difficulty = data.get("difficulty")
    duration = data.get("duration")
    available_slots = data.get("available_slots")
    start_date = data.get("start_date")
    end_date = data.get("end_date")

    # check required fields
    if not all([trek_name, location, difficulty, duration,
                available_slots, start_date, end_date]):
        return jsonify({"message": "Please fill all required fields"}), 400

    # check difficulty
    if difficulty not in ["Easy", "Moderate", "Hard"]:
        return jsonify({"message": "Invalid difficulty level"}), 400

    # validate numbers and dates
    try:
        duration = int(duration)
        available_slots = int(available_slots)

        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

    except (ValueError, TypeError):
        return jsonify({"message": "Please enter valid trek details"}), 400

    if duration <= 0 or available_slots <= 0:
        return jsonify({"message": "Duration and slots must be greater than zero"}), 400

    if end_date < start_date:
        return jsonify({"message": "End date cannot be before start date"}), 400

    # create trek object
    new_trek = Trek(
        trek_name=trek_name,
        location=location,
        difficulty=difficulty,
        duration=duration,
        available_slots=available_slots,
        start_date=start_date,
        end_date=end_date,
        status="Pending")

    db.session.add(new_trek)
    db.session.commit()
    clear_trek_cache()

    return jsonify({
        "message": "Trek created successfully",
        "trek_id": new_trek.id}), 201



# View all treks
@admin_bp.route("/treks", methods=["GET"])
@login_required
@role_required("admin")
def view_treks():

    treks = Trek.query.order_by(Trek.id.desc()).all()

    trek_list = []

    for trek in treks:

        trek_data = {
            "id": trek.id,
            "trek_name": trek.trek_name,
            "location": trek.location,
            "difficulty": trek.difficulty,
            "duration": trek.duration,
            "available_slots": trek.available_slots,
            "status": trek.status,
            "start_date": trek.start_date.strftime("%Y-%m-%d"),
            "end_date": trek.end_date.strftime("%Y-%m-%d"),
            "assigned_staff": (
                trek.assigned_staff.name
                if trek.assigned_staff
                else "Not Assigned"),}
        trek_list.append(trek_data)
    return jsonify(trek_list)



# Update an existing trek
@admin_bp.route("/treks/<int:trek_id>", methods=["PUT"])
@login_required
@role_required("admin")
def update_trek(trek_id):

    trek = Trek.query.get(trek_id)

    if not trek:
        return jsonify({"message": "Trek not found"}), 404

    data = request.get_json()

    trek_name = data.get("trek_name")
    location = data.get("location")
    difficulty = data.get("difficulty")
    duration = data.get("duration")
    available_slots = data.get("available_slots")
    start_date = data.get("start_date")
    end_date = data.get("end_date")

    if not all([
        trek_name, location, difficulty, duration,
        available_slots, start_date, end_date
    ]):
        return jsonify({"message": "Please fill all required fields"}), 400

    if difficulty not in ["Easy", "Moderate", "Hard"]:
        return jsonify({"message": "Invalid difficulty level"}), 400

    try:
        duration = int(duration)
        available_slots = int(available_slots)

        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

    except (ValueError, TypeError):
        return jsonify({"message": "Please enter valid trek details"}), 400

    if duration <= 0 or available_slots < 0:
        return jsonify({
            "message": "Duration must be greater than zero and slots cannot be negative"}), 400

    if end_date < start_date:
        return jsonify({
            "message": "End date cannot be before start date"}), 400

    trek_name = trek_name.strip()
    location = location.strip()

    if not trek_name or not location:
        return jsonify({
            "message": "Trek name and location are required"}), 400

    # Check existing bookings
    booked_slots = Booking.query.filter_by(
        trek_id=trek.id,
        status="Booked").count()

    if available_slots < booked_slots:
        return jsonify({
            "message": "Available slots cannot be less than existing bookings"}), 400

    # update trek details
    trek.trek_name = trek_name
    trek.location = location
    trek.difficulty = difficulty
    trek.duration = duration
    trek.available_slots = available_slots
    trek.start_date = start_date
    trek.end_date = end_date

    db.session.commit()
    clear_trek_cache()
    return jsonify({
        "message": "Trek updated successfully"}), 200


# delete a trek
@admin_bp.route("/treks/<int:trek_id>", methods=["DELETE"])
@login_required
@role_required("admin")
def delete_trek(trek_id):

    trek = Trek.query.get(trek_id)
    if not trek:
        return jsonify({"message": "Trek not found"}), 404

    # vhecking whether the trek has bookings
    existing_bookings = Booking.query.filter_by(
        trek_id=trek.id).count()

    if existing_bookings > 0:
        return jsonify({
            "message": "This trek cannot be deleted because it has booking history"}), 400

    db.session.delete(trek)
    db.session.commit()
    clear_trek_cache()
    return jsonify({
        "message": "Trek deleted successfully"}), 200



# view all users
@admin_bp.route("/users", methods=["GET"])
@login_required
@role_required("admin")
def view_users():

    users = User.query.filter_by(
        role="user").order_by(User.id.desc()).all()

    user_list = []

    for user in users:
        user_data = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "contact": user.contact,
            "status": user.status,
            "is_blacklisted": user.is_blacklisted}

        user_list.append(user_data)
    return jsonify(user_list)


# update user account status
@admin_bp.route("/users/<int:user_id>/status", methods=["PUT"])
@login_required
@role_required("admin")
def update_user_status(user_id):

    user = User.query.filter_by(
        id=user_id,
        role="user").first()

    if not user:
        return jsonify({
            "message": "User not found"}), 404

    data = request.get_json()
    status = data.get("status")

    if status not in ["Active", "Inactive"]:
        return jsonify({
            "message": "Invalid account status"}), 400

    user.status = status
    db.session.commit()
    return jsonify({
        "message": "User status updated successfully"}), 200


# Update user blacklist status
@admin_bp.route("/users/<int:user_id>/blacklist", methods=["PUT"])
@login_required
@role_required("admin")
def update_user_blacklist(user_id):

    user = User.query.filter_by(
        id=user_id,
        role="user").first()

    if not user:
        return jsonify({
            "message": "User not found"}), 404
    data = request.get_json()
    is_blacklisted = data.get("is_blacklisted")
    if not isinstance(is_blacklisted, bool):
        return jsonify({
            "message": "Invalid blacklist status"}), 400
    user.is_blacklisted = is_blacklisted
    db.session.commit()
    return jsonify({
        "message": "User blacklist status updated successfully"}), 200


# create a new STAFF account
@admin_bp.route("/staff", methods=["POST"])
@login_required
@role_required("admin")
def create_staff():

    data = request.get_json()

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    contact = data.get("contact")

    if not name or not email or not password:
        return jsonify({
            "message": "Please fill all required fields"}), 400

    name = name.strip()
    email = email.strip().lower()

    if not name or not email:
        return jsonify({
            "message": "Name and email are required"}), 400

    if len(password) < 8:
        return jsonify({
            "message": "Password must contain at least 8 characters"}), 400

    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        return jsonify({
            "message": "This email is already registered"}), 400

    new_staff = User(
        name=name,
        email=email,
        password_hash=generate_password_hash(password),
        role="staff",
        contact=contact,
        status="Active",
        is_approved=True,
        is_blacklisted=False)

    db.session.add(new_staff)
    db.session.commit()

    return jsonify({
        "message": "Staff account created successfully"}), 201


# VIEW all staff members
@admin_bp.route("/staff", methods=["GET"])
@login_required
@role_required("admin")
def view_staff():

    staff_members = User.query.filter_by(
        role="staff").order_by(User.id.desc()).all()

    staff_list = []

    for staff in staff_members:

        staff_data = {
            "id": staff.id,
            "name": staff.name,
            "email": staff.email,
            "contact": staff.contact,
            "status": staff.status,
            "is_blacklisted": staff.is_blacklisted}

        staff_list.append(staff_data)
    return jsonify(staff_list)


# Update staff account status
@admin_bp.route("/staff/<int:staff_id>/status", methods=["PUT"])
@login_required
@role_required("admin")
def update_staff_status(staff_id):

    staff = User.query.filter_by(
        id=staff_id,
        role="staff").first()

    if not staff:
        return jsonify({
            "message": "Staff member not found"}), 404

    data = request.get_json()

    status = data.get("status")

    if status not in ["Active", "Inactive"]:
        return jsonify({
            "message": "Invalid account status"}), 400

    staff.status = status
    db.session.commit()

    return jsonify({
        "message": "Staff status updated successfully"}), 200


# update staff blacklist status
@admin_bp.route("/staff/<int:staff_id>/blacklist", methods=["PUT"])
@login_required
@role_required("admin")
def update_staff_blacklist(staff_id):

    staff = User.query.filter_by(
        id=staff_id,
        role="staff").first()

    if not staff:
        return jsonify({
            "message": "Staff member not found"}), 404

    data = request.get_json()
    is_blacklisted = data.get("is_blacklisted")

    if not isinstance(is_blacklisted, bool):
        return jsonify({
            "message": "Invalid blacklist status"}), 400

    staff.is_blacklisted = is_blacklisted
    db.session.commit()
    return jsonify({
        "message": "Staff blacklist status updated successfully"}), 200


# assign staff to a trek
@admin_bp.route("/treks/<int:trek_id>/assign-staff", methods=["PUT"])
@login_required
@role_required("admin")
def assign_staff(trek_id):

    trek = Trek.query.get(trek_id)

    if not trek:
        return jsonify({
            "message": "Trek not found"}), 404

    data = request.get_json()
    staff_id = data.get("staff_id")

    if staff_id is None:
        return jsonify({
            "message": "Please select a staff member"}), 400

    try:
        staff_id = int(staff_id)
    except (ValueError, TypeError):
        return jsonify({
            "message": "Invalid staff member"}), 400

    staff = User.query.filter_by(
        id=staff_id,
        role="staff",
        status="Active",
        is_approved=True,
        is_blacklisted=False).first()

    if not staff:
        return jsonify({
            "message": "Selected staff member is not available"}), 400

    trek.assigned_staff_id = staff.id
    db.session.commit()
    return jsonify({
        "message": "Staff assigned successfully"}), 200


# reemove staff assignment from a trek
@admin_bp.route("/treks/<int:trek_id>/assign-staff", methods=["DELETE"])
@login_required
@role_required("admin")
def remove_staff_assignment(trek_id):

    trek = Trek.query.get(trek_id)

    if not trek:
        return jsonify({
            "message": "Trek not found"}), 404

    if not trek.assigned_staff_id:
        return jsonify({
            "message": "No staff member is assigned to this trek"}), 400

    trek.assigned_staff_id = None
    db.session.commit()
    return jsonify({
        "message": "Staff assignment removed successfully"}), 200


# view all bookings
@admin_bp.route("/bookings", methods=["GET"])
@login_required
@role_required("admin")
def view_bookings():

    bookings = Booking.query.order_by(
        Booking.booking_date.desc()).all()

    booking_list = []

    for booking in bookings:

        booking_data = {
            "id": booking.id,
            "user_id": booking.user_id,
            "user_name": booking.user.name,
            "user_email": booking.user.email,
            "trek_id": booking.trek_id,
            "trek_name": booking.trek.trek_name,
            "location": booking.trek.location,
            "start_date": booking.trek.start_date.strftime("%Y-%m-%d"),
            "end_date": booking.trek.end_date.strftime("%Y-%m-%d"),
            "booking_date": booking.booking_date.strftime("%Y-%m-%d %H:%M"),
            "status": booking.status,
            "payment_status": booking.payment_status}

        booking_list.append(booking_data)
    return jsonify(booking_list), 200


# cancel A booking
@admin_bp.route("/bookings/<int:booking_id>/cancel", methods=["PUT"])
@login_required
@role_required("admin")
def cancel_booking(booking_id):

    booking = Booking.query.get(booking_id)

    if not booking:
        return jsonify({"message": "Booking not found"}), 404
    if booking.status != "Booked":
        return jsonify({
            "message": "Only active bookings can be cancelled"}), 400

    booking.status = "Cancelled"

    db.session.commit()
    clear_trek_cache()
    return jsonify({
        "message": "Booking cancelled successfully"}), 200