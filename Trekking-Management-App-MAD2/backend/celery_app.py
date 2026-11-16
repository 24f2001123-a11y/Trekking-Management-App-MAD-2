
from celery import Celery
from app import app

from models import Trek, Booking

import csv
import io

from sqlalchemy import func

# Create Celery object
celery = Celery(
    app.import_name,
    broker=app.config["CELERY_BROKER_URL"],
    backend=app.config["CELERY_RESULT_BACKEND"]
)


# Connect Celery tasks with Flask application context
class FlaskTask(celery.Task):

    def __call__(self, *args, **kwargs):

        with app.app_context():
            return self.run(*args, **kwargs)


celery.Task = FlaskTask

# Export user's booking history as CSV
@celery.task
def export_booking_history(user_id):

    output = io.StringIO()

    writer = csv.writer(output)

    # CSV column headings
    writer.writerow([
        "User ID",
        "Trek Name",
        "Location",
        "Booking Status",
        "Dates"
    ])

    # Get bookings of the selected user
    bookings = Booking.query.join(Trek).filter(
        Booking.user_id == user_id
    ).order_by(Booking.booking_date.desc()).all()

    # Add booking details to CSV
    for booking in bookings:

        dates = (
            str(booking.trek.start_date)
            + " to "
            + str(booking.trek.end_date)
        )

        writer.writerow([
            user_id,
            booking.trek.trek_name,
            booking.trek.location,
            booking.status,
            dates
        ])

    return {
        "user_id": user_id,
        "csv_content": output.getvalue()
    }