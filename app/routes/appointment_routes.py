from flask import Blueprint, request, jsonify
from ..models.appointment import Appointment
from ..models.patient import Patient
from ..database import db
from ..utils import has_conflict

bp = Blueprint('appointments', __name__, url_prefix='/appointments')

@bp.route('/', methods=['POST'])
def create_appointment():
    data = request.json
    if has_conflict(data['doctor_id'], data['date']):
        return jsonify({"error": "Doctor is already booked at this time"}), 409
    price = float(data.get('price', 0))
    patient = db.session.get(Patient, data['patient_id'])
    if not patient:
        return jsonify({"error": "Paciente nao encontrado"}), 404
    if patient.has_insurance:
        price_paid = price * 0.5
    else:
        price_paid = price
    appointment = Appointment(
        patient_id=data['patient_id'],
        doctor_id=data['doctor_id'],
        date=data['date'],
        price=price_paid
    )
    db.session.add(appointment)
    db.session.commit()
    return jsonify({"id": appointment.id, "price_paid": price_paid}), 201

@bp.route('/<int:id>', methods=['DELETE'])
def cancel_appointment(id):
    ap = db.session.get(Appointment, id)
    if not ap:
        return jsonify({"error": "Consulta nao encontrada"}), 404
    db.session.delete(ap)
    db.session.commit()
    return jsonify({"message": "Consulta cancelada"}), 200

@bp.route('/<int:id>/cancel', methods=['DELETE'])
def cancel_appointment_alt(id):
    # Permite cancelar consulta via /appointments/<id>/cancel
    ap = db.session.get(Appointment, id)
    if not ap:
        return jsonify({"error": "Consulta nao encontrada"}), 404
    db.session.delete(ap)
    db.session.commit()
    return jsonify({"message": "Consulta cancelada"}), 200
