from .models.appointment import Appointment
from .database import db
from datetime import datetime, timedelta

def has_conflict(doctor_id, date):
    # date: string "YYYY-MM-DD HH:MM"
    dt = datetime.strptime(date, "%Y-%m-%d %H:%M")
    dt_start = dt
    dt_end = dt + timedelta(minutes=30)
    appointments = db.session.query(Appointment).filter_by(doctor_id=doctor_id).all()
    for ap in appointments:
        ap_dt = datetime.strptime(ap.date, "%Y-%m-%d %H:%M")
        ap_start = ap_dt
        ap_end = ap_dt + timedelta(minutes=30)
        # Se houver sobreposição de intervalos
        if (dt_start < ap_end and dt_end > ap_start):
            return True
    return False
