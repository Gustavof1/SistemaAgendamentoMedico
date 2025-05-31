from flask import Blueprint, request, jsonify
from ..models.appointment import Appointment
from ..database import db
from ..utils import has_conflict

bp = Blueprint('appointments', __name__, url_prefix='/appointments')

@bp.route('/', methods=['POST'])
def create_appointment():
    data = request.json
    if has_conflict(data['doctor_id'], data['date']):
        return jsonify({"error": "Doctor is already booked at this time"}), 409
    appointment = Appointment(
        patient_id=data['patient_id'],
        doctor_id=data['doctor_id'],
        date=data['date']
    )
    db.session.add(appointment)
    db.session.commit()
    return jsonify({"id": appointment.id}), 201
