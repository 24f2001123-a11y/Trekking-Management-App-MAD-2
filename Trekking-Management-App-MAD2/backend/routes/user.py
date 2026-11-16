# user dashboard fiel

from flask import Blueprint, jsonify, request, send_file
from flask_login import login_required, current_user
from routes.auth import role_required
from models.trek import Trek
from models.booking import Booking
from extensions import db

import json
import redis 
import extensions
from io import BytesIO

user_bp = Blueprint("user", __name__, url_prefix="/api/user")

# clear cached trek data
def clear_trek_cache():
    if extensions.redis_available:
        try:
            extensions.redis_client.delete("available_treks")

        except redis.RedisError:
            extensions.disable_redis()


# View available treks
@user_bp.route("/treks", methods=["GET"])
@login_required
@role_required("user")
def view_treks():

    # Check Redis only if it is available
    if extensions.redis_available:

        try:
            cached_treks = extensions.redis_client.get(
                "available_treks")

            if cached_treks:
                return jsonify(json.loads(cached_treks)), 200

        except redis.RedisError:
            extensions.disable_redis()

    # Get treks from SQLite
    treks = Trek.query.filter(
        Trek.status == "Open",
        Trek.available_slots > 0).order_by(Trek.start_date).all()

    trek_list = []

    for trek in treks:

        trek_data = {
            "id": trek.id,
            "trek_name": trek.trek_name,
            "location": trek.location,
            "difficulty": trek.difficulty,
            "duration": trek.duration,
            "available_slots": trek.available_slots,
            "start_date": trek.start_date.strftime("%Y-%m-%d"),
            "end_date": trek.end_date.strftime("%Y-%m-%d"),
            "status": trek.status}
        trek_list.append(trek_data)

    # Store data in Redis if available
    if extensions.redis_available:

        try:
            extensions.redis_client.setex(
                "available_treks",
                300,
                json.dumps(trek_list))

        except redis.RedisError:
            extensions.disable_redis()

    return jsonify(trek_list), 200



# Book a trek
@user_bp.route("/bookings", methods=["POST"])
@login_required
@role_required("user")
def book_trek():

    data = request.get_json()

    if not data or not data.get("trek_id"):
        return jsonify({
            "message": "Please select a trek"}), 400

    try:
        trek_id = int(data.get("trek_id"))
    except (ValueError, TypeError):
        return jsonify({
            "message": "Invalid trek ID"}), 400

    trek = Trek.query.get(trek_id)

    if not trek:
        return jsonify({
            "message": "Trek not found"}), 404

    if trek.status != "Open":
        return jsonify({
            "message": "This trek is not open for booking"}), 400

    # Check for an existing active booking
    existing_booking = Booking.query.filter_by(
        user_id=current_user.id,
        trek_id=trek_id,
        status="Booked").first()

    if existing_booking:
        return jsonify({
            "message": "You have already booked this trek"}), 400

    # Reduce one slot only if slots are still available
    updated_rows = Trek.query.filter(
        Trek.id == trek_id,
        Trek.status == "Open",
        Trek.available_slots > 0).update({Trek.available_slots: Trek.available_slots - 1},
        synchronize_session=False)

    if updated_rows == 0:
        db.session.rollback()

        return jsonify({
            "message": "No available slots for this trek"}), 400

    # Create the booking
    new_booking = Booking(
        user_id=current_user.id,
        trek_id=trek_id,
        status="Booked",
        payment_status="Not Required")

    db.session.add(new_booking)

    try:
        db.session.commit()
        db.session.refresh(trek)

    except Exception:
        db.session.rollback()

        return jsonify({
            "message": "Booking failed. Please try again"}), 500

    clear_trek_cache()

    return jsonify({
        "message": "Trek booked successfully",
        "booking_id": new_booking.id,
        "available_slots": trek.available_slots}), 201




# View user's booking history
@user_bp.route("/bookings", methods=["GET"])
@login_required
@role_required("user")
def view_my_bookings():

    bookings = Booking.query.filter_by(
        user_id=current_user.id).order_by(
        Booking.booking_date.desc()).all()

    booking_list = []

    for booking in bookings:

        booking_data = {
            "id": booking.id,
            "trek_name": booking.trek.trek_name,
            "location": booking.trek.location,
            "start_date": booking.trek.start_date.strftime("%Y-%m-%d"),
            "end_date": booking.trek.end_date.strftime("%Y-%m-%d"),
            "booking_date": booking.booking_date.strftime("%Y-%m-%d %H:%M"),
            "status": booking.status,
            "payment_status": booking.payment_status}
        booking_list.append(booking_data)

    return jsonify(booking_list), 200




# Cancel user's booking
@user_bp.route("/bookings/<int:booking_id>/cancel", methods=["PUT"])
@login_required
@role_required("user")
def cancel_booking(booking_id):

    booking = Booking.query.filter_by(
        id=booking_id,
        user_id=current_user.id).first()

    if not booking:
        return jsonify({
            "message": "Booking not found"}), 404

    if booking.status != "Booked":
        return jsonify({
            "message": "Only active bookings can be cancelled"}), 400

    # Cancel the booking
    booking.status = "Cancelled"

    # Restore one available slot
    booking.trek.available_slots += 1

    try:
        db.session.commit()

    except Exception:
        db.session.rollback()

        return jsonify({
            "message": "Could not cancel booking. Please try again"}), 500

    clear_trek_cache()

    return jsonify({
        "message": "Booking cancelled successfully"}), 200




# Update user profile
@user_bp.route("/profile", methods=["PUT"])
@login_required
@role_required("user")
def update_profile():

    data = request.get_json()

    if not data:
        return jsonify({
            "message": "Please enter your profile details"}), 400

    name = data.get("name", "").strip()
    contact = data.get("contact", "").strip()

    if not name:
        return jsonify({
            "message": "Name cannot be empty"}), 400

    if len(name) > 100:
        return jsonify({
            "message": "Name cannot exceed 100 characters"}), 400

    if len(contact) > 15:
        return jsonify({
            "message": "Contact number cannot exceed 15 characters"}), 400

    current_user.name = name
    current_user.contact = contact

    try:
        db.session.commit()

    except Exception:
        db.session.rollback()                       

        return jsonify({
            "message": "Profile update failed"}), 500

    return jsonify({
        "message": "Profile updated successfully",
        "user": {
            "name": current_user.name,
            "email": current_user.email,
            "contact": current_user.contact}}), 200



# Start CSV export task
@user_bp.route("/bookings/export", methods=["POST"])
@login_required
@role_required("user")
def start_booking_export():

    from celery_app import export_booking_history
    task = export_booking_history.delay(current_user.id)
    return jsonify({
        "message": "CSV export started",
        "task_id": task.id}), 202


# Download exported CSV file
@user_bp.route("/bookings/export/<task_id>", methods=["GET"])
@login_required
@role_required("user")
def download_booking_export(task_id):
    from celery_app import celery
    task = celery.AsyncResult(task_id)

    #check whether task is completed
    if not task.ready():
        return jsonify({
            "status": "Processing",
            "message": "CSV file is still being generated"}), 202
    #check whether task failed
    if task.failed():
        return jsonify({
            "message": "CSV export failed"}), 500

    export_data = task.result

    #check that the csb belongs to the logged-in user
    if not isinstance(export_data, dict):
        return jsonify({
            "message": "Invalid export result"}), 500
    if export_data.get("user_id") != current_user.id:
        return jsonify({
            "message": "You cannot download another user's export"}), 403

    csv_content = export_data.get("csv_content", "")

    return send_file(
        BytesIO(csv_content.encode("utf-8-sig")),
        mimetype="text/csv",
        as_attachment=True,
        download_name="booking_history.csv")