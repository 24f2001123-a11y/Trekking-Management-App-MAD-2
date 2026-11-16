#THIS is staff file 

from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from routes.auth import role_required
from models.trek import Trek


from flask import request
from extensions import db

from models.booking import Booking

from datetime import date
from models.booking import Booking
from extensions import db, clear_trek_cache

# Create Staff Blueprint
staff_bp = Blueprint("staff", __name__, url_prefix="/api/staff")


# View treks assigned to logged-in staff
@staff_bp.route("/treks", methods=["GET"])
@login_required
@role_required("staff")
def view_assigned_treks():

    treks = Trek.query.filter_by(
        assigned_staff_id=current_user.id).all()

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
            "end_date": trek.end_date.strftime("%Y-%m-%d")}
        trek_list.append(trek_data)
    return jsonify(trek_list), 200

# Update trek availability and status
@staff_bp.route("/treks/<int:trek_id>", methods=["PUT"])
@login_required
@role_required("staff")
def update_trek(trek_id):

    trek = Trek.query.filter_by(
        id=trek_id,
        assigned_staff_id=current_user.id
    ).first()

    if not trek:
        return jsonify({
            "message": "Trek not found or not assigned to you"}), 404
    if trek.status == "Completed":
        return jsonify({
            "message": "Completed treks cannot be updated"}), 400

    data = request.get_json()
    available_slots = data.get("available_slots")
    status = data.get("status")

    try:
        available_slots = int(available_slots)
    except (ValueError, TypeError):
        return jsonify({
            "message": "Please enter a valid number of slots"}), 400

    if available_slots < 0:
        return jsonify({
            "message": "Available slots cannot be negative"}), 400

    if status not in ["Open", "Closed"]:
        return jsonify({
            "message": "Status must be Open or Closed"}), 400

    if status == "Open" and available_slots == 0:
        return jsonify({
            "message": "A trek with zero available slots cannot be opened"}), 400

    trek.available_slots = available_slots
    trek.status = status

    db.session.commit()
    clear_trek_cache()

    return jsonify({
        "message": "Trek updated successfully"}), 200


# View participants of an assigned trek
@staff_bp.route("/treks/<int:trek_id>/participants", methods=["GET"])
@login_required
@role_required("staff")
def view_participants(trek_id):

    # Check whether the trek is assigned to this staff member
    trek = Trek.query.filter_by(
        id=trek_id,
        assigned_staff_id=current_user.id).first()

    if not trek:
        return jsonify({
            "message": "Trek not found or not assigned to you"}), 404

    # Get active bookings for this trek
    bookings = Booking.query.filter(
        Booking.trek_id == trek_id,
        Booking.status.in_(["Booked", "Completed"])).all()

    participant_list = []

    for booking in bookings:

        participant_data = {
            "booking_id": booking.id,
            "user_id": booking.user.id,
            "name": booking.user.name,
            "email": booking.user.email,
            "contact": booking.user.contact,
            "booking_date": booking.booking_date.strftime("%Y-%m-%d %H:%M"),
            "status": booking.status}
        participant_list.append(participant_data)

    return jsonify({
        "trek_name": trek.trek_name,
        "participants": participant_list}), 200



# Mark an assigned trek as completed
@staff_bp.route("/treks/<int:trek_id>/complete", methods=["PUT"])
@login_required
@role_required("staff")
def complete_trek(trek_id):

    # Find the trek assigned to the logged-in staff member
    trek = Trek.query.filter_by(
        id=trek_id,
        assigned_staff_id=current_user.id).first()

    if not trek:
        return jsonify({
            "message": "Trek not found or not assigned to you"}), 404

    # Check whether the trek is already completed
    if trek.status == "Completed":
        return jsonify({
            "message": "This trek is already completed"}), 400

    # Check whether the trek end date has passed
    if trek.end_date > date.today():
        return jsonify({
            "message": "This trek cannot be completed before its end date"}), 400
    # Update trek status
    trek.status = "Completed"

    # Update active bookings
    bookings = Booking.query.filter_by(
        trek_id=trek_id,
        status="Booked").all()

    for booking in bookings:
        booking.status = "Completed"

    db.session.commit()
    clear_trek_cache()
    return jsonify({
        "message": "Trek marked as completed successfully"}), 200