
#this is my configurtion file

import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "trekkingmate-secret-key"
    SQLALCHEMY_DATABASE_URI = "sqlite:///trekkingmate.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # creating admin here 
    ADMIN_EMAIL = "admin@trekkingmate.com"
    ADMIN_PASSWORD = "admin123"

    # celery configuration port and database
    CELERY_BROKER_URL = "redis://127.0.0.1:6379/0"
    CELERY_RESULT_BACKEND = "redis://127.0.0.1:6379/0"

