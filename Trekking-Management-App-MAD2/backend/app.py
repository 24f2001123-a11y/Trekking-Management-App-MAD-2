#this is main app filr



import os

from flask import Flask, jsonify, render_template
from config import Config
from extensions import db, login_manager

from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.staff import staff_bp
from routes.user import user_bp

# Import database models
from models import User, Trek, Booking

from werkzeug.security import generate_password_hash


app = Flask(__name__,
    template_folder="../frontend/templates",
    static_folder="../frontend/static")

# Load application configuration
app.config.from_object(Config)

# create instance folder if it does not exist
os.makedirs(app.instance_path, exist_ok=True)

# connect database with Flask
db.init_app(app)

# connect Flask-Login with the application
login_manager.init_app(app)

# registering routes
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(staff_bp)
app.register_blueprint(user_bp)



# load logged-in user from the database
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/test")
def test_api():
    response = {
        "project": "TrekkingMate",
        "message": "Flask API is working",
        "status": "success"}
    return jsonify(response)


# create database tables
#creating admin
with app.app_context():
    db.create_all()
    print("Admin email:", app.config["ADMIN_EMAIL"])
    print("Database tables created successfully!")

    # Check whether admin already exists
    admin = User.query.filter_by(
        email=app.config["ADMIN_EMAIL"]).first()

    # Create admin if it does not exist
    if not admin:
        admin = User(
            name="Admin",
            email=app.config["ADMIN_EMAIL"],
            password_hash=generate_password_hash(
                app.config["ADMIN_PASSWORD"]
            ),
            role="admin",
            contact="",
            status="Active",
            is_approved=True,
            is_blacklisted=False)

        db.session.add(admin)
        db.session.commit()

        print("Admin account created successfully!")

    else:
        print("Admin account already exists!")



if __name__ == "__main__":
    app.run(debug=True)

