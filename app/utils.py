from .models.appointment import Appointment
from .database import db

def has_conflict(doctor_id, date):
    return db.session.query(Appointment).filter_by(doctor_id=doctor_id, date=date).first() is not None
