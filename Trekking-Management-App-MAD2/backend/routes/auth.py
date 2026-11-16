# this is authenticstion pfile


from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from flask_login import login_user, logout_user, current_user 
from functools import wraps


from extensions import db
from models.user import User



# Check whether user has permission to access an API
def role_required(*allowed_roles):
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            # Check whether user is logged in
            if not current_user.is_authenticated:
                return jsonify({
                    "message": "Please login first"}), 401
            # Check account status
            if current_user.status != "Active" or current_user.is_blacklisted:
                return jsonify({
                    "message": "Your account is inactive or blocked"}), 403
            # Check account approval
            if not current_user.is_approved:
                return jsonify({
                    "message": "Your account is waiting for approval"}), 403
            # Check user role
            if current_user.role not in allowed_roles:
                return jsonify({
                    "message": "You do not have permission to access this page"}), 403
            return function(*args, **kwargs)
        return wrapper
    return decorator


# Create authentication blueprint
auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


# User registration API
@auth_bp.route("/register", methods=["POST"])
def register():

    # Get data sent by VueJS
    data = request.get_json()

    if not data:
        return jsonify({"message": "Invalid request data"}), 400

    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    contact = data.get("contact", "").strip()

    # Check required fields
    if not name or not email or not password:
        return jsonify({
            "message": "Name, email and password are required"}), 400

    # Check email format
    if "@" not in email or "." not in email:
        return jsonify({
            "message": "Please enter a valid email address"}), 400

    # Check password length
    if len(password) < 8:
        return jsonify({
            "message": "Password must contain at least 8 characters"}), 400

    # Check whether email already exists
    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        return jsonify({
            "message": "Email is already registered"}), 409

    # Create new trekker account
    hashed_password = generate_password_hash(password)

    new_user = User(
        name=name,
        email=email,
        password_hash=hashed_password,
        role="user",
        contact=contact,
        status="Active",
        is_approved=True,
        is_blacklisted=False)

    # save user in database
    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "message": "Registration successful",
        "user": {
            "id": new_user.id,
            "name": new_user.name,
            "email": new_user.email,
            "role": new_user.role}}), 201





#this is login route

@auth_bp.route("/login", methods=["POST"])
def login():
    # Get login details from VueJS
    data = request.get_json()

    if not data:
        return jsonify({"message": "Invalid request data"}), 400

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    # Check required fields
    if not email or not password:
        return jsonify({
            "message": "Email and password are required"}), 400

    # Find user using email
    user = User.query.filter_by(email=email).first()

    # Check whether user exists and password is correct
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({
            "message": "Invalid email or password"}), 401

    # Check account status
    if user.status != "Active" or user.is_blacklisted:
        return jsonify({
            "message": "Your account is inactive or blocked"}), 403

    # Check account approval
    if not user.is_approved:
        return jsonify({
            "message": "Your account is waiting for admin approval"}), 403

    # Create login session
    login_user(user)

    return jsonify({
        "message": "Login successful",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role}}), 200



#this is logout route

# User logout API
@auth_bp.route("/logout", methods=["POST"])
def logout():
    if not current_user.is_authenticated:
        return jsonify({
            "message": "You are not logged in"}), 401

    logout_user()

    return jsonify({
        "message": "Logout successful"}), 200


# Check currently logged-in user
@auth_bp.route("/me", methods=["GET"])
def get_current_user():

    if not current_user.is_authenticated:
        return jsonify({
            "logged_in": False,
            "message": "User is not logged in"
        }), 401

    return jsonify({
        "logged_in": True,
        "user": {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "role": current_user.role}}), 200
